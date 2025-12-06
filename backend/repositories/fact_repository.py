from typing import List, Dict


class FactRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def get_facts_by_job_uuid(self, job_uuid: str) -> List[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT id, fact, step_id, source_type, source_content, confidence, 
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
                    'step_id': row[2],
                    'source_type': row[3],
                    'source_content': row[4],
                    'confidence': float(row[5]) if row[5] else None,
                    'is_validated': row[6],
                    'language': row[7],
                    'metadata': row[8],
                    'created_at': row[9].isoformat() if row[9] else None
                }
                for row in rows
            ]
        finally:
            cur.close()

