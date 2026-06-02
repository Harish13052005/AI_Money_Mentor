import os
import logging
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    GROQ = "groq"
    TOGETHER = "together"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int, temperature: float) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
        except ImportError:
            self.client = None

    def generate_text(self, prompt: str, max_tokens: int, temperature: float) -> str:
        chat_completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            max_tokens=max_tokens,
            temperature=temperature
        )
        return chat_completion.choices[0].message.content

    def is_available(self) -> bool:
        return self.client is not None and bool(self.api_key)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            self.client = None

    def generate_text(self, prompt: str, max_tokens: int, temperature: float) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

    def is_available(self) -> bool:
        return self.client is not None and bool(self.api_key)

class TogetherProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            import together
            self.client = together
            self.client.api_key = api_key
        except ImportError:
            self.client = None

    def generate_text(self, prompt: str, max_tokens: int, temperature: float) -> str:
        response = self.client.Complete.create(
            prompt=f"<s>[INST] {prompt} [/INST]",
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response['output']['choices'][0]['text']

    def is_available(self) -> bool:
        return self.client is not None and bool(self.api_key)

class HuggingFaceProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(token=api_key)
        except ImportError:
            self.client = None

    def generate_text(self, prompt: str, max_tokens: int, temperature: float) -> str:
        response = self.client.text_generation(
            prompt,
            model="mistralai/Mistral-7B-Instruct-v0.2",
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        return response

    def is_available(self) -> bool:
        return self.client is not None and bool(self.api_key)

class LLMProviderManager:
    def __init__(self, api_keys: Dict[str, str], primary_provider: str = "groq"):
        self.providers: Dict[LLMProvider, BaseLLMProvider] = {}
        
        if api_keys.get("groq"):
            self.providers[LLMProvider.GROQ] = GroqProvider(api_keys["groq"])
        if api_keys.get("together"):
            self.providers[LLMProvider.TOGETHER] = TogetherProvider(api_keys["together"])
        if api_keys.get("huggingface"):
            self.providers[LLMProvider.HUGGINGFACE] = HuggingFaceProvider(api_keys["huggingface"])
        if api_keys.get("openai"):
            self.providers[LLMProvider.OPENAI] = OpenAIProvider(api_keys["openai"])
            
        # Safe enum lookup
        try:
            self.primary = LLMProvider(primary_provider.lower())
        except (ValueError, AttributeError):
            self.primary = LLMProvider.GROQ
        
        if self.primary not in self.providers or not self.providers[self.primary].is_available():
            logger.warning(f"Primary provider {self.primary} not available, will use fallback.")

    def get_available_providers(self) -> List[str]:
        return [p.value for p, inst in self.providers.items() if inst.is_available()]

    def set_provider(self, provider: LLMProvider) -> bool:
        if provider in self.providers and self.providers[provider].is_available():
            self.primary = provider
            return True
        return False

    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        # Try primary first
        order = [self.primary] + [p for p in LLMProvider if p != self.primary]
        
        last_error = None
        for provider_type in order:
            provider = self.providers.get(provider_type)
            if not provider or not provider.is_available():
                continue
                
            try:
                logger.info(f"Attempting generation with {provider_type.value}")
                return provider.generate_text(prompt, max_tokens, temperature)
            except Exception as e:
                logger.warning(f"Provider {provider_type.value} failed: {e}")
                last_error = e
                continue
        
        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    def health_check(self) -> Dict[str, bool]:
        return {p.value: inst.is_available() for p, inst in self.providers.items()}