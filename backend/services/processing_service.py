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

        print(f"[JOB {job_uuid}] Starting processing with config: {processing_config}", flush=True)

        try:
            self.job_service.update_job_status(job_uuid, 'processing')
            self.conn.commit()

            job_status = self.job_service.get_job_status(job_uuid)
            if not job_status:
                print(f"[JOB {job_uuid}] ERROR: Job not found", flush=True)
                return

            items = job_status['items']
            print(f"[JOB {job_uuid}] Found {len(items)} items to process", flush=True)

            # Step 1: Fact Extraction
            print(f"[JOB {job_uuid}] === STEP 1: FACT EXTRACTION ===", flush=True)
            fact_ids = self._extract_facts(
                job_uuid, items, language, step_number
            )
            self.conn.commit()
            print(f"[JOB {job_uuid}] STEP 1 COMPLETE: Extracted {len(fact_ids)} facts", flush=True)
            step_number += 1

            # Step 2: Validation
            print(f"[JOB {job_uuid}] === STEP 2: VALIDATION ===", flush=True)
            self._validate_facts(job_uuid, fact_ids, step_number)
            self.conn.commit()
            print(f"[JOB {job_uuid}] STEP 2 COMPLETE: Validated {len(fact_ids)} facts", flush=True)
            step_number += 1
            
            # Step 3: Prediction Extraction
            print(f"[JOB {job_uuid}] === STEP 3: PREDICTION EXTRACTION ===", flush=True)
            self._extract_predictions(job_uuid, items, language, step_number)
            self.conn.commit()
            print(f"[JOB {job_uuid}] STEP 3 COMPLETE: Predictions extracted", flush=True)
            step_number += 1

            # Step 4: Unknown Extraction
            print(f"[JOB {job_uuid}] === STEP 4: UNKNOWN EXTRACTION ===", flush=True)
            self._extract_unknowns(job_uuid, items, language, step_number)
            self.conn.commit()
            print(f"[JOB {job_uuid}] STEP 4 COMPLETE: Unknowns extracted", flush=True)
            step_number += 1

            self.job_service.update_job_status(job_uuid, 'completed')
            self.conn.commit()
            print(f"[JOB {job_uuid}] === JOB COMPLETED SUCCESSFULLY ===", flush=True)

        except Exception as e:
            print(f"[JOB {job_uuid}] === JOB FAILED: {str(e)} ===", flush=True)
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

        for idx, item in enumerate(items):
            item_id = item['id']
            item_type = item.get('item_type', 'unknown')
            wage = item.get('wage')
            print(f"[STEP {step_number}] Processing item {idx+1}/{len(items)}: id={item_id}, type={item_type}", flush=True)

            converted_items = self.content_converter.convert_items_to_text([item])
            if not converted_items or not converted_items[0].get('conversion_success', True):
                print(f"[STEP {step_number}] Item {item_id} conversion failed, skipping", flush=True)
                continue

            content = converted_items[0]['content'][:10000]
            print(f"[STEP {step_number}] Item {item_id} content length: {len(content)} chars", flush=True)

            facts = self.fact_extraction_service.extract_facts(content, language)
            print(f"[STEP {step_number}] Item {item_id} extracted {len(facts)} facts", flush=True)
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
        print(f"[STEP {step_number}] Completed fact extraction: {total_facts} facts extracted, {len(fact_ids)} stored", flush=True)

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

        fact_nodes = self.node_repository.get_nodes_by_job(job_uuid, 'fact')
        # Map by the fact text (node's 'value' field)
        fact_node_map = {f['value'][:100]: f for f in fact_nodes}

        print(f"[STEP {step_number}] Using {len(facts_data[:30])} facts as context, {len(fact_nodes)} fact nodes available", flush=True)

        all_content = []
        for item in items:
            converted_items = self.content_converter.convert_items_to_text([item])
            if converted_items and converted_items[0].get('conversion_success', True):
                all_content.append(converted_items[0]['content'][:5000])

        combined_content = "\n\n---\n\n".join(all_content)

        # Try to extract predictions with sources first
        predictions_with_sources = self.prediction_service.extract_predictions_with_sources(
            combined_content, language, facts_data[:30]
        )

        prediction_count = 0
        relation_count = 0

        if predictions_with_sources:
            print(f"[STEP {step_number}] Got {len(predictions_with_sources)} predictions with sources", flush=True)
            for pred_data in predictions_with_sources[:30]:
                pred_text = pred_data.get('prediction', '')
                source_facts = pred_data.get('source_facts', [])

                if pred_text and len(pred_text.strip()) > 10:
                    pred_node_id = self.node_repository.create_node(
                        'prediction', pred_text, job_uuid,
                        {'source': 'prediction_extraction', 'language': language, 'source_count': len(source_facts)}
                    )
                    prediction_count += 1

                    for src_fact in source_facts:
                        fact_text = src_fact.get('fact', '')[:100]
                        if fact_text in fact_node_map:
                            fact_node = fact_node_map[fact_text]
                            self.node_repository.create_relation(
                                pred_node_id, str(fact_node['id']), 'derived_from', 0.8
                            )
                            relation_count += 1
                            print(f"[RELATION] Created derived_from: prediction -> fact", flush=True)
                        else:
                            print(f"[RELATION] No matching fact node for: {fact_text[:50]}...", flush=True)
        else:
            # Fallback: use old method and link all predictions to all facts
            print(f"[STEP {step_number}] Sourced extraction failed, using fallback method", flush=True)
            facts_context = "\n".join([f"- {f['fact']}" for f in facts_data[:30]])
            predictions = self.prediction_service.extract_predictions(combined_content, language, facts_context)

            if predictions:
                print(f"[STEP {step_number}] Fallback extracted {len(predictions)} predictions", flush=True)
                for pred in predictions[:30]:
                    if pred and len(pred.strip()) > 10:
                        pred_node_id = self.node_repository.create_node(
                            'prediction', pred, job_uuid,
                            {'source': 'prediction_extraction_fallback', 'language': language}
                        )
                        prediction_count += 1

                        # Link to first few facts as general sources
                        for fact_node in list(fact_nodes)[:3]:
                            self.node_repository.create_relation(
                                pred_node_id, str(fact_node['id']), 'derived_from', 0.5
                            )
                            relation_count += 1
                        print(f"[RELATION] Created {min(3, len(fact_nodes))} fallback relations for prediction", flush=True)
            else:
                print(f"[STEP {step_number}] No predictions extracted from either method", flush=True)

        self.step_service.update_step(
            step_id, 'completed',
            {'predictions_extracted': prediction_count, 'relations_created': relation_count}
        )
        print(f"[STEP {step_number}] Completed prediction extraction: {prediction_count} predictions, {relation_count} relations created", flush=True)
        print(f"[STEP {step_number}] Prediction summary: LLM returned {len(predictions_with_sources)} predictions with sources", flush=True)

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
        print(f"[STEP {step_number}] Combined content length: {len(combined_content)} chars", flush=True)

        unknowns = self.unknown_service.extract_unknowns(combined_content, language, facts_context)
        print(f"[STEP {step_number}] LLM returned {len(unknowns) if unknowns else 0} unknowns", flush=True)

        if not unknowns:
            print(f"[STEP {step_number}] No unknowns extracted, skipping node creation", flush=True)

        unknown_count = 0
        for unknown in unknowns[:30]:
            if unknown and len(unknown.strip()) > 10:
                self.node_repository.create_node(
                    'missing_information', unknown, job_uuid,
                    {'source': 'unknown_extraction', 'language': language}
                )
                unknown_count += 1

        self.step_service.update_step(
            step_id, 'completed',
            {'unknowns_extracted': unknown_count}
        )
        print(f"[STEP {step_number}] Completed unknown extraction: {unknown_count} unknowns stored", flush=True)

