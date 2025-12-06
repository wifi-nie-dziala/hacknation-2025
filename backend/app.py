from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from pgvector.psycopg2 import register_vector
import requests
import os
from services.processing_service import ProcessingService

app = Flask(__name__)
CORS(app)

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'database')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'hacknation')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# LLM configuration
LLM_EN_HOST = os.getenv('LLM_EN_HOST', 'llm-en')
LLM_EN_PORT = os.getenv('LLM_EN_PORT', '11434')
LLM_PL_HOST = os.getenv('LLM_PL_HOST', 'llm-pl')
LLM_PL_PORT = os.getenv('LLM_PL_PORT', '11434')


def get_db_connection():
    """Create and return a database connection."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    register_vector(conn)
    return conn


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'backend'}), 200


@app.route('/api/extract-facts-en', methods=['POST'])
def extract_facts_en():
    """Extract facts from English text using the English LLM."""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Call English LLM
        response = requests.post(
            f'http://{LLM_EN_HOST}:{LLM_EN_PORT}/api/generate',
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
    """Extract facts from Polish text using the Polish LLM."""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Call Polish LLM
        response = requests.post(
            f'http://{LLM_PL_HOST}:{LLM_PL_PORT}/api/generate',
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
    # Debug mode should only be enabled in development
    # In production, use gunicorn (see Dockerfile)
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', '8080'))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
