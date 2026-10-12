import re
import html
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ArtifactCompiler:
    """
    Extracts, compiles, and applies strict security isolation policies to artifacts.
    Treats all AI-generated HTML as untrusted input.
    """

    @staticmethod
    def extract_artifact_from_text(text: str) -> Optional[Dict[str, str]]:
        """
        Detects if model output includes an explicit artifact block (HTML, Markdown, or Code).
        """
        # Look for ```html ... ```
        html_match = re.search(r'```html\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
        if html_match:
            raw_html = html_match.group(1).strip()
            # Extract possible title
            title_match = re.search(r'<title>(.*?)</title>', raw_html, re.IGNORECASE)
            title = title_match.group(1) if title_match else "Interactive HTML Document"
            return {
                "title": title,
                "artifact_type": "html",
                "content": ArtifactCompiler.sanitize_and_sandbox_html(raw_html)
            }

        # Look for ```markdown ... ```
        md_match = re.search(r'```markdown\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
        if md_match:
            raw_md = md_match.group(1).strip()
            first_line = raw_md.splitlines()[0].lstrip("#").strip() if raw_md else "Markdown Document"
            return {
                "title": first_line or "Editorial Markdown Artifact",
                "artifact_type": "markdown",
                "content": raw_md
            }

        return None

    @staticmethod
    def sanitize_and_sandbox_html(raw_html: str) -> str:
        """
        Enforces defense-in-depth isolation for HTML documents:
        1. Strips dangerous script tags and inline event handlers (onerror, onload, onclick).
        2. Injects restrictive Content Security Policy (CSP meta tag).
        3. Wraps with baseline responsive modern styling if bare fragment.
        """
        # Strip script tags
        sanitized = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', raw_html, flags=re.IGNORECASE)
        # Strip inline event handlers
        sanitized = re.sub(r'\bon\w+\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+)', '', sanitized, flags=re.IGNORECASE)

        csp_meta = (
            '<meta http-equiv="Content-Security-Policy" content="'
            "default-src 'none'; "
            "style-src 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src https://fonts.gstatic.com data:; "
            "img-src data: https:; "
            "base-uri 'none'; "
            "form-action 'none';"
            '">'
        )

        base_styles = """
        <style>
            :root { color-scheme: light; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                margin: 0; padding: 24px; color: #1E221E; background: #FFFFFF; line-height: 1.6;
            }
            * { box-sizing: border-box; }
        </style>
        """

        if "<head>" in sanitized.lower():
            # Inject CSP right after <head>
            sanitized = re.sub(r'(<head[^>]*>)', r'\1\n' + csp_meta + base_styles, sanitized, flags=re.IGNORECASE)
        else:
            # Wrap standalone body or snippet into complete HTML doc
            sanitized = f"<!DOCTYPE html><html><head>{csp_meta}{base_styles}</head><body>{sanitized}</body></html>"

        return sanitized

artifact_compiler = ArtifactCompiler()
