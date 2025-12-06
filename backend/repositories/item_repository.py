from typing import List, Dict, Optional
from datetime import datetime, timezone


class ItemRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create_item(self, job_uuid: str, item_type: str, content: str, wage: Optional[float] = None):
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO processing_items (job_id, item_type, content, wage, status)
                VALUES (
                    (SELECT id FROM processing_jobs WHERE job_uuid = %s),
                    %s, %s, %s, 'pending'
                )
                """,
                (job_uuid, item_type, content, wage)
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def get_items_by_job_uuid(self, job_uuid: str) -> List[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT id, item_type, content, wage, status, processed_content, error_message
                FROM processing_items
                WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = %s)
                ORDER BY id
                """,
                (job_uuid,)
            )
            rows = cur.fetchall()
            return [
                {
                    'id': row[0],
                    'type': row[1],
                    'content': row[2],
                    'wage': float(row[3]) if row[3] else None,
                    'status': row[4],
                    'processed_content': row[5],
                    'error_message': row[6]
                }
                for row in rows
            ]
        finally:
            cur.close()

    def update_item_status(self, item_id: int, status: str,
                          processed_content: Optional[str] = None,
                          error_message: Optional[str] = None):
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

