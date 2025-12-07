from typing import List, Dict, Optional
import psycopg2.extras


class NodeRepository:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create_node(self, node_type: str, value: str, job_uuid: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        cur = self.conn.cursor()
        try:
            metadata_json = psycopg2.extras.Json(metadata) if metadata else None
            if job_uuid:
                cur.execute(
                    """
                    INSERT INTO nodes (type, value, job_id, metadata)
                    VALUES (%s, %s, (SELECT id FROM processing_jobs WHERE job_uuid = %s), %s)
                    RETURNING id
                    """,
                    (node_type, value, job_uuid, metadata_json)
                )
            else:
                cur.execute(
                    """
                    INSERT INTO nodes (type, value, metadata)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (node_type, value, metadata_json)
                )
            node_id = cur.fetchone()[0]
            self.conn.commit()
            return str(node_id)
        finally:
            cur.close()

    def get_node(self, node_id: str) -> Optional[Dict]:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                SELECT id, type, value, job_id, metadata, created_at, updated_at
                FROM nodes
                WHERE id = %s
                """,
                (node_id,)
            )
            row = cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'type': row[1],
                    'value': row[2],
                    'job_id': row[3],
                    'metadata': row[4],
                    'created_at': row[5].isoformat() if row[5] else None,
                    'updated_at': row[6].isoformat() if row[6] else None
                }
            return None
        finally:
            cur.close()

    def get_nodes_by_job(self, job_uuid: str, node_type: Optional[str] = None) -> List[Dict]:
        cur = self.conn.cursor()
        try:
            if node_type:
                cur.execute(
                    """
                    SELECT id, type, value, job_id, metadata, created_at, updated_at
                    FROM nodes
                    WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = %s)
                    AND type = %s
                    ORDER BY created_at
                    """,
                    (job_uuid, node_type)
                )
            else:
                cur.execute(
                    """
                    SELECT id, type, value, job_id, metadata, created_at, updated_at
                    FROM nodes
                    WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = %s)
                    ORDER BY created_at
                    """,
                    (job_uuid,)
                )
            rows = cur.fetchall()
            return [
                {
                    'id': row[0],
                    'type': row[1],
                    'value': row[2],
                    'job_id': row[3],
                    'metadata': row[4],
                    'created_at': row[5].isoformat() if row[5] else None,
                    'updated_at': row[6].isoformat() if row[6] else None
                }
                for row in rows
            ]
        finally:
            cur.close()

    def create_relation(self, source_node_id: str, target_node_id: str,
                       relation_type: str, confidence: float = 1.0, metadata: Optional[Dict] = None) -> str:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO node_relations (source_node_id, target_node_id, relation_type, confidence, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (source_node_id, target_node_id, relation_type, confidence, metadata)
            )
            relation_id = cur.fetchone()[0]
            self.conn.commit()
            return relation_id
        finally:
            cur.close()

    def get_node_relations(self, node_id: str, direction: str = 'both') -> List[Dict]:
        cur = self.conn.cursor()
        try:
            if direction == 'outgoing':
                query = """
                    SELECT nr.id, nr.source_node_id, nr.target_node_id, nr.relation_type, 
                           nr.confidence, nr.metadata, nr.created_at,
                           n.type as target_type, n.value as target_value
                    FROM node_relations nr
                    JOIN nodes n ON nr.target_node_id = n.id
                    WHERE nr.source_node_id = %s
                    ORDER BY nr.created_at
                """
            elif direction == 'incoming':
                query = """
                    SELECT nr.id, nr.source_node_id, nr.target_node_id, nr.relation_type, 
                           nr.confidence, nr.metadata, nr.created_at,
                           n.type as source_type, n.value as source_value
                    FROM node_relations nr
                    JOIN nodes n ON nr.source_node_id = n.id
                    WHERE nr.target_node_id = %s
                    ORDER BY nr.created_at
                """
            else:
                query = """
                    SELECT nr.id, nr.source_node_id, nr.target_node_id, nr.relation_type, 
                           nr.confidence, nr.metadata, nr.created_at
                    FROM node_relations nr
                    WHERE nr.source_node_id = %s OR nr.target_node_id = %s
                    ORDER BY nr.created_at
                """
                cur.execute(query, (node_id, node_id))
                rows = cur.fetchall()
                return [
                    {
                        'id': row[0],
                        'source_node_id': row[1],
                        'target_node_id': row[2],
                        'relation_type': row[3],
                        'confidence': float(row[4]) if row[4] else None,
                        'metadata': row[5],
                        'created_at': row[6].isoformat() if row[6] else None
                    }
                    for row in rows
                ]

            cur.execute(query, (node_id,))
            rows = cur.fetchall()
            return [
                {
                    'id': str(row[0]),
                    'source_node_id': str(row[1]),
                    'target_node_id': str(row[2]),
                    'relation_type': row[3],
                    'confidence': float(row[4]) if row[4] else None,
                    'metadata': row[5],
                    'created_at': row[6].isoformat() if row[6] else None,
                    'related_node_type': row[7] if len(row) > 7 else None,
                    'related_node_value': row[8] if len(row) > 8 else None
                }
                for row in rows
            ]
        finally:
            cur.close()

