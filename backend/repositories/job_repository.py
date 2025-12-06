from typing import List, Dict, Optional
from datetime import datetime, timezone


class JobRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create_job(self) -> str:
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO processing_jobs (status) VALUES ('pending') RETURNING job_uuid"
            )
            job_uuid = cur.fetchone()[0]
            self.conn.commit()
            return str(job_uuid)
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cur.close()

    def get_job_by_uuid(self, job_uuid: str) -> Optional[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT job_uuid, status, created_at, updated_at, completed_at, error_message
                FROM processing_jobs
                WHERE job_uuid = %s
                """,
                (job_uuid,)
            )
            row = cur.fetchone()
            if not row:
                return None

            return {
                'job_uuid': str(row[0]),
                'status': row[1],
                'created_at': row[2].isoformat() if row[2] else None,
                'updated_at': row[3].isoformat() if row[3] else None,
                'completed_at': row[4].isoformat() if row[4] else None,
                'error_message': row[5]
            }
        finally:
            cur.close()

    def get_all_jobs(self, limit: int = 100) -> List[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT job_uuid, status, created_at, updated_at, completed_at, error_message
                FROM processing_jobs
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,)
            )
            rows = cur.fetchall()
            return [
                {
                    'job_uuid': str(row[0]),
                    'status': row[1],
                    'created_at': row[2].isoformat() if row[2] else None,
                    'updated_at': row[3].isoformat() if row[3] else None,
                    'completed_at': row[4].isoformat() if row[4] else None,
                    'error_message': row[5]
                }
                for row in rows
            ]
        finally:
            cur.close()

    def update_job_status(self, job_uuid: str, status: str, error_message: Optional[str] = None):
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

