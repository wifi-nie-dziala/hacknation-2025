"""Test script for embedding service."""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_health():
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_single_text():
    print("Testing single text embedding...")
    data = {
        "texts": ["Hello world"]
    }
    response = requests.post(f"{BASE_URL}/embed", json=data)
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Count: {result.get('count')}")
    print(f"Dimension: {result.get('dimension')}")
    print(f"First 5 values: {result['embeddings'][0][:5]}\n")

def test_multiple_texts():
    print("Testing multiple texts...")
    data = {
        "texts": [
            "Artificial intelligence is transforming the world",
            "AI zmienia świat",
            "Climate change is a global challenge"
        ]
    }
    response = requests.post(f"{BASE_URL}/embed", json=data)
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Count: {result.get('count')}")
    print(f"Dimension: {result.get('dimension')}")
    
    # Show similarity between English and Polish AI sentences
    import numpy as np
    emb = np.array(result['embeddings'])
    similarity = np.dot(emb[0], emb[1]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]))
    print(f"Similarity between EN and PL AI text: {similarity:.4f}")
    
    similarity2 = np.dot(emb[0], emb[2]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[2]))
    print(f"Similarity between AI and Climate text: {similarity2:.4f}\n")

def test_long_corpus():
    print("Testing longer corpus (100 texts)...")
    data = {
        "texts": [f"This is sentence number {i} about various topics." for i in range(100)]
    }
    response = requests.post(f"{BASE_URL}/embed", json=data)
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Count: {result.get('count')}")
    print(f"Dimension: {result.get('dimension')}\n")

if __name__ == '__main__':
    print("=" * 60)
    print("EMBEDDING SERVICE TEST")
    print("=" * 60 + "\n")
    
    try:
        test_health()
        test_single_text()
        test_multiple_texts()
        test_long_corpus()
        print("✓ All tests passed!")
    except Exception as e:
        print(f"✗ Test failed: {e}")
