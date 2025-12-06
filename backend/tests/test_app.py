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


def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


@patch('app.get_db_connection')
@patch('app.ProcessingService')
def test_submit_job(mock_service, mock_db, client):
    mock_service_instance = Mock()
    mock_service.return_value = mock_service_instance
    mock_service_instance.create_job.return_value = 'test-uuid-123'

    response = client.post('/api/submit', json={
        'items': [{'type': 'text', 'content': 'Test', 'wage': 50}],
        'processing': {'enable_fact_extraction': True}
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['job_uuid'] == 'test-uuid-123'


def test_submit_job_no_items(client):
    response = client.post('/api/submit', json={})
    assert response.status_code == 400


@patch('app.get_db_connection')
def test_get_results(mock_db, client):
    from datetime import datetime
    mock_conn = Mock()
    mock_cur = Mock()
    mock_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    mock_cur.fetchall.side_effect = [
        [('job-uuid', 'completed', datetime(2024, 1, 1), datetime(2024, 1, 1))],
        [(1, 'Test fact', 'en', datetime(2024, 1, 1))]
    ]

    response = client.get('/api/results')
    assert response.status_code == 200
    data = response.get_json()
    assert 'jobs' in data
    assert 'facts' in data
    assert len(data['jobs']) == 1
    assert len(data['facts']) == 1


@patch('app.get_db_connection')
@patch('app.ProcessingService')
def test_get_job_details(mock_service, mock_db, client):
    mock_service_instance = Mock()
    mock_service.return_value = mock_service_instance
    mock_service_instance.get_job_status.return_value = {
        'job_uuid': 'test-uuid',
        'status': 'completed',
        'items': []
    }
    mock_service_instance.get_job_steps.return_value = []
    mock_service_instance.get_extracted_facts.return_value = []

    response = client.get('/api/jobs/test-uuid')
    assert response.status_code == 200
    data = response.get_json()
    assert 'job' in data
    assert 'steps' in data
    assert 'facts' in data


@patch('app.get_db_connection')
@patch('app.ProcessingService')
def test_get_job_details_not_found(mock_service, mock_db, client):
    mock_service_instance = Mock()
    mock_service.return_value = mock_service_instance
    mock_service_instance.get_job_status.return_value = None

    response = client.get('/api/jobs/nonexistent-uuid')
    assert response.status_code == 404


