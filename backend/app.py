from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from pgvector.psycopg2 import register_vector
from services.processing_service import ProcessingService
from repositories.node_repository import NodeRepository
import config
import threading

app = Flask(__name__)
CORS(app)


def get_db_connection():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )
    register_vector(conn)
    return conn


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/submit', methods=['POST'])
def submit_job():
    data = request.json
    if not data or 'items' not in data:
        return jsonify({'error': 'Missing items'}), 400

    items = data.get('items', [])
    processing_config = data.get('processing', {})

    if not items:
        return jsonify({'error': 'Empty items'}), 400

    try:
        conn = get_db_connection()
        processing_service = ProcessingService(conn)
        job_uuid = processing_service.create_job(items)
        conn.close()

        if processing_config:
            def process_in_background():
                conn = get_db_connection()
                service = ProcessingService(conn)
                try:
                    service.process_job(job_uuid, processing_config)
                finally:
                    conn.close()

            thread = threading.Thread(target=process_in_background, daemon=True)
            thread.start()

        return jsonify({'job_uuid': job_uuid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/jobs/<job_uuid>', methods=['GET'])
def get_job_details(job_uuid):
    try:
        conn = get_db_connection()
        processing_service = ProcessingService(conn)

        job_status = processing_service.get_job_status(job_uuid)
        if not job_status:
            conn.close()
            return jsonify({'error': 'Job not found'}), 404

        steps = processing_service.get_job_steps(job_uuid)
        facts = processing_service.get_extracted_facts(job_uuid)

        conn.close()

        return jsonify({
            'job': job_status,
            'steps': steps,
            'facts': facts
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs', methods=['GET'])
def get_all_jobs():
    try:
        limit = request.args.get('limit', 100, type=int)

        conn = get_db_connection()
        processing_service = ProcessingService(conn)

        jobs = processing_service.get_all_jobs(limit)

        conn.close()

        return jsonify({'jobs': jobs, 'count': len(jobs)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/jobs/<job_uuid>/nodes', methods=['GET'])
def get_job_nodes(job_uuid):
    try:
        node_type = request.args.get('type')

        conn = get_db_connection()
        node_repo = NodeRepository(conn)
        nodes = node_repo.get_nodes_by_job(job_uuid, node_type)
        conn.close()

        return jsonify({'nodes': nodes, 'count': len(nodes)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/nodes/<node_id>', methods=['GET'])
def get_node(node_id):
    try:
        conn = get_db_connection()
        node_repo = NodeRepository(conn)
        node = node_repo.get_node(node_id)
        conn.close()

        if not node:
            return jsonify({'error': 'Node not found'}), 404

        return jsonify({'node': node}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/nodes/<node_id>/relations', methods=['GET'])
def get_node_relations(node_id):
    try:
        direction = request.args.get('direction', 'both')

        if direction not in ['incoming', 'outgoing', 'both']:
            return jsonify({'error': 'Invalid direction. Must be: incoming, outgoing, or both'}), 400

        conn = get_db_connection()
        node_repo = NodeRepository(conn)
        relations = node_repo.get_node_relations(node_id, direction)
        conn.close()

        return jsonify({'relations': relations, 'count': len(relations)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT, debug=config.FLASK_DEBUG)
