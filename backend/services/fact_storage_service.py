"""Fact storage and validation service."""
import json
from typing import List, Dict, Optional


class FactStorageService:
    """Handles fact storage and validation."""

    def __init__(self, db_connection):
        self.conn = db_connection

    def store_extracted_fact(self, job_uuid: str, step_id: int, fact: str,
                            source_type: str, source_content: str,
                            item_id: int = None, wage: float = None,
                            confidence: float = 0.5, language: str = 'en',
                            metadata: Optional[Dict] = None) -> int:
        """Store an extracted fact."""
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO extracted_facts
                (job_id, step_id, item_id, fact, wage, source_type, source_content, confidence, language, metadata)
                VALUES (
                    (SELECT id FROM processing_jobs WHERE job_uuid = %s),
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
                """,
                (job_uuid, step_id, item_id, fact, wage, source_type, source_content[:1000],
                 confidence, language, json.dumps(metadata) if metadata else None)
            )
            fact_id = cur.fetchone()[0]
            self.conn.commit()
            return fact_id
        finally:
            cur.close()

    def validate_and_store_fact(self, fact_id: int, embedding: Optional[List[float]] = None):
        """Validate a fact and store it in the vector database."""
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                UPDATE extracted_facts
                SET is_validated = TRUE
                WHERE id = %s
                RETURNING fact, language
                """,
                (fact_id,)
            )
            result = cur.fetchone()

            if result:
                fact, language = result

                if embedding:
                    cur.execute(
                        "INSERT INTO facts (fact, language, embedding) VALUES (%s, %s, %s)",
                        (fact, language, embedding)
                    )
                else:
                    cur.execute(
                        "INSERT INTO facts (fact, language) VALUES (%s, %s)",
                        (fact, language)
                    )

                self.conn.commit()
        finally:
            cur.close()

    def get_extracted_facts(self, job_uuid: str, validated_only: bool = False) -> List[Dict]:
        """Get extracted facts for a job."""
        cur = self.conn.cursor()
        try:
            query = """
                SELECT id, fact, item_id, wage, source_type, confidence, is_validated, language,
                       metadata, created_at
                FROM extracted_facts
                WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = %s)
            """

            if validated_only:
                query += " AND is_validated = TRUE"

            query += " ORDER BY created_at DESC"

            cur.execute(query, (job_uuid,))
            rows = cur.fetchall()

            return [
                {
                    'id': row[0],
                    'fact': row[1],
                    'item_id': row[2],
                    'wage': float(row[3]) if row[3] else None,
                    'source_type': row[4],
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

