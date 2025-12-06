# Content Converter Service

Konwertuje wszystkie typy items (text, file, link) na markdown text przed wysłaniem do LLM.

## Użycie

```python
from services.content_converter_service import ContentConverterService

converter = ContentConverterService()

items = [
    {'type': 'text', 'content': 'Plain text content'},
    {'type': 'file', 'content': 'base64_encoded_pdf_or_docx'},
    {'type': 'link', 'content': 'https://example.com'}
]

# Konwertuj wszystkie items na text
converted = converter.convert_items_to_text(items)

# Każdy item ma teraz:
# - content: markdown text
# - source_type: text/file/link
# - conversion_success: True/False
# - original_item: oryginalny item
```

## Funkcje

### Files (PDF, DOCX, PPTX, XLSX)
- Używa `markitdown` do konwersji
- Dodaje header `# Source: File`
- Zachowuje strukturę dokumentu (nagłówki, listy, tabele)

### URLs
- Używa `playwright` do renderowania JS (dynamiczne strony)
- Konwertuje HTML do markdown przez `markitdown`
- Dodaje header `# Source: URL`
- Timeout: 10s

### Text
- Pozostaje bez zmian
- Tylko kopiuje content

## Instalacja

```bash
pip install 'markitdown[pdf,docx,pptx,xlsx]' playwright
playwright install chromium
```

## Integracja z ProcessingService

Processing service automatycznie konwertuje wszystkie items przed fact extraction:

```python
# W process_job():
converted_items = self.content_converter.convert_items_to_text(items)
all_content = [item['content'] for item in converted_items if item.get('conversion_success', True)]
```
