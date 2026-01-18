from abc import ABC, abstractmethod

class AIService(ABC):
    @abstractmethod
    def predict_salary(self, input_data) -> dict:
        """
        Abstract method to predict salary based on input data.
        Returns a dictionary containing the prediction results.
        """
        pass
