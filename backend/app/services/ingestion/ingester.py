import os
import re
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        doc_id: str,
        title: str,
        guest: Optional[str],
        date: Optional[str],
        doc_type: str,
        speaker: Optional[str],
        timestamp: Optional[str],
        text: str,
        source_file: str,
        url: Optional[str] = None
    ):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.title = title
        self.guest = guest
        self.date = date
        self.doc_type = doc_type
        self.speaker = speaker
        self.timestamp = timestamp
        self.text = text
        self.source_file = source_file
        self.url = url or f"https://www.lennysnewsletter.com/p/{doc_id}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "title": self.title,
            "guest": self.guest,
            "date": self.date,
            "doc_type": self.doc_type,
            "speaker": self.speaker,
            "timestamp": self.timestamp,
            "text": self.text,
            "source_file": self.source_file,
            "url": self.url
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentChunk":
        return cls(**data)


class TranscriptIngester:
    """
    Ingests and normalizes Lenny's Podcast and Newsletter transcripts from Markdown files.
    Preserves YAML frontmatter metadata (title, guest, date, etc.) and timestamps/speakers.
    """

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Extracts YAML frontmatter if present and returns (metadata, body)."""
        frontmatter = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                raw_fm = parts[1]
                body = parts[2].strip()
                for line in raw_fm.splitlines():
                    if ":" in line:
                        key, val = line.split(":", 1)
                        clean_key = key.strip()
                        clean_val = val.strip().strip('"').strip("'")
                        frontmatter[clean_key] = clean_val
        return frontmatter, body

    def chunk_document(
        self, 
        doc_id: str, 
        metadata: Dict[str, Any], 
        body: str, 
        filename: str, 
        chunk_size: int = 1200, 
        overlap: int = 200
    ) -> List[DocumentChunk]:
        """
        Chunks dialogue turns or paragraphs while maintaining speaker and timestamp context.
        """
        chunks = []
        # Pattern to detect speaker turn: **Speaker Name** (00:12:34):
        turn_pattern = re.compile(r'\*\*([^*]+)\*\*\s*\(([\d:]+)\):')
        
        # Split body into speaker blocks or paragraphs
        lines = body.split("\n\n")
        current_speaker = metadata.get("guest", "Speaker")
        current_timestamp = "00:00:00"
        
        current_chunk_text = []
        current_chunk_len = 0
        chunk_idx = 0

        for block in lines:
            block = block.strip()
            if not block:
                continue

            # Check if block introduces a new speaker
            match = turn_pattern.search(block)
            if match:
                current_speaker = match.group(1).strip()
                current_timestamp = match.group(2).strip()

            block_len = len(block)
            if current_chunk_len + block_len > chunk_size and current_chunk_text:
                full_text = "\n\n".join(current_chunk_text)
                chunk_id = f"{doc_id}_{chunk_idx}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    title=metadata.get("title", doc_id),
                    guest=metadata.get("guest"),
                    date=metadata.get("date"),
                    doc_type=metadata.get("type", "podcast"),
                    speaker=current_speaker,
                    timestamp=current_timestamp,
                    text=full_text,
                    source_file=filename,
                    url=metadata.get("url")
                ))
                chunk_idx += 1
                # Retain partial overlap if suitable
                current_chunk_text = [current_chunk_text[-1]] if len(current_chunk_text) > 1 else []
                current_chunk_len = len(current_chunk_text[0]) if current_chunk_text else 0

            current_chunk_text.append(block)
            current_chunk_len += block_len

        # Flush remaining text
        if current_chunk_text:
            full_text = "\n\n".join(current_chunk_text)
            chunk_id = f"{doc_id}_{chunk_idx}"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                title=metadata.get("title", doc_id),
                guest=metadata.get("guest"),
                date=metadata.get("date"),
                doc_type=metadata.get("type", "podcast"),
                speaker=current_speaker,
                timestamp=current_timestamp,
                text=full_text,
                source_file=filename,
                url=metadata.get("url")
            ))

        return chunks

    def ingest_all(self, max_docs_per_folder: Optional[int] = None) -> List[DocumentChunk]:
        """Ingests podcasts and newsletters from the transcripts repository."""
        all_chunks = []
        subdirs = ["podcasts", "newsletters"]
        
        for subdir in subdirs:
            target_path = os.path.join(self.data_dir, subdir)
            if not os.path.exists(target_path):
                logger.warning(f"Directory {target_path} does not exist, skipping.")
                continue

            files = [f for f in os.listdir(target_path) if f.endswith(".md")]
            if max_docs_per_folder:
                files = files[:max_docs_per_folder]

            for file in files:
                file_path = os.path.join(target_path, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        raw = f.read()
                    
                    doc_id = os.path.splitext(file)[0]
                    metadata, body = self.parse_frontmatter(raw)
                    if "title" not in metadata:
                        metadata["title"] = doc_id.replace("-", " ").title()
                    metadata["type"] = "podcast" if subdir == "podcasts" else "newsletter"
                    
                    chunks = self.chunk_document(doc_id, metadata, body, file)
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error(f"Error parsing {file_path}: {e}")

        logger.info(f"Ingested {len(all_chunks)} chunks across repository.")
        return all_chunks
