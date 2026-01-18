import os
from .providers.disabled import DisabledAIProvider
from .providers.groq_provider import GroqAIProvider

class AIServiceFactory:
    @staticmethod
    def get_service():
        provider_type = os.getenv("AI_PROVIDER", "disabled").lower()
        
        if provider_type == "groq":
            return GroqAIProvider()
        return DisabledAIProvider()
