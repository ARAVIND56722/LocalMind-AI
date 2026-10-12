import logging
from typing import List, Optional
from app.services.retrieval.index import BM25Index
from app.services.ingestion.ingester import TranscriptIngester, DocumentChunk
from app.schemas.schemas import SourceCitation
from app.core.config import settings

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self):
        self.index = BM25Index()
        self.is_initialized = False

    def initialize(self):
        """Initializes the index from saved cache or ingests from transcript repository."""
        if self.is_initialized:
            return

        # Try to load existing cached index
        if self.index.load(settings.RETRIEVAL_INDEX_FILE):
            self.is_initialized = True
            logger.info("Successfully loaded retrieval index from disk.")
            return

        # Otherwise ingest directly from transcripts directory
        logger.info(f"Building retrieval index from transcripts: {settings.TRANSCRIPTS_DATA_DIR}")
        ingester = TranscriptIngester(settings.TRANSCRIPTS_DATA_DIR)
        chunks = ingester.ingest_all(max_docs_per_folder=40)
        if chunks:
            self.index.fit(chunks)
            self.index.save(settings.RETRIEVAL_INDEX_FILE)
            self.is_initialized = True
            logger.info(f"Initialized retrieval engine with {len(chunks)} chunks.")
        else:
            logger.warning("No transcript chunks ingested. Index remains empty.")

    def search(self, query: str, top_k: int = 5) -> List[SourceCitation]:
        if not self.is_initialized:
            self.initialize()

        results = self.index.search(query, top_k=top_k)
        citations = []
        for chunk, score in results:
            citations.append(SourceCitation(
                id=chunk.chunk_id,
                title=chunk.title,
                guest=chunk.guest,
                timestamp=chunk.timestamp,
                speaker=chunk.speaker,
                url=chunk.url,
                quote=chunk.text[:500] + ("..." if len(chunk.text) > 500 else ""),
                score=round(score, 3)
            ))
        return citations

# Global singleton
retrieval_service = RetrievalService()
