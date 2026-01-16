import pandas as pd
import numpy as np

np.random.seed(42)

# RESTRICTED categories
titles = ['Software Engineer', 'Data Scientist', 'Product Manager', 'DevOps', 'Designer', 'QA Engineer', 'Sales', 'HR']
seniorities = ['Junior', 'Mid', 'Senior', 'Lead', 'Principal']
locations = ['New York', 'SF', 'Remote', 'London', 'India', 'Germany']
tech_stacks = ['Python', 'Java', 'Javascript', 'Go', 'Rust', 'C++']
company_sizes = ['Startup', 'Mid-Size', 'Big Tech']

n = 2000
data = {
    'title': np.random.choice(titles, n),
    'seniority': np.random.choice(seniorities, n),
    'location': np.random.choice(locations, n),
    'tech_stack': np.random.choice(tech_stacks, n),
    'company_size': np.random.choice(company_sizes, n),
    'years_experience': np.random.randint(0, 26, n)
}

df = pd.DataFrame(data)

# Base salaries by seniority
seniority_base = {
    'Junior': 60000,
    'Mid': 90000,
    'Senior': 130000,
    'Lead': 170000,
    'Principal': 240000
}

# Location multipliers
location_mult = {
    'SF': 1.4,
    'New York': 1.3,
    'Remote': 1.0,
    'London': 0.95,
    'Germany': 0.85,
    'India': 0.25
}

# Tech stack premium
tech_premium = {
    'Rust': 1.15,
    'Go': 1.15,
    'C++': 1.05,
    'Python': 1.0,
    'Java': 1.0,
    'Javascript': 1.0
}

# Company size multipliers
company_mult = {
    'Big Tech': 1.35,
    'Mid-Size': 1.0,
    'Startup': 0.75
}

# Title multipliers (Sales/HR typically lower than engineering)
title_mult = {
    'Software Engineer': 1.0,
    'Data Scientist': 1.05,
    'Product Manager': 1.1,
    'DevOps': 1.05,
    'Designer': 0.9,
    'QA Engineer': 0.85,
    'Sales': 0.95,
    'HR': 0.8
}

salaries = []
for idx, row in df.iterrows():
    base = seniority_base[row['seniority']]
    
    salary = base * location_mult[row['location']]
    salary *= tech_premium[row['tech_stack']]
    salary *= company_mult[row['company_size']]
    salary *= title_mult[row['title']]
    
    # Years experience bonus (3% per year, capped)
    exp_bonus = min(row['years_experience'] * 0.03, 0.4)
    salary *= (1 + exp_bonus)
    
    # 5% noise
    noise = np.random.normal(0, 0.05)
    salary *= (1 + noise)
    
    salary = max(salary, 8000)  # Floor
    salaries.append(round(salary, 2))

df['salary'] = salaries

df.to_csv('salary_data.csv', index=False)

print(f"Generated {len(df)} rows")
print(f"\nSample data:")
print(df.head(10))
print(f"\nSalary range: ${df['salary'].min():,.0f} - ${df['salary'].max():,.0f}")
print(f"Mean: ${df['salary'].mean():,.0f}")

# Validate the anchor points
principal_bigtech_sf = df[(df['seniority'] == 'Principal') & 
                          (df['company_size'] == 'Big Tech') & 
                          (df['location'] == 'SF')]
junior_startup_india = df[(df['seniority'] == 'Junior') & 
                          (df['company_size'] == 'Startup') & 
                          (df['location'] == 'India')]

print(f"\nPrincipal @ Big Tech in SF (sample): ${principal_bigtech_sf['salary'].mean():,.0f}")
print(f"Junior @ Startup in India (sample): ${junior_startup_india['salary'].mean():,.0f}")