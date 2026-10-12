import os
import json
import math
import re
import logging
from typing import List, Dict, Any, Optional
from app.services.ingestion.ingester import DocumentChunk

logger = logging.getLogger(__name__)

class BM25Index:
    """
    Lightweight, highly performant pure-Python BM25 Okapi retrieval engine.
    Zero external C-dependency issues, completely deterministic, fast indexing.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: List[int] = []
        self.avg_dl: float = 0.0
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.corpus_size: int = 0
        self.chunks: List[DocumentChunk] = []

    def tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_\-]{2,}\b', text)]

    def fit(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        self.corpus_size = len(chunks)
        self.doc_len = []
        self.doc_freqs = []
        df: Dict[str, int] = {}

        for chunk in chunks:
            # Combine title, guest, and text for rich retrieval indexing
            text_to_index = f"{chunk.title} {chunk.guest or ''} {chunk.speaker or ''} {chunk.text}"
            tokens = self.tokenize(text_to_index)
            self.doc_len.append(len(tokens))
            
            frequencies: Dict[str, int] = {}
            for token in tokens:
                frequencies[token] = frequencies.get(token, 0) + 1
            self.doc_freqs.append(frequencies)

            for token in frequencies:
                df[token] = df.get(token, 0) + 1

        self.avg_dl = sum(self.doc_len) / self.corpus_size if self.corpus_size > 0 else 0

        # Calculate IDF with standard Okapi smoothing
        self.idf = {}
        for token, freq in df.items():
            self.idf[token] = math.log(1 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 5) -> List[tuple[DocumentChunk, float]]:
        if not self.chunks or self.corpus_size == 0:
            return []

        tokens = self.tokenize(query)
        scores = [0.0] * self.corpus_size

        for token in tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]
            for i, doc_freq in enumerate(self.doc_freqs):
                if token in doc_freq:
                    freq = doc_freq[token]
                    numerator = freq * (self.k1 + 1)
                    denominator = freq + self.k1 * (1 - self.b + self.b * (self.doc_len[i] / self.avg_dl))
                    scores[i] += idf_val * (numerator / denominator)

        # Pair scores with chunks
        ranked = sorted(
            [(self.chunks[i], score) for i, score in enumerate(scores) if score > 0.05],
            key=lambda x: x[1],
            reverse=True
        )
        return ranked[:top_k]

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {
            "k1": self.k1,
            "b": self.b,
            "chunks": [c.to_dict() for c in self.chunks]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        logger.info(f"Saved retrieval index with {len(self.chunks)} items to {filepath}")

    def load(self, filepath: str) -> bool:
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            chunks = [DocumentChunk.from_dict(d) for d in data.get("chunks", [])]
            self.fit(chunks)
            logger.info(f"Loaded {len(chunks)} chunks into retrieval engine.")
            return True
        except Exception as e:
            logger.error(f"Failed to load index from {filepath}: {e}")
            return False
