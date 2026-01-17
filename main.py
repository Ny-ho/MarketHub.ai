from fastapi import FastAPI,HTTPException
from typing import Optional,List
from pydantic import BaseModel,EmailStr
import time
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from database import engine
import models
models.Base.metadata.create_all(bind=engine)
# Database Schema Initialization
def init_db():
    try:
        models.Base.metadata.create_all(bind=engine)
        from sqlalchemy import text, inspect
        inspector = inspect(engine)
        with engine.connect() as conn:
            # FORCE ADD 'description' if it was missed in earlier deploys
            if 'jobs' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('jobs')]
                if 'description' not in cols:
                    conn.execute(text("ALTER TABLE jobs ADD COLUMN description TEXT"))
                    conn.commit()
            # FORCE ADD 'username' to 'users'
            if 'users' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('users')]
                if 'username' not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN username TEXT"))
                    conn.commit()
        print("DATABASE BOOT: Registry Synchronized and Self-Healed.")
    except Exception as e:
        print(f"DATABASE BOOT ERROR: {str(e)}")

init_db()
from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal
import security
from fastapi.security import OAuth2PasswordBearer
import joblib
import pandas as pd

# NOTE: transformers is imported lazily inside get_classifier() to avoid startup memory usage

# Known Valid Titles (Must match your CSV)
KNOWN_TITLES = ["Software Engineer", "Data Scientist", "Product Manager", "DevOps", "Designer", "QA Engineer", "Sales", "HR"]

import gc

# AI Models (Lazy Loaded with Lite Fallback)
_classifier = None
_model = None

def get_classifier():
    global _classifier
    if _classifier is None:
        try:
            print("LOADING AI MODEL (first request only)...")
            from transformers import pipeline  # Lazy import - only loads when needed
            _classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")
            gc.collect()
            print("AI MODEL LOADED SUCCESSFULLY")
        except Exception as e:
            print(f"AI MODEL UNAVAILABLE: {str(e)}")
            _classifier = None  # Will use lite fallback
    return _classifier

def get_salary_model():
    global _model
    if _model is None:
        try:
            _model = joblib.load("salary_model.pkl")
        except Exception:
            # Fallback will be handled in the endpoint
            pass
    return _model

def lite_ai_classifier(title, candidates):
    """Zero-RAM Fallback: Basic keyword matcher"""
    title_lower = title.lower()
    for candidate in candidates:
        if candidate.lower() in title_lower:
            return {'labels': [candidate], 'scores': [0.99]}
    return {'labels': [candidates[0]], 'scores': [0.45]}

def lite_salary_predictor(title):
    """Zero-RAM Fallback: Market averages"""
    averages = {
        "Software Engineer": 115000,
        "Data Scientist": 125000,
        "Product Manager": 130000,
        "DevOps": 120000,
        "Designer": 95000,
        "QA Engineer": 85000,
        "Sales": 75000,
        "HR": 70000
    }
    return averages.get(title, 90000)
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    username=security.decode_access_token(token)
    if username is None:
        raise HTTPException(status_code=404,detail="not with coorect jwt token")
    user=db.query(models.UserDB).filter(models.UserDB.email==username).first()
    if user is None:
        raise HTTPException(status_code=401,detail="user not found")
    return user

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
#just a middlware for calculating time taken of a function
@app.middleware("http")
async def get_call_time_seconds(request:Request,call_next):
    start_time=time.time()
    response=await call_next(request)
    process_time=time.time()-start_time
    response.headers["X-process-time"]=str(process_time)
    return response

#just to read the jobs available only read
@app.get("/jobs")
def get_jobs(db:Session =Depends(get_db)):
    return db.query(models.JobDB).all()
#get job only by id no need to search anything more if u have id
@app.get("/jobs/{job_id}")
def get_job_by_id(job_id:int,db:Session=Depends(get_db)):
    job_to_get=db.query(models.JobDB).filter(models.JobDB.id==job_id).first()
    if job_to_get is None:
        
        raise HTTPException(status_code=404,detail="job not found 404 status given")
    return job_to_get
# Pydantic models for Job signals
class Job(BaseModel):
    title: str
    location: str
    salary: int
    description: Optional[str] = None
@app.post("/jobs")
def create_job(job: Job, db: Session = Depends(get_db)):
    try:
        # Standard DB insertion (ID is auto-generated)
        new_job = models.JobDB(
            title=job.title,
            location=job.location,
            salary=job.salary,
            description=job.description
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job
    except Exception as e:
        db.rollback()
        print(f"JOB DEPLOYMENT FAILED: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market Signal Failure: {str(e)}")
#now to apply our resume or give information to jobs company
class Applicant(BaseModel):
    name:str
    position:str
    location:str
    projects_done:str
@app.post("/jobs/{job_id}/apply")
async def apply_for_job(job_id: int, db: Session = Depends(get_db), current_user: models.UserDB = Depends(get_current_user)):
    job = db.query(models.JobDB).filter(models.JobDB.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    print(f"User {current_user.email} applying for job {job.title}")
    return {"message": "Application signal sent successfully."}

@app.delete("/jobs/{job_id}")
def delete_job(job_id:int, db:Session=Depends(get_db)):
    job_to_delete=db.query(models.JobDB).filter(models.JobDB.id==job_id).first()
    if job_to_delete is None:
        raise HTTPException(status_code=404,detail="job not found")
    db.delete(job_to_delete)
    db.commit()
    return{"message":"job is deleted"}

@app.put("/jobs/{job_id}")
def update_job(job_id:int,job_update:Job,db:Session=Depends(get_db)):
    job_to_update=db.query(models.JobDB).filter(models.JobDB.id==job_id).first()
    if job_to_update is None:
        raise HTTPException(status_code=404,detail="job not found")
    job_to_update.title=job_update.title
    job_to_update.location=job_update.location
    job_to_update.salary=job_update.salary
    db.commit()
    return{"message":"job is upadted"}

#password hashing (making password gibbrish)
class UserCreate(BaseModel):
    email:EmailStr
    username:str
    password:str
@app.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # 1. Check if email already exists
        existing_email = db.query(models.UserDB).filter(models.UserDB.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Identity Signal already registered with this email.")
        
        # 2. Check if username already exists
        existing_username = db.query(models.UserDB).filter(models.UserDB.username == user.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Agent Identity already taken.")

        # 3. Create the user
        new_user = models.UserDB(
            email=user.email,
            username=user.username,
            hashed_password=security.get_password_hash(user.password)
        )
        db.add(new_user)
        db.commit()
        return {"message": "Agent Signal Initialized."}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        # Log the error and return a detailed message
        print(f"CRITICAL REGISTRY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Core Registry Error: {str(e)}")

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
def for_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Check both email AND username so agents can use either to log in
    db_user = db.query(models.UserDB).filter(
        (models.UserDB.email == form_data.username) | (models.UserDB.username == form_data.username)
    ).first()
    
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid Signal ID (Email or Agent Name)")
    if not security.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Secret Cipher")
    
    # Always use email as the token subject for consistency in auth guards
    token = security.create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def view_profile(current_user:models.UserDB=Depends(get_current_user)):
    return{"email":current_user.email,"username":current_user.username,"id":current_user.id}

@app.get("/community")
def get_community(db:Session=Depends(get_db)):
    users = db.query(models.UserDB).all()
    return [{"id": u.id, "username": u.username or "Anonymous Agent"} for u in users]

class todocreate(BaseModel):
    task:str
class todoresponse(BaseModel):
    id:int
    task:str
    is_done:bool
    owner_id:int
    
    class Config:
        from_attributes=True
@app.post("/todos",response_model=todoresponse)
def create_todo(todo:todocreate,db:Session=Depends(get_db),current_user:models.UserDB=Depends(get_current_user)):
    new_todo=models.TodoDB(
        task=todo.task,
        owner_id=current_user.id
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo
@app.get("/todos")
def get_my_todos(db:Session=Depends(get_db),current_user:models.UserDB=Depends(get_current_user)):
    return db.query(models.TodoDB).filter(models.TodoDB.owner_id==current_user.id).all()

class salary_input(BaseModel):
    title: str
    location: str
    years_of_experience: int
    tech_stack: str      
    seniority: str       
    company_size: str    
@app.post("/predict_salary")
def predict_salary(input_data: salary_input):
    try:
        # 1. AI Cleaning (Smart Fallback)
        classifier = get_classifier()
        if classifier:
            result = classifier(input_data.title, KNOWN_TITLES)
            mode = "PREMIUM BRAIN"
        else:
            result = lite_ai_classifier(input_data.title, KNOWN_TITLES)
            mode = "LITE HEURISTIC (RAM SAVE)"
            
        cleaned_title = result['labels'][0]
        match_score = result['scores'][0]

        # 2. Confidence Logic
        if match_score > 0.8: confidence = "High"
        elif match_score > 0.5: confidence = "Medium"
        else: confidence = "Low"

        # 3. Predict Base Number
        model = get_salary_model()
        if model:
            df = pd.DataFrame({
                "title": [cleaned_title],
                "location": [input_data.location],
                "years_experience": [input_data.years_of_experience],
                "tech_stack": [input_data.tech_stack],
                "seniority": [input_data.seniority],
                "company_size": [input_data.company_size]
            })
            base_prediction = int(model.predict(df)[0])
        else:
            base_prediction = lite_salary_predictor(cleaned_title)

        # 4. Range Logic
        low_range = int(base_prediction * 0.9)
        high_range = int(base_prediction * 1.1)

        return {
            "prediction": {
                "average": base_prediction,
                "range": f"${low_range:,} - ${high_range:,}",
                "confidence_level": confidence,
                "match_accuracy": f"{match_score:.2%}"
            },
            "metadata": {
                "cleaned_title": cleaned_title,
                "mode": mode,
                "disclaimer": "Market Intelligence Sync: Successful."
            }
        }
    except Exception as e:
        print(f"SALARY PREDICTION ERROR: {str(e)}")
        return {
            "error": "Salary prediction temporarily unavailable",
            "message": "The AI model could not be loaded on this server. Please try again later.",
            "fallback": {"average": 100000, "range": "$90,000 - $110,000"}
        }
@app.post("/predict_salary_batch")
def predict_salary_batch(inputs:List[salary_input]):
    model = get_salary_model()
    if model is None:
        return {"error": "Batch salary prediction temporarily unavailable"}
    data=[item.dict()for item in inputs]
    df=pd.DataFrame(data)
    df=df.rename(columns={"years_of_experience":"years_experience"})
    predictions=model.predict(df)
    return{"estimated_salaries":predictions.tolist()}

#to directly show frontend in localhost 8000
from fastapi.responses import FileResponse

@app.get("/")
def read_root():
    return FileResponse("static/index.html") 
