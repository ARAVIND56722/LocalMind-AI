import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.ingestion.ingester import TranscriptIngester
from app.services.retrieval.index import BM25Index
from app.core.config import settings

def main():
    print(f"Ingesting transcripts from: {settings.TRANSCRIPTS_DATA_DIR}")
    ingester = TranscriptIngester(settings.TRANSCRIPTS_DATA_DIR)
    chunks = ingester.ingest_all()
    
    if not chunks:
        print("ERROR: No transcript chunks found. Please check TRANSCRIPTS_DATA_DIR.")
        sys.exit(1)
        
    print(f"Successfully parsed {len(chunks)} chunks.")
    print("Building BM25 indexing model...")
    index = BM25Index()
    index.fit(chunks)
    
    target_path = settings.RETRIEVAL_INDEX_FILE
    index.save(target_path)
    print(f"Retrieval index saved to: {target_path}")
    print("Knowledge base ready!")

if __name__ == "__main__":
    main()
