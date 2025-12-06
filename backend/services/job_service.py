"""Job and item management service."""
import base64
from typing import List, Dict, Optional
from repositories.job_repository import JobRepository
from repositories.item_repository import ItemRepository
from repositories.step_repository import StepRepository
from repositories.scraped_data_repository import ScrapedDataRepository
from repositories.fact_repository import FactRepository


class JobService:
    """Handles job and item business logic."""
    VALID_TYPES = ['text', 'file', 'link']
    VALID_STATUSES = ['pending', 'processing', 'completed', 'failed']

    def __init__(self, db_connection):
        self.conn = db_connection
        self.job_repo = JobRepository(db_connection)
        self.item_repo = ItemRepository(db_connection)
        self.step_repo = StepRepository(db_connection)
        self.scraped_repo = ScrapedDataRepository(db_connection)
        self.fact_repo = FactRepository(db_connection)

    def create_job(self, items: List[Dict]) -> str:
        if not items:
            raise ValueError("Items list cannot be empty")
        for item in items:
            self._validate_item(item)
        job_uuid = self.job_repo.create_job()
        for item in items:
            self.item_repo.create_item(
                job_uuid,
                item['type'],
                item['content'],
                item.get('wage')
            )
        return job_uuid

    def get_job_status(self, job_uuid: str) -> Optional[Dict]:
        job = self.job_repo.get_job_by_uuid(job_uuid)
        if not job:
            return None
        items = self.item_repo.get_items_by_job_uuid(job_uuid)
        return {
            **job,
            'items': items,
            'total_items': len(items),
            'completed_items': sum(1 for item in items if item['status'] == 'completed'),
            'failed_items': sum(1 for item in items if item['status'] == 'failed')
        }

    def get_all_jobs(self, limit: int = 100) -> List[Dict]:
        jobs = self.job_repo.get_all_jobs(limit)
        for job in jobs:
            job_uuid = job['job_uuid']
            items = self.item_repo.get_items_by_job_uuid(job_uuid)
            steps = self.step_repo.get_steps_by_job_uuid(job_uuid)
            scraped_data = self.scraped_repo.get_scraped_data_by_job_uuid(job_uuid)
            extracted_facts = self.fact_repo.get_facts_by_job_uuid(job_uuid)
            job.update({
                'items': items,
                'steps': steps,
                'scraped_data': scraped_data,
                'extracted_facts': extracted_facts,
                'total_items': len(items),
                'completed_items': sum(1 for item in items if item['status'] == 'completed'),
                'failed_items': sum(1 for item in items if item['status'] == 'failed')
            })
        return jobs

    def update_job_status(self, job_uuid: str, status: str, error_message: Optional[str] = None):
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        self.job_repo.update_job_status(job_uuid, status, error_message)

    def update_item_status(self, item_id: int, status: str,
                           processed_content: Optional[str] = None,
                           error_message: Optional[str] = None):
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        self.item_repo.update_item_status(item_id, status, processed_content, error_message)

    def _validate_item(self, item: Dict):
        if 'type' not in item:
            raise ValueError("Item must have 'type' field")
        if item['type'] not in self.VALID_TYPES:
            raise ValueError(f"Invalid type: {item['type']}. Must be one of {self.VALID_TYPES}")
        if 'content' not in item:
            raise ValueError("Item must have 'content' field")
        if not item['content']:
            raise ValueError("Item content cannot be empty")
        if item['type'] == 'file':
            try:
                base64.b64decode(item['content'], validate=True)
            except Exception as e:
                raise ValueError(f"File content must be valid base64 encoded string: {str(e)}")
        if item['type'] == 'link':
            content = item['content'].strip()
            if not (content.startswith('http://') or content.startswith('https://')):
                raise ValueError("Link content must be a valid URL starting with http:// or https://")
        if 'wage' in item and item['wage'] is not None:
            try:
                float(item['wage'])
            except (ValueError, TypeError):
                raise ValueError("Wage must be a valid number")
