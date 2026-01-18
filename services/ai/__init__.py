from .factory import AIServiceFactory

def predict_salary(input_data) -> dict:
    """
    Main entry point for AI salary prediction.
    Instantiates the service on-demand (lazy loading).
    """
    service = AIServiceFactory.get_service()
    return service.predict_salary(input_data)
