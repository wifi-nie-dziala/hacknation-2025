from typing import List, Dict


class FactRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def get_facts_by_job_uuid(self, job_uuid: str) -> List[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT id, fact, item_id, wage, source_type, source_content, confidence, 
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
                    'item_id': row[2],
                    'wage': float(row[3]) if row[3] else None,
                    'source_type': row[4],
                    'source_content': row[5],
                    'confidence': float(row[6]) if row[6] else None,
                    'is_validated': row[7],
                    'language': row[8],
                    'metadata': row[9],
                    'created_at': row[10].isoformat() if row[10] else None
                }
                for row in rows
            ]
        finally:
            cur.close()

