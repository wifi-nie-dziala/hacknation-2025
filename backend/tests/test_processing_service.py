import pytest
import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.processing_service import ProcessingService


@pytest.fixture
def mock_conn():
    return Mock()


def test_create_job_valid(mock_conn):
    mock_cur = Mock()
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = ['test-uuid-123']

    service = ProcessingService(mock_conn)
    items = [
        {'type': 'text', 'content': 'Test content', 'wage': 50.0}
    ]

    job_uuid = service.create_job(items)
    assert job_uuid == 'test-uuid-123'
    mock_conn.commit.assert_called_once()


def test_create_job_empty_items(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="Items list cannot be empty"):
        service.create_job([])


def test_validate_item_no_type(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="Item must have 'type' field"):
        service._validate_item({'content': 'test'})


def test_validate_item_invalid_type(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="Invalid type"):
        service._validate_item({'type': 'invalid', 'content': 'test'})


def test_validate_item_no_content(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="Item must have 'content' field"):
        service._validate_item({'type': 'text'})


def test_validate_item_empty_content(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="Item content cannot be empty"):
        service._validate_item({'type': 'text', 'content': ''})


def test_validate_item_invalid_base64(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="File content must be valid base64"):
        service._validate_item({'type': 'file', 'content': 'not-base64!!!'})


def test_validate_item_valid_base64(mock_conn):
    service = ProcessingService(mock_conn)

    service._validate_item({'type': 'file', 'content': 'SGVsbG8gV29ybGQ='})


def test_validate_item_invalid_url(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="Link content must be a valid URL"):
        service._validate_item({'type': 'link', 'content': 'not-a-url'})


def test_validate_item_valid_url(mock_conn):
    service = ProcessingService(mock_conn)

    service._validate_item({'type': 'link', 'content': 'https://example.com'})
    service._validate_item({'type': 'link', 'content': 'http://example.com'})


def test_validate_item_invalid_wage(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="Wage must be a valid number"):
        service._validate_item({'type': 'text', 'content': 'test', 'wage': 'invalid'})


def test_get_job_status_not_found(mock_conn):
    mock_cur = Mock()
    mock_conn.cursor.return_value = mock_cur
    mock_cur.fetchone.return_value = None

    service = ProcessingService(mock_conn)
    result = service.get_job_status('non-existent-uuid')

    assert result is None


def test_get_job_status_success(mock_conn):
    mock_cur = Mock()
    mock_conn.cursor.return_value = mock_cur

    from datetime import datetime
    now = datetime.now()

    mock_cur.fetchone.return_value = (
        'test-uuid', 'completed', now, now, now, None
    )
    mock_cur.fetchall.return_value = [
        (1, 'text', 'content', 100.0, 'completed', 'processed', None)
    ]

    service = ProcessingService(mock_conn)
    result = service.get_job_status('test-uuid')

    assert result is not None
    assert result['job_uuid'] == 'test-uuid'
    assert result['status'] == 'completed'
    assert result['total_items'] == 1
    assert result['completed_items'] == 1
    assert result['failed_items'] == 0


def test_update_job_status_invalid_status(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="Invalid status"):
        service.update_job_status('uuid', 'invalid_status')


def test_update_job_status_success(mock_conn):
    mock_cur = Mock()
    mock_conn.cursor.return_value = mock_cur

    service = ProcessingService(mock_conn)
    service.update_job_status('test-uuid', 'completed', None)

    mock_conn.commit.assert_called_once()


def test_update_item_status_invalid_status(mock_conn):
    service = ProcessingService(mock_conn)

    with pytest.raises(ValueError, match="Invalid status"):
        service.update_item_status(1, 'invalid_status')


def test_update_item_status_success(mock_conn):
    mock_cur = Mock()
    mock_conn.cursor.return_value = mock_cur

    service = ProcessingService(mock_conn)
    service.update_item_status(1, 'completed', 'processed content', None)

    mock_conn.commit.assert_called_once()

