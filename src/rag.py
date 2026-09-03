"""Document processing and semantic retrieval engine (Agentic RAG)."""
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract raw text cleanly from a PDF file."""
    reader = PdfReader(str(pdf_path))
    pages_text = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(text.strip())
    return "\n\n".join(pages_text)

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[Dict[str, Any]]:
    """Chunk document text into overlapping segments with metadata."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = []
    current_len = 0
    chunk_id = 0

    for para in paragraphs:
        words = para.split()
        if current_len + len(words) > chunk_size and current_chunk:
            chunk_content = " ".join(current_chunk)
            chunks.append({
                "id": chunk_id,
                "text": chunk_content,
                "token_estimate": len(current_chunk)
            })
            chunk_id += 1
            # Keep overlap
            overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = list(overlap_words)
            current_len = len(current_chunk)
            
        current_chunk.extend(words)
        current_len += len(words)

    if current_chunk:
        chunks.append({
            "id": chunk_id,
            "text": " ".join(current_chunk),
            "token_estimate": len(current_chunk)
        })

    return chunks

class LocalSemanticRAGStore:
    """Fast, lightweight, sub-millisecond in-memory vector store for Agentic RAG."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True
        )
        self.chunks: List[Dict[str, Any]] = []
        self.matrix = None
        self.is_indexed = False

    def index_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """Fit vectorizer and index chunk collection."""
        if not chunks:
            return
        self.chunks = chunks
        corpus = [c["text"] for c in chunks]
        self.matrix = self.vectorizer.fit_transform(corpus)
        self.is_indexed = True

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve top_k most relevant chunks for a specific query."""
        if not self.is_indexed or not query.strip():
            return []
        
        try:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.matrix).flatten()
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score > 0.01:
                    results.append({
                        "chunk": self.chunks[idx],
                        "score": round(score, 4)
                    })
            return results
        except Exception:
            return []
