"""LLM client interface for Ollama Cloud."""
import json
import logging
import httpx
from typing import List, Dict, Any, Optional
from src.config import OLLAMA_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger("recruitment_assistant.llm")

class OllamaCloudLLM:
    """Direct high-reliability client for Ollama Cloud API."""
    
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or OLLAMA_MODEL
        self.api_key = api_key or OLLAMA_API_KEY
        self.base_url = OLLAMA_BASE_URL
        if not self.api_key:
            logger.warning("OLLAMA_API_KEY is missing. Model queries might fail.")
            
    def invoke(self, prompt: str, system: Optional[str] = None) -> str:
        """Call Ollama Cloud generate/chat endpoint synchronously."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        endpoint = f"{self.base_url}/api/chat"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama API Error ({resp.status_code}): {resp.text}")
            data = resp.json()
            return data.get("message", {}).get("content", "")

    async def ainvoke(self, prompt: str, system: Optional[str] = None) -> str:
        """Asynchronous call to Ollama Cloud API."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        endpoint = f"{self.base_url}/api/chat"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(endpoint, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama API Error ({resp.status_code}): {resp.text}")
            data = resp.json()
            return data.get("message", {}).get("content", "")

# Default instance
llm_client = OllamaCloudLLM()
