import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, get_db_connection


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'backend'


@patch('app.get_db_connection')
def test_facts_get(mock_db, client):
    from datetime import datetime
    mock_conn = Mock()
    mock_cur = Mock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = [
        (1, 'Test fact', 'en', datetime(2024, 1, 1))
    ]

    response = client.get('/api/facts')
    assert response.status_code == 200
    data = response.get_json()
    assert 'facts' in data
    assert len(data['facts']) == 1
    assert data['facts'][0]['fact'] == 'Test fact'


@patch('app.get_db_connection')
def test_facts_post(mock_db, client):
    mock_conn = Mock()
    mock_cur = Mock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = [123]

    response = client.post('/api/facts', json={
        'fact': 'New fact',
        'language': 'en'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['id'] == 123


def test_facts_post_no_fact(client):
    response = client.post('/api/facts', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


@patch('app.requests.post')
def test_extract_facts_en(mock_requests, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'response': 'Extracted facts'}
    mock_requests.return_value = mock_response

    response = client.post('/api/extract-facts-en', json={
        'text': 'Some text to extract facts from'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['facts'] == 'Extracted facts'
    assert data['language'] == 'en'


def test_extract_facts_en_no_text(client):
    response = client.post('/api/extract-facts-en', json={})
    assert response.status_code == 400


@patch('app.requests.post')
def test_extract_facts_pl(mock_requests, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'response': 'Wyodrębnione fakty'}
    mock_requests.return_value = mock_response

    response = client.post('/api/extract-facts-pl', json={
        'text': 'Tekst do wyodrębnienia faktów'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['facts'] == 'Wyodrębnione fakty'
    assert data['language'] == 'pl'


@patch('app.get_db_connection')
def test_search_facts(mock_db, client):
    mock_conn = Mock()
    mock_cur = Mock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchall.return_value = [
        (1, 'Similar fact', 'en', 0.1)
    ]

    embedding = [0.1] * 384
    response = client.post('/api/search', json={
        'embedding': embedding,
        'limit': 5
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'results' in data
    assert len(data['results']) == 1


def test_search_facts_no_embedding(client):
    response = client.post('/api/search', json={})
    assert response.status_code == 400

