from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from pgvector.psycopg2 import register_vector
from services.processing_service import ProcessingService
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


@app.route('/api/results', methods=['GET'])
def get_results():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            SELECT job_uuid, status, created_at, completed_at
            FROM processing_jobs
            ORDER BY created_at DESC
            LIMIT 100
        ''')
        jobs = cur.fetchall()

        cur.execute('''
            SELECT id, fact, language, created_at
            FROM facts
            ORDER BY created_at DESC
            LIMIT 100
        ''')
        facts = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({
            'jobs': [{
                'job_uuid': str(j[0]),
                'status': j[1],
                'created_at': j[2].isoformat() if j[2] else None,
                'completed_at': j[3].isoformat() if j[3] else None
            } for j in jobs],
            'facts': [{
                'id': f[0],
                'fact': f[1],
                'language': f[2],
                'created_at': f[3].isoformat() if f[3] else None
            } for f in facts]
        }), 200
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



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT, debug=config.FLASK_DEBUG)
