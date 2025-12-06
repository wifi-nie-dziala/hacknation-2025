"""Processing orchestrator - coordinates all processing services."""
from typing import Dict
from .job_service import JobService
from .step_service import StepService
from .scraper_service import ScraperService
from .fact_extraction_service import FactExtractionService
from .fact_storage_service import FactStorageService


class ProcessingService:
    """Orchestrates the multi-step processing workflow."""

    def __init__(self, db_connection):
        self.conn = db_connection
        self.job_service = JobService(db_connection)
        self.step_service = StepService(db_connection)
        self.scraper_service = ScraperService(db_connection)
        self.fact_extraction_service = FactExtractionService()
        self.fact_storage_service = FactStorageService(db_connection)

    # Delegate to JobService
    def create_job(self, items):
        return self.job_service.create_job(items)

    def get_job_status(self, job_uuid):
        return self.job_service.get_job_status(job_uuid)

    def update_job_status(self, job_uuid, status, error_message=None):
        return self.job_service.update_job_status(job_uuid, status, error_message)

    def update_item_status(self, item_id, status, processed_content=None, error_message=None):
        return self.job_service.update_item_status(item_id, status, processed_content, error_message)

    # Delegate to StepService
    def get_job_steps(self, job_uuid):
        return self.step_service.get_job_steps(job_uuid)

    # Delegate to FactStorageService
    def get_extracted_facts(self, job_uuid, validated_only=False):
        return self.fact_storage_service.get_extracted_facts(job_uuid, validated_only)

    def validate_and_store_fact(self, fact_id, embedding=None):
        return self.fact_storage_service.validate_and_store_fact(fact_id, embedding)

    # Processing orchestration
    def process_job(self, job_uuid: str, processing_config: Dict):
        """Execute the processing workflow for a job."""
        step_number = 1
        language = processing_config.get('language', 'en')

        try:
            self.job_service.update_job_status(job_uuid, 'processing')

            job_status = self.job_service.get_job_status(job_uuid)
            if not job_status:
                return

            items = job_status['items']
            all_content = []

            # Step 1: Scraping
            if processing_config.get('enable_scraping'):
                all_content.extend(
                    self._scrape_links(job_uuid, items, step_number)
                )
                step_number += len([i for i in items if i['type'] == 'link'])

            # Add text items
            all_content.extend([
                item['content']
                for item in items
                if item['type'] == 'text'
            ])

            # Step 2: Fact Extraction
            if processing_config.get('enable_fact_extraction') and all_content:
                fact_ids = self._extract_facts(
                    job_uuid, all_content, language, step_number
                )
                step_number += 1

                # Step 3: Validation
                if processing_config.get('enable_validation'):
                    self._validate_facts(job_uuid, fact_ids, step_number)

            self.job_service.update_job_status(job_uuid, 'completed')

        except Exception as e:
            self.job_service.update_job_status(job_uuid, 'failed', str(e))
            raise

    def _scrape_links(self, job_uuid: str, items: list, step_number: int) -> list:
        """Scrape all link items."""
        scraped_content = []

        for item in items:
            if item['type'] == 'link':
                step_id = self.step_service.create_step(
                    job_uuid, step_number, 'scraping',
                    {'url': item['content']},
                    {'source': 'link_item'}
                )
                step_number += 1

                self.step_service.update_step(step_id, 'processing')
                result = self.scraper_service.scrape_url(job_uuid, step_id, item['content'])

                if result['success']:
                    scraped_content.append(result['content'])
                    self.step_service.update_step(
                        step_id, 'completed',
                        {'scraped_length': len(result['content'])}
                    )
                else:
                    self.step_service.update_step(
                        step_id, 'failed',
                        error_message=result['error']
                    )

        return scraped_content

    def _extract_facts(self, job_uuid: str, content_list: list, language: str, step_number: int) -> list:
        """Extract facts from content."""
        combined_text = ' '.join(content_list)[:10000]

        step_id = self.step_service.create_step(
            job_uuid, step_number, 'extraction',
            {'text_length': len(combined_text)},
            {'language': language}
        )

        self.step_service.update_step(step_id, 'processing')
        facts = self.fact_extraction_service.extract_facts(combined_text, language)

        fact_ids = []
        for fact in facts[:20]:
            fact_id = self.fact_storage_service.store_extracted_fact(
                job_uuid, step_id, fact, 'llm_extraction',
                combined_text[:500], 0.7, language
            )
            fact_ids.append(fact_id)

        self.step_service.update_step(
            step_id, 'completed',
            {'facts_extracted': len(facts)}
        )

        return fact_ids

    def _validate_facts(self, job_uuid: str, fact_ids: list, step_number: int):
        """Validate and store facts."""
        step_id = self.step_service.create_step(
            job_uuid, step_number, 'validation',
            {'fact_count': len(fact_ids)},
            {'auto_validate': True}
        )

        self.step_service.update_step(step_id, 'processing')

        for fact_id in fact_ids:
            self.fact_storage_service.validate_and_store_fact(fact_id)

        self.step_service.update_step(
            step_id, 'completed',
            {'validated_facts': len(fact_ids)}
        )

