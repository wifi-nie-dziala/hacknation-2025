"""Convert all item types (file, link, text) to markdown text."""
import base64
import io
from typing import Dict, List
from markitdown import MarkItDown
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class ContentConverterService:
    """Converts files and URLs to markdown text."""

    def __init__(self):
        self.md_converter = MarkItDown()

    def convert_items_to_text(self, items: List[Dict]) -> List[Dict]:
        """Convert all items to text format with metadata headers."""
        text_items = []
        
        for item in items:
            item_type = item['type']
            
            if item_type == 'text':
                text_items.append({
                    'content': item['content'],
                    'source_type': 'text',
                    'original_item': item
                })
            
            elif item_type == 'file':
                converted = self._convert_file(item)
                text_items.append(converted)
            
            elif item_type == 'link':
                converted = self._convert_url(item)
                text_items.append(converted)
        
        return text_items

    def _convert_file(self, item: Dict) -> Dict:
        """Convert base64 file to markdown text."""
        try:
            file_content = base64.b64decode(item['content'])
            file_stream = io.BytesIO(file_content)
            
            result = self.md_converter.convert_stream(file_stream)
            markdown_text = result.text_content
            
            metadata_header = f"# Source: File\n\n"
            full_text = metadata_header + markdown_text
            
            return {
                'content': full_text,
                'source_type': 'file',
                'original_item': item,
                'conversion_success': True
            }
        
        except Exception as e:
            return {
                'content': f"# Source: File (Conversion Failed)\n\nError: {str(e)}",
                'source_type': 'file',
                'original_item': item,
                'conversion_success': False,
                'error': str(e)
            }

    def _convert_url(self, item: Dict) -> Dict:
        """Convert URL to markdown using playwright for JS rendering."""
        url = item['content']
        
        try:
            html_content = self._fetch_rendered_html(url)
            
            html_stream = io.BytesIO(html_content.encode('utf-8'))
            result = self.md_converter.convert_stream(html_stream, file_extension='.html')
            markdown_text = result.text_content
            
            metadata_header = f"# Source: {url}\n\n"
            full_text = metadata_header + markdown_text
            
            return {
                'content': full_text,
                'source_type': 'link',
                'original_item': item,
                'conversion_success': True,
                'url': url
            }
        
        except Exception as e:
            return {
                'content': f"# Source: {url} (Conversion Failed)\n\nError: {str(e)}",
                'source_type': 'link',
                'original_item': item,
                'conversion_success': False,
                'error': str(e),
                'url': url
            }

    def _fetch_rendered_html(self, url: str, timeout: int = 10000) -> str:
        """Fetch HTML after JS execution using playwright."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(url, wait_until='networkidle', timeout=timeout)
                html_content = page.content()
                
                browser.close()
                return html_content
        
        except PlaywrightTimeoutError:
            raise Exception(f"Timeout while loading {url}")
        except Exception as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")
