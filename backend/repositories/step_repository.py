from typing import List, Dict, Optional


class StepRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def get_steps_by_job_uuid(self, job_uuid: str) -> List[Dict]:
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

