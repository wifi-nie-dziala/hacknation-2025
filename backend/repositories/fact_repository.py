from typing import List, Dict


class FactRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def get_facts_by_job_uuid(self, job_uuid: str) -> List[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT id, fact, source_type, source_content, confidence, 
                       is_validated, language, metadata, created_at
                FROM extracted_facts
                WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = %s)
                ORDER BY created_at
                """,
                (job_uuid,)
            )
            rows = cur.fetchall()
            return [
                {
                    'id': row[0],
                    'fact': row[1],
                    'source_type': row[2],
                    'source_content': row[3],
                    'confidence': float(row[4]) if row[4] else None,
                    'is_validated': row[5],
                    'language': row[6],
                    'metadata': row[7],
                    'created_at': row[8].isoformat() if row[8] else None
                }
                for row in rows
            ]
        finally:
            cur.close()

