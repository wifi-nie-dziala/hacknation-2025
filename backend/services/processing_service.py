"""Processing service for handling document/content processing jobs."""
import base64
from datetime import datetime, timezone
from typing import List, Dict, Optional


class ProcessingService:
    """Service for managing processing jobs and items."""

    VALID_TYPES = ['text', 'file', 'link']
    VALID_STATUSES = ['pending', 'processing', 'completed', 'failed']

    def __init__(self, db_connection):
        """Initialize the processing service with a database connection.

        Args:
            db_connection: PostgreSQL database connection
        """
        self.conn = db_connection

    def create_job(self, items: List[Dict]) -> str:
        """Create a new processing job with items.

        Args:
            items: List of dictionaries containing 'type', 'content', and 'wage'

        Returns:
            UUID of the created job

        Raises:
            ValueError: If items are invalid
        """
        if not items:
            raise ValueError("Items list cannot be empty")

        # Validate items
        for item in items:
            self._validate_item(item)

        cur = self.conn.cursor()
        try:
            # Create the job
            cur.execute(
                """
                INSERT INTO processing_jobs (status)
                VALUES ('pending')
                RETURNING job_uuid
                """
            )
            job_uuid = cur.fetchone()[0]

            # Create items for the job
            for item in items:
                cur.execute(
                    """
                    INSERT INTO processing_items (job_id, item_type, content, wage, status)
                    VALUES (
                        (SELECT id FROM processing_jobs WHERE job_uuid = %s),
                        %s, %s, %s, 'pending'
                    )
                    """,
                    (job_uuid, item['type'], item['content'], item.get('wage'))
                )

            self.conn.commit()
            return str(job_uuid)

        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def get_job_status(self, job_uuid: str) -> Optional[Dict]:
        """Get the status of a processing job.

        Args:
            job_uuid: UUID of the job

        Returns:
            Dictionary containing job status and items, or None if not found
        """
        cur = self.conn.cursor()
        try:
            # Get job details
            cur.execute(
                """
                SELECT job_uuid, status, created_at, updated_at, completed_at, error_message
                FROM processing_jobs
                WHERE job_uuid = %s
                """,
                (job_uuid,)
            )

            job_row = cur.fetchone()
            if not job_row:
                return None

            # Get items for the job
            cur.execute(
                """
                SELECT id, item_type, content, wage, status, processed_content, error_message
                FROM processing_items
                WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = %s)
                ORDER BY id
                """,
                (job_uuid,)
            )

            items_rows = cur.fetchall()

            items = [
                {
                    'id': row[0],
                    'type': row[1],
                    'content': row[2],
                    'wage': float(row[3]) if row[3] else None,
                    'status': row[4],
                    'processed_content': row[5],
                    'error_message': row[6]
                }
                for row in items_rows
            ]

            return {
                'job_uuid': str(job_row[0]),
                'status': job_row[1],
                'created_at': job_row[2].isoformat() if job_row[2] else None,
                'updated_at': job_row[3].isoformat() if job_row[3] else None,
                'completed_at': job_row[4].isoformat() if job_row[4] else None,
                'error_message': job_row[5],
                'items': items,
                'total_items': len(items),
                'completed_items': sum(1 for item in items if item['status'] == 'completed'),
                'failed_items': sum(1 for item in items if item['status'] == 'failed')
            }

        finally:
            cur.close()

    def update_job_status(self, job_uuid: str, status: str, error_message: Optional[str] = None):
        """Update the status of a job.

        Args:
            job_uuid: UUID of the job
            status: New status
            error_message: Optional error message
        """
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        cur = self.conn.cursor()
        try:
            completed_at = datetime.now(timezone.utc) if status in ['completed', 'failed'] else None

            cur.execute(
                """
                UPDATE processing_jobs
                SET status = %s, updated_at = %s, completed_at = %s, error_message = %s
                WHERE job_uuid = %s
                """,
                (status, datetime.now(timezone.utc), completed_at, error_message, job_uuid)
            )

            self.conn.commit()
        finally:
            cur.close()

    def update_item_status(self, item_id: int, status: str,
                          processed_content: Optional[str] = None,
                          error_message: Optional[str] = None):
        """Update the status of a processing item.

        Args:
            item_id: ID of the item
            status: New status
            processed_content: Optional processed content
            error_message: Optional error message
        """
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                UPDATE processing_items
                SET status = %s, updated_at = %s, processed_content = %s, error_message = %s
                WHERE id = %s
                """,
                (status, datetime.now(timezone.utc), processed_content, error_message, item_id)
            )

            self.conn.commit()
        finally:
            cur.close()

    def _validate_item(self, item: Dict):
        """Validate a processing item.

        Args:
            item: Dictionary containing item data

        Raises:
            ValueError: If item is invalid
        """
        if 'type' not in item:
            raise ValueError("Item must have 'type' field")

        if item['type'] not in self.VALID_TYPES:
            raise ValueError(f"Invalid type: {item['type']}. Must be one of {self.VALID_TYPES}")

        if 'content' not in item:
            raise ValueError("Item must have 'content' field")

        if not item['content']:
            raise ValueError("Item content cannot be empty")

        # Validate base64 encoding for file type
        if item['type'] == 'file':
            try:
                # Try to decode the base64 content to validate it
                base64.b64decode(item['content'], validate=True)
            except Exception as e:
                raise ValueError(f"File content must be valid base64 encoded string: {str(e)}")

        # Validate URL format for link type
        if item['type'] == 'link':
            content = item['content'].strip()
            if not (content.startswith('http://') or content.startswith('https://')):
                raise ValueError("Link content must be a valid URL starting with http:// or https://")

        if 'wage' in item and item['wage'] is not None:
            try:
                float(item['wage'])
            except (ValueError, TypeError):
                raise ValueError("Wage must be a valid number")

