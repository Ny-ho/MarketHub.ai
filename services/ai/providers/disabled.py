from ..base import AIService

class DisabledAIProvider(AIService):
    def predict_salary(self, input_data) -> dict:
        return {
            "error": "AI service is disabled in production",
            "message": "The AI salary prediction module is currently inactive. Please enable it via environmental parameters to resume predictive telemetry.",
            "fallback": {"average": 100000, "range": "$90,000 - $110,000"}
        }
