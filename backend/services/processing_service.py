"""Processing orchestrator - coordinates all processing services."""
from typing import Dict
from .job_service import JobService
from .step_service import StepService
from .scraper_service import ScraperService
from .fact_extraction_service import FactExtractionService
from .fact_storage_service import FactStorageService
from .content_converter_service import ContentConverterService
from .prediction_service import PredictionService
from .unknown_service import UnknownService
from repositories.node_repository import NodeRepository


class ProcessingService:
    """Orchestrates the multi-step processing workflow."""

    def __init__(self, db_connection):
        self.conn = db_connection
        self.job_service = JobService(db_connection)
        self.step_service = StepService(db_connection)
        self.scraper_service = ScraperService(db_connection)
        self.fact_extraction_service = FactExtractionService()
        self.fact_storage_service = FactStorageService(db_connection)
        self.content_converter = ContentConverterService()
        self.prediction_service = PredictionService()
        self.unknown_service = UnknownService()
        self.node_repository = NodeRepository(db_connection)

    # Delegate to JobService
    def create_job(self, items):
        return self.job_service.create_job(items)

    def get_job_status(self, job_uuid):
        return self.job_service.get_job_status(job_uuid)

    def get_all_jobs(self, limit=100):
        return self.job_service.get_all_jobs(limit)

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
            self.conn.commit()

            job_status = self.job_service.get_job_status(job_uuid)
            if not job_status:
                return

            items = job_status['items']
            
            # Step 1: Fact Extraction
            fact_ids = self._extract_facts(
                job_uuid, items, language, step_number
            )
            self.conn.commit()
            step_number += 1

            # Step 2: Validation
            self._validate_facts(job_uuid, fact_ids, step_number)
            self.conn.commit()
            step_number += 1
            
            # Step 3: Prediction Extraction
            self._extract_predictions(job_uuid, items, language, step_number)
            self.conn.commit()
            step_number += 1

            # Step 4: Unknown Extraction
            self._extract_unknowns(job_uuid, items, language, step_number)
            self.conn.commit()
            step_number += 1

            self.job_service.update_job_status(job_uuid, 'completed')
            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            self.job_service.update_job_status(job_uuid, 'failed', str(e))
            self.conn.commit()
            raise

    def _extract_facts(self, job_uuid: str, items: list, language: str, step_number: int) -> list:
        """Extract facts from content."""
        print(f"[STEP {step_number}] Starting fact extraction for {len(items)} items", flush=True)
        step_id = self.step_service.create_step(
            job_uuid, step_number, 'extraction',
            {'item_count': len(items)},
            {'language': language}
        )

        self.step_service.update_step(step_id, 'processing')

        fact_ids = []
        total_facts = 0

        for item in items:
            item_id = item['id']
            wage = item.get('wage')

            converted_items = self.content_converter.convert_items_to_text([item])
            if not converted_items or not converted_items[0].get('conversion_success', True):
                continue

            content = converted_items[0]['content'][:10000]

            facts = self.fact_extraction_service.extract_facts(content, language)
            total_facts += len(facts)

            for fact in facts[:20]:
                fact_id = self.fact_storage_service.store_extracted_fact(
                    job_uuid, step_id, fact, 'llm_extraction',
                    content[:500], item_id, wage, 0.7, language
                )
                fact_ids.append(fact_id)
                
                # Store fact in nodes
                self.node_repository.create_node(
                    'fact', fact, job_uuid,
                    {'source': 'fact_extraction', 'item_id': item_id, 'language': language}
                )

        self.step_service.update_step(
            step_id, 'completed',
            {'facts_extracted': total_facts}
        )
        print(f"[STEP {step_number}] Completed fact extraction: {total_facts} facts extracted", flush=True)

        return fact_ids

    def _validate_facts(self, job_uuid: str, fact_ids: list, step_number: int):
        """Validate and store facts."""
        print(f"[STEP {step_number}] Starting validation for {len(fact_ids)} facts", flush=True)
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
        print(f"[STEP {step_number}] Completed validation: {len(fact_ids)} facts validated", flush=True)

    def _extract_predictions(self, job_uuid: str, items: list, language: str, step_number: int):
        """Extract predictions with context from extracted facts."""
        print(f"[STEP {step_number}] Starting prediction extraction for {len(items)} items", flush=True)
        step_id = self.step_service.create_step(
            job_uuid, step_number, 'reasoning',
            {'item_count': len(items), 'task': 'prediction_extraction'},
            {'language': language}
        )

        self.step_service.update_step(step_id, 'processing')

        facts_data = self.fact_storage_service.get_extracted_facts(job_uuid, validated_only=False)
        facts_context = "\n".join([f"- {f['fact']}" for f in facts_data[:30]])
        print(f"[STEP {step_number}] Using {len(facts_data[:30])} facts as context", flush=True)

        all_content = []
        for item in items:
            converted_items = self.content_converter.convert_items_to_text([item])
            if converted_items and converted_items[0].get('conversion_success', True):
                all_content.append(converted_items[0]['content'][:5000])

        combined_content = "\n\n---\n\n".join(all_content)

        predictions = self.prediction_service.extract_predictions(combined_content, language, facts_context)

        if not predictions:
            print(f"[STEP {step_number}] No predictions extracted, skipping node creation", flush=True)

        for pred in predictions[:30]:
            if pred and len(pred.strip()) > 10:
                self.node_repository.create_node(
                    'prediction', pred, job_uuid,
                    {'source': 'prediction_extraction', 'language': language}
                )

        self.step_service.update_step(
            step_id, 'completed',
            {'predictions_extracted': len(predictions[:30])}
        )
        print(f"[STEP {step_number}] Completed prediction extraction: {len(predictions[:30])} predictions", flush=True)

    def _extract_unknowns(self, job_uuid: str, items: list, language: str, step_number: int):
        """Extract unknowns with context from extracted facts."""
        print(f"[STEP {step_number}] Starting unknown extraction for {len(items)} items", flush=True)
        step_id = self.step_service.create_step(
            job_uuid, step_number, 'reasoning',
            {'item_count': len(items), 'task': 'unknown_extraction'},
            {'language': language}
        )

        self.step_service.update_step(step_id, 'processing')

        facts_data = self.fact_storage_service.get_extracted_facts(job_uuid, validated_only=False)
        facts_context = "\n".join([f"- {f['fact']}" for f in facts_data[:30]])
        print(f"[STEP {step_number}] Using {len(facts_data[:30])} facts as context", flush=True)

        all_content = []
        for item in items:
            converted_items = self.content_converter.convert_items_to_text([item])
            if converted_items and converted_items[0].get('conversion_success', True):
                all_content.append(converted_items[0]['content'][:5000])

        combined_content = "\n\n---\n\n".join(all_content)

        unknowns = self.unknown_service.extract_unknowns(combined_content, language, facts_context)

        if not unknowns:
            print(f"[STEP {step_number}] No unknowns extracted, skipping node creation", flush=True)

        for unknown in unknowns[:30]:
            if unknown and len(unknown.strip()) > 10:
                self.node_repository.create_node(
                    'missing_information', unknown, job_uuid,
                    {'source': 'unknown_extraction', 'language': language}
                )

        self.step_service.update_step(
            step_id, 'completed',
            {'unknowns_extracted': len(unknowns[:30])}
        )
        print(f"[STEP {step_number}] Completed unknown extraction: {len(unknowns[:30])} unknowns", flush=True)

