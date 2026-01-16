from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_predict_salary_robustness():
    # Test the "Mars" scenario automatically
    response = client.post("/predict_salary", json={
        "title": "Software Engineer", 
        "location": "Mars", 
        "years_of_experience": 0
    })
    
    # Assertions (The "Grading" Logic)
    assert response.status_code == 200
    assert "estimated_salary" in response.json()
    print("✅ Mars Test Passed!")
    