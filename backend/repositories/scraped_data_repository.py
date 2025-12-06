from typing import List, Dict


class ScrapedDataRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def get_scraped_data_by_job_uuid(self, job_uuid: str) -> List[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT id, url, content, content_type, status, error_message, metadata, created_at
                FROM scraped_data
                WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = %s)
                ORDER BY created_at
                """,
                (job_uuid,)
            )
            rows = cur.fetchall()
            return [
                {
                    'id': row[0],
                    'url': row[1],
                    'content': row[2],
                    'content_type': row[3],
                    'status': row[4],
                    'error_message': row[5],
                    'metadata': row[6],
                    'created_at': row[7].isoformat() if row[7] else None
                }
                for row in rows
            ]
        finally:
            cur.close()

