"""Web scraping service."""
import json
import requests
from typing import Dict
from bs4 import BeautifulSoup


class ScraperService:
    """Handles web scraping operations."""

    def __init__(self, db_connection):
        self.conn = db_connection

    def scrape_url(self, job_uuid: str, step_id: int, url: str) -> Dict:
        """Scrape content from a URL."""
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO scraped_data (job_id, step_id, url, status)
                VALUES (
                    (SELECT id FROM processing_jobs WHERE job_uuid = %s),
                    %s, %s, 'pending'
                )
                RETURNING id
                """,
                (job_uuid, step_id, url)
            )
            scraped_id = cur.fetchone()[0]
            self.conn.commit()

            try:
                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; FactExtractor/1.0)'
                })
                response.raise_for_status()

                text = self._extract_text(response.text)

                cur.execute(
                    """
                    UPDATE scraped_data
                    SET content = %s, content_type = %s, status = 'completed',
                        metadata = %s
                    WHERE id = %s
                    """,
                    (text, response.headers.get('Content-Type'),
                     json.dumps({'status_code': response.status_code}), scraped_id)
                )
                self.conn.commit()

                return {'success': True, 'content': text, 'url': url}

            except Exception as e:
                cur.execute(
                    """
                    UPDATE scraped_data
                    SET status = 'failed', error_message = %s
                    WHERE id = %s
                    """,
                    (str(e), scraped_id)
                )
                self.conn.commit()
                return {'success': False, 'error': str(e), 'url': url}

        finally:
            cur.close()

    def _extract_text(self, html: str) -> str:
        """Extract clean text from HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

