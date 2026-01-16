import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# 1. Load Data from CSV
try:
    df = pd.read_csv("salary_data.csv")
except FileNotFoundError:
    print("❌ Error: 'salary_data.csv' not found. Run generate_data.py first.")
    exit()

print(df)
# ... (your existing pandas code)

# 3. Import Skills
# OneHotEncoder: Converts text ("New York") into numbers (1, 0, 0)
# LinearRegression: The math formula that draws the line
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
import joblib 

# 4. Define the Brain
# "Take the 'title' and 'location', turn them into numbers, then predict."
model = Pipeline(steps=[
    ('preprocessor', ColumnTransformer(
        transformers=[
            ('text_columns', OneHotEncoder(handle_unknown='ignore'), ['title', 'seniority', 'location', 'tech_stack', 'company_size'])
        ], 
        remainder='passthrough' # Keep 'years_experience' as is (it's already a number)
    )),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

# 5. Train the Brain (The "Aha!" Moment)
# X = Inputs (Title, Location, Experience)
# y = Output (Salary)
X = df[['title', 'seniority', 'location', 'tech_stack', 'company_size', 'years_experience']]
y = df['salary']

print("Training Model...")
model.fit(X, y)
print("✅ Model Trained!")

# 6. Save the Brain to a file (so we can use it in main.py)
joblib.dump(model, 'salary_model.pkl')
print("✅ Model Saved to salary_model.pkl")