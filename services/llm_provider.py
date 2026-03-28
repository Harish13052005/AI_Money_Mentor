"""
Multi-provider LLM abstraction layer.
Supports: Groq, HuggingFace, Together AI, OpenAI with automatic fallback.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging
from enum import Enum
import time

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers."""
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    TOGETHER = "together"
    OPENAI = "openai"


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: str, model: str = None, timeout: int = 30):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate text based on prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and API key is valid."""
        pass


class GroqProvider(BaseLLMProvider):
    """Groq API provider - FREE with generous rate limits."""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        super().__init__(api_key, model)
        if not api_key or api_key == "your-groq-api-key":
            raise ValueError("Groq API key not configured")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client."""
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            logger.info("Groq client initialized successfully")
        except ImportError:
            logger.error("groq library not installed. Install with: pip install groq")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise
    
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate text using Groq API."""
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.timeout
            )
            return message.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check Groq availability."""
        try:
            # Simple test to verify API key works
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
                timeout=5
            )
            return True
        except Exception as e:
            logger.warning(f"Groq provider unavailable: {e}")
            return False


class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace Inference API provider - FREE tier available."""
    
    def __init__(self, api_key: str, model: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        super().__init__(api_key, model)
        if not api_key or api_key == "your-huggingface-api-key":
            raise ValueError("HuggingFace API key not configured")
        self.endpoint = f"https://api-inference.huggingface.co/models/{model}"
    
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate text using HuggingFace API."""
        try:
            import requests
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                }
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"HuggingFace API error: {response.text}")
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            return ""
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check HuggingFace availability."""
        try:
            import requests
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                "https://api-inference.huggingface.co/api/whoami",
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"HuggingFace provider unavailable: {e}")
            return False


class TogetherAIProvider(BaseLLMProvider):
    """Together AI provider - FREE tier with good limits."""
    
    def __init__(self, api_key: str, model: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        super().__init__(api_key, model)
        if not api_key or api_key == "your-together-api-key":
            raise ValueError("Together AI API key not configured")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Together AI client."""
        try:
            from together import Together
            self.client = Together(api_key=self.api_key)
            logger.info("Together AI client initialized successfully")
        except ImportError:
            logger.error("together library not installed. Install with: pip install together")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Together AI client: {e}")
            raise
    
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate text using Together AI API."""
        try:
            response = self.client.completions.create(
                model=self.model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.timeout
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"Together AI API error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check Together AI availability."""
        try:
            self.client.completions.create(
                model=self.model,
                prompt="test",
                max_tokens=1,
                timeout=5
            )
            return True
        except Exception as e:
            logger.warning(f"Together AI provider unavailable: {e}")
            return False


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider - Use as fallback when others are unavailable."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        if not api_key or api_key == "your-api-key":
            raise ValueError("OpenAI API key not configured")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            logger.error("openai library not installed. Install with: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate text using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.timeout
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check OpenAI availability."""
        try:
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
                timeout=5
            )
            return True
        except Exception as e:
            logger.warning(f"OpenAI provider unavailable: {e}")
            return False


class LLMProviderManager:
    """
    Manages multiple LLM providers with automatic fallback.
    Tries providers in priority order and falls back on failure.
    """
    
    # Default provider priority order
    DEFAULT_PROVIDER_ORDER = [
        LLMProvider.GROQ,
        LLMProvider.TOGETHER,
        LLMProvider.HUGGINGFACE,
        LLMProvider.OPENAI,
    ]
    
    def __init__(self, api_keys: Dict[str, str], provider_order: Optional[List[LLMProvider]] = None):
        """
        Initialize provider manager.
        
        Args:
            api_keys: Dictionary with keys like 'groq', 'openai', 'huggingface', 'together'
            provider_order: List of providers to try in order (default: DEFAULT_PROVIDER_ORDER)
        """
        self.api_keys = api_keys
        self.provider_order = provider_order or self.DEFAULT_PROVIDER_ORDER
        self.providers: Dict[LLMProvider, BaseLLMProvider] = {}
        self.current_provider: Optional[LLMProvider] = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers."""
        provider_classes = {
            LLMProvider.GROQ: GroqProvider,
            LLMProvider.HUGGINGFACE: HuggingFaceProvider,
            LLMProvider.TOGETHER: TogetherAIProvider,
            LLMProvider.OPENAI: OpenAIProvider,
        }
        
        for provider_type, provider_class in provider_classes.items():
            api_key = self.api_keys.get(provider_type.value)
            if not api_key:
                logger.debug(f"Skipping {provider_type.value} - API key not provided")
                continue
            
            try:
                self.providers[provider_type] = provider_class(api_key)
                logger.info(f"Initialized {provider_type.value} provider")
            except Exception as e:
                logger.warning(f"Failed to initialize {provider_type.value}: {e}")
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        retry_failed: bool = True
    ) -> str:
        """
        Generate text with automatic fallback.
        
        Args:
            prompt: Text prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation
            retry_failed: If True, try other providers on failure
        
        Returns:
            Generated text
        
        Raises:
            Exception: If all providers fail
        """
        # Try primary provider first
        if self.current_provider and self.current_provider in self.providers:
            try:
                logger.info(f"Using {self.current_provider.value} provider")
                result = self.providers[self.current_provider].generate_text(
                    prompt, max_tokens, temperature
                )
                return result
            except Exception as e:
                logger.warning(f"{self.current_provider.value} failed: {e}")
                if not retry_failed:
                    raise
        
        # Fallback to provider priority order
        for provider_type in self.provider_order:
            if provider_type not in self.providers:
                logger.debug(f"Skipping {provider_type.value} - not initialized")
                continue
            
            try:
                logger.info(f"Falling back to {provider_type.value} provider")
                result = self.providers[provider_type].generate_text(
                    prompt, max_tokens, temperature
                )
                self.current_provider = provider_type  # Update current provider
                logger.info(f"Successfully used {provider_type.value} provider")
                return result
            except Exception as e:
                logger.warning(f"{provider_type.value} failed: {e}")
                continue
        
        raise Exception(
            f"All LLM providers failed. Available: {list(self.providers.keys())}"
        )
    
    def set_provider(self, provider: LLMProvider) -> bool:
        """
        Set the primary provider to use.
        
        Args:
            provider: Provider to use
        
        Returns:
            True if provider is available, False otherwise
        """
        if provider not in self.providers:
            logger.error(f"Provider {provider.value} not available")
            return False
        
        self.current_provider = provider
        logger.info(f"Primary provider set to {provider.value}")
        return True
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [p.value for p in self.providers.keys()]
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all providers."""
        health = {}
        for provider_type, provider in self.providers.items():
            try:
                health[provider_type.value] = provider.is_available()
            except Exception as e:
                logger.warning(f"Health check failed for {provider_type.value}: {e}")
                health[provider_type.value] = False
        return health
