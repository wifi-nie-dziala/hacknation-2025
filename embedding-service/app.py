from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import numpy as np

app = Flask(__name__)

# Lightweight model for CPU - multilingual, good quality
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model': 'paraphrase-multilingual-MiniLM-L12-v2'}), 200

@app.route('/embed', methods=['POST'])
def embed():
    data = request.json
    
    if not data or 'texts' not in data:
        return jsonify({'error': 'Missing texts field'}), 400
    
    texts = data['texts']
    
    if not isinstance(texts, list):
        return jsonify({'error': 'texts must be an array'}), 400
    
    if len(texts) == 0:
        return jsonify({'error': 'texts array is empty'}), 400
    
    try:
        embeddings = model.encode(texts, show_progress_bar=False)
        embeddings_list = embeddings.tolist()
        
        return jsonify({
            'embeddings': embeddings_list,
            'count': len(embeddings_list),
            'dimension': len(embeddings_list[0])
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
