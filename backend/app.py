from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from pgvector.psycopg2 import register_vector
import requests
from services.processing_service import ProcessingService
import config

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
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'backend'}), 200


@app.route('/api/extract-facts-en', methods=['POST'])
def extract_facts_en():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        response = requests.post(
            f'http://{config.LLM_EN_HOST}:{config.LLM_EN_PORT}/api/generate',
            json={
                'model': 'llama2',
                'prompt': f'Extract key facts from the following text:\n\n{text}\n\nFacts:',
                'stream': False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'facts': result.get('response', ''),
                'language': 'en'
            }), 200
        else:
            return jsonify({'error': 'LLM request failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/extract-facts-pl', methods=['POST'])
def extract_facts_pl():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        response = requests.post(
            f'http://{config.LLM_PL_HOST}:{config.LLM_PL_PORT}/api/generate',
            json={
                'model': 'llama2',
                'prompt': f'Wyodrębnij kluczowe fakty z następującego tekstu:\n\n{text}\n\nFakty:',
                'stream': False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'facts': result.get('response', ''),
                'language': 'pl'
            }), 200
        else:
            return jsonify({'error': 'LLM request failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/facts', methods=['GET', 'POST'])
def facts():
    """Get or store facts in the vector database."""
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT id, fact, language, created_at FROM facts ORDER BY created_at DESC LIMIT 100')
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            facts_list = [
                {
                    'id': row[0],
                    'fact': row[1],
                    'language': row[2],
                    'created_at': row[3].isoformat() if row[3] else None
                }
                for row in rows
            ]
            
            return jsonify({'facts': facts_list}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    elif request.method == 'POST':
        data = request.json
        fact = data.get('fact', '')
        language = data.get('language', 'en')
        embedding = data.get('embedding', None)
        
        if not fact:
            return jsonify({'error': 'No fact provided'}), 400
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            if embedding:
                cur.execute(
                    'INSERT INTO facts (fact, language, embedding) VALUES (%s, %s, %s) RETURNING id',
                    (fact, language, embedding)
                )
            else:
                cur.execute(
                    'INSERT INTO facts (fact, language) VALUES (%s, %s) RETURNING id',
                    (fact, language)
                )
            
            fact_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({'id': fact_id, 'message': 'Fact stored successfully'}), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search_facts():
    """Search for similar facts using vector similarity."""
    data = request.json
    query_embedding = data.get('embedding', None)
    limit = data.get('limit', 10)
    
    if not query_embedding:
        return jsonify({'error': 'No embedding provided'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            '''
            SELECT id, fact, language, embedding <-> %s AS distance
            FROM facts
            WHERE embedding IS NOT NULL
            ORDER BY distance
            LIMIT %s
            ''',
            (query_embedding, limit)
        )
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        results = [
            {
                'id': row[0],
                'fact': row[1],
                'language': row[2],
                'distance': float(row[3])
            }
            for row in rows
        ]
        
        return jsonify({'results': results}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/processing/submit', methods=['POST'])
def submit_processing_job():
    """Submit a new processing job with a list of items.

    Expected JSON format:
    {
        "items": [
            {
                "type": "text|file|link",
                "content": "text content | base64-encoded file | URL",
                "wage": 100.50
            },
            ...
        ]
    }

    Content requirements by type:
    - text: Plain text string
    - file: Base64-encoded file content (e.g., PDF)
    - link: Valid URL starting with http:// or https://

    Returns:
    {
        "job_uuid": "uuid-string",
        "status_url": "/api/processing/status/{uuid}"
    }
    """
    data = request.json

    if not data or 'items' not in data:
        return jsonify({'error': 'Request must contain "items" field'}), 400

    items = data.get('items', [])

    if not isinstance(items, list):
        return jsonify({'error': '"items" must be a list'}), 400

    if not items:
        return jsonify({'error': '"items" list cannot be empty'}), 400

    try:
        conn = get_db_connection()
        processing_service = ProcessingService(conn)

        # Create the job
        job_uuid = processing_service.create_job(items)

        # Close connection
        conn.close()

        # Return the job UUID and status URL
        status_url = f'/api/processing/status/{job_uuid}'

        return jsonify({
            'job_uuid': job_uuid,
            'status_url': status_url,
            'message': f'Processing job created successfully with {len(items)} item(s)'
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create processing job: {str(e)}'}), 500


@app.route('/api/processing/jobs', methods=['GET'])
def get_processing_jobs():
    """Get list of all processing jobs.

    Query parameters:
    - status: Filter by status (pending|processing|completed|failed)
    - limit: Max number of results (default 100)
    - offset: Pagination offset (default 0)

    Returns:
    {
        "jobs": [
            {
                "job_uuid": "uuid-string",
                "status": "pending|processing|completed|failed",
                "created_at": "ISO timestamp",
                "updated_at": "ISO timestamp",
                "completed_at": "ISO timestamp or null",
                "error_message": "error message or null",
                "total_items": 5,
                "completed_items": 3,
                "failed_items": 0
            },
            ...
        ],
        "total": 10,
        "limit": 100,
        "offset": 0
    }
    """
    status = request.args.get('status', None)
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if status:
            count_query = 'SELECT COUNT(*) FROM processing_jobs WHERE status = %s'
            cur.execute(count_query, (status,))
        else:
            count_query = 'SELECT COUNT(*) FROM processing_jobs'
            cur.execute(count_query)

        total = cur.fetchone()[0]

        if status:
            query = '''
                SELECT job_uuid, status, created_at, updated_at, completed_at, error_message
                FROM processing_jobs
                WHERE status = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            '''
            cur.execute(query, (status, limit, offset))
        else:
            query = '''
                SELECT job_uuid, status, created_at, updated_at, completed_at, error_message
                FROM processing_jobs
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            '''
            cur.execute(query, (limit, offset))

        rows = cur.fetchall()

        jobs = []
        for row in rows:
            job_uuid = str(row[0])

            cur.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM processing_items
                WHERE job_id = (SELECT id FROM processing_jobs WHERE job_uuid = %s)
            ''', (job_uuid,))

            stats = cur.fetchone()

            jobs.append({
                'job_uuid': job_uuid,
                'status': row[1],
                'created_at': row[2].isoformat() if row[2] else None,
                'updated_at': row[3].isoformat() if row[3] else None,
                'completed_at': row[4].isoformat() if row[4] else None,
                'error_message': row[5],
                'total_items': int(stats[0]) if stats[0] else 0,
                'completed_items': int(stats[1]) if stats[1] else 0,
                'failed_items': int(stats[2]) if stats[2] else 0
            })

        cur.close()
        conn.close()

        return jsonify({
            'jobs': jobs,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get jobs: {str(e)}'}), 500


@app.route('/api/processing/status/<job_uuid>', methods=['GET'])
def get_processing_status(job_uuid):
    """Get the status of a processing job.

    Returns:
    {
        "job_uuid": "uuid-string",
        "status": "pending|processing|completed|failed",
        "created_at": "ISO timestamp",
        "updated_at": "ISO timestamp",
        "completed_at": "ISO timestamp or null",
        "error_message": "error message or null",
        "total_items": 5,
        "completed_items": 3,
        "failed_items": 0,
        "items": [
            {
                "id": 1,
                "type": "text",
                "content": "...",
                "wage": 100.50,
                "status": "completed",
                "processed_content": "...",
                "error_message": null
            },
            ...
        ]
    }
    """
    try:
        conn = get_db_connection()
        processing_service = ProcessingService(conn)

        # Get job status
        job_status = processing_service.get_job_status(job_uuid)

        # Close connection
        conn.close()

        if not job_status:
            return jsonify({'error': 'Job not found'}), 404

        return jsonify(job_status), 200

    except Exception as e:
        return jsonify({'error': f'Failed to get job status: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT, debug=config.FLASK_DEBUG)
