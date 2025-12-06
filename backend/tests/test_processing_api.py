import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('app.get_db_connection')
def test_submit_processing_job(mock_db, client):
    mock_conn = Mock()
    mock_cur = Mock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = ['test-uuid-123']

    response = client.post('/api/processing/submit', json={
        'items': [
            {'type': 'text', 'content': 'Test content', 'wage': 50.0}
        ]
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['job_uuid'] == 'test-uuid-123'
    assert 'status_url' in data


def test_submit_processing_job_no_items(client):
    response = client.post('/api/processing/submit', json={})
    assert response.status_code == 400


def test_submit_processing_job_empty_items(client):
    response = client.post('/api/processing/submit', json={'items': []})
    assert response.status_code == 400


@patch('app.get_db_connection')
def test_get_processing_status(mock_db, client):
    from datetime import datetime
    mock_conn = Mock()
    mock_cur = Mock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    now = datetime.now()
    mock_cur.fetchone.return_value = (
        'test-uuid', 'completed', now, now, now, None
    )
    mock_cur.fetchall.return_value = [
        (1, 'text', 'content', 100.0, 'completed', 'processed', None)
    ]

    response = client.get('/api/processing/status/test-uuid')
    assert response.status_code == 200
    data = response.get_json()
    assert data['job_uuid'] == 'test-uuid'
    assert data['status'] == 'completed'
    assert data['total_items'] == 1


@patch('app.get_db_connection')
def test_get_processing_status_not_found(mock_db, client):
    mock_conn = Mock()
    mock_cur = Mock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = None

    response = client.get('/api/processing/status/non-existent')
    assert response.status_code == 404

