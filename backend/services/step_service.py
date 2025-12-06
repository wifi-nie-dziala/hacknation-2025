"""Processing step management service."""
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional


class StepService:
    """Handles processing step CRUD operations."""

    STEP_TYPES = ['scraping', 'extraction', 'reasoning', 'validation', 'embedding']
    STEP_STATUSES = ['pending', 'processing', 'completed', 'failed', 'skipped']

    def __init__(self, db_connection):
        self.conn = db_connection

    def create_step(self, job_uuid: str, step_number: int, step_type: str,
                   input_data: Dict, metadata: Optional[Dict] = None) -> int:
        """Create a new processing step."""
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO processing_steps (job_id, step_number, step_type, status, input_data, metadata)
                VALUES (
                    (SELECT id FROM processing_jobs WHERE job_uuid = %s),
                    %s, %s, 'pending', %s, %s
                )
                RETURNING id
                """,
                (job_uuid, step_number, step_type, json.dumps(input_data),
                 json.dumps(metadata) if metadata else None)
            )
            step_id = cur.fetchone()[0]
            self.conn.commit()
            return step_id
        finally:
            cur.close()

    def update_step(self, step_id: int, status: str, output_data: Optional[Dict] = None,
                   error_message: Optional[str] = None):
        """Update step status and output."""
        cur = self.conn.cursor()
        try:
            completed_at = datetime.now(timezone.utc) if status in ['completed', 'failed', 'skipped'] else None
            cur.execute(
                """
                UPDATE processing_steps
                SET status = %s, output_data = %s, error_message = %s,
                    updated_at = %s, completed_at = %s
                WHERE id = %s
                """,
                (status, json.dumps(output_data) if output_data else None,
                 error_message, datetime.now(timezone.utc), completed_at, step_id)
            )
            self.conn.commit()
        finally:
            cur.close()

    def get_job_steps(self, job_uuid: str) -> List[Dict]:
        """Get all steps for a job."""
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT id, step_number, step_type, status, input_data, output_data,
                       error_message, metadata, created_at, completed_at
                FROM processing_steps
                WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = %s)
                ORDER BY step_number
                """,
                (job_uuid,)
            )
            rows = cur.fetchall()
            return [
                {
                    'id': row[0],
                    'step_number': row[1],
                    'step_type': row[2],
                    'status': row[3],
                    'input_data': row[4],
                    'output_data': row[5],
                    'error_message': row[6],
                    'metadata': row[7],
                    'created_at': row[8].isoformat() if row[8] else None,
                    'completed_at': row[9].isoformat() if row[9] else None
                }
                for row in rows
            ]
        finally:
            cur.close()

