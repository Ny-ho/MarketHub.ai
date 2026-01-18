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
            if 'jobs' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('jobs')]
                if 'description' not in cols:
                    conn.execute(text("ALTER TABLE jobs ADD COLUMN description TEXT"))
                    conn.commit()
            if 'users' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('users')]
                if 'username' not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN username TEXT"))
                    conn.commit()
        print("DATABASE: OK")
    except Exception as e:
        print(f"DATABASE ERROR: {str(e)}")

init_db()

from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal
import security
from fastapi.security import OAuth2PasswordBearer
import joblib
import pandas as pd

# AI Model Loading (Lazy)
_classifier = None
_model = None

KNOWN_TITLES = ["Software Engineer", "Data Scientist", "Product Manager", "DevOps", "Designer", "QA Engineer", "Sales", "HR"]

def get_classifier():
    global _classifier
    if _classifier is None:
        print("Loading AI model (first request)...")
        from transformers import pipeline
        _classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")
        print("AI model loaded.")
    return _classifier

def get_salary_model():
    global _model
    if _model is None:
        _model = joblib.load("salary_model.pkl")
    return _model

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
        raise HTTPException(status_code=404,detail="Invalid token")
    user=db.query(models.UserDB).filter(models.UserDB.email==username).first()
    if user is None:
        raise HTTPException(status_code=401,detail="User not found")
    return user

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.middleware("http")
async def get_call_time_seconds(request:Request,call_next):
    start_time=time.time()
    response=await call_next(request)
    response.headers["X-process-time"]=str(time.time()-start_time)
    return response

# ==================== JOBS ====================
@app.get("/jobs")
def get_jobs(db:Session=Depends(get_db)):
    return db.query(models.JobDB).all()

@app.get("/jobs/{job_id}")
def get_job_by_id(job_id:int,db:Session=Depends(get_db)):
    job=db.query(models.JobDB).filter(models.JobDB.id==job_id).first()
    if job is None:
        raise HTTPException(status_code=404,detail="Job not found")
    return job

class Job(BaseModel):
    title: str
    location: str
    salary: int
    description: Optional[str] = None

@app.post("/jobs")
def create_job(job: Job, db: Session = Depends(get_db)):
    new_job = models.JobDB(title=job.title,location=job.location,salary=job.salary,description=job.description)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@app.post("/jobs/{job_id}/apply")
async def apply_for_job(job_id: int, db: Session = Depends(get_db), current_user: models.UserDB = Depends(get_current_user)):
    job = db.query(models.JobDB).filter(models.JobDB.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Application sent."}

@app.delete("/jobs/{job_id}")
def delete_job(job_id:int, db:Session=Depends(get_db)):
    job=db.query(models.JobDB).filter(models.JobDB.id==job_id).first()
    if job is None:
        raise HTTPException(status_code=404,detail="Job not found")
    db.delete(job)
    db.commit()
    return{"message":"Job deleted"}

@app.put("/jobs/{job_id}")
def update_job(job_id:int,job_update:Job,db:Session=Depends(get_db)):
    job=db.query(models.JobDB).filter(models.JobDB.id==job_id).first()
    if job is None:
        raise HTTPException(status_code=404,detail="Job not found")
    job.title=job_update.title
    job.location=job_update.location
    job.salary=job_update.salary
    db.commit()
    return{"message":"Job updated"}

# ==================== USERS ====================
class UserCreate(BaseModel):
    email:EmailStr
    username:str
    password:str

@app.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.UserDB).filter(models.UserDB.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email exists")
    if db.query(models.UserDB).filter(models.UserDB.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username exists")
    new_user = models.UserDB(email=user.email,username=user.username,hashed_password=security.get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
def for_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.UserDB).filter((models.UserDB.email == form_data.username) | (models.UserDB.username == form_data.username)).first()
    if db_user is None or not security.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = security.create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def view_profile(current_user:models.UserDB=Depends(get_current_user)):
    return{"email":current_user.email,"username":current_user.username,"id":current_user.id}

@app.get("/community")
def get_community(db:Session=Depends(get_db)):
    return [{"id": u.id, "username": u.username or "Anonymous"} for u in db.query(models.UserDB).all()]

# ==================== TODOS ====================
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
    new_todo=models.TodoDB(task=todo.task,owner_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.get("/todos")
def get_my_todos(db:Session=Depends(get_db),current_user:models.UserDB=Depends(get_current_user)):
    return db.query(models.TodoDB).filter(models.TodoDB.owner_id==current_user.id).all()

# ==================== AI SALARY PREDICTION ====================
class salary_input(BaseModel):
    title: str
    location: str
    years_of_experience: int
    tech_stack: str
    seniority: str
    company_size: str

@app.post("/predict_salary")
def predict_salary(input_data: salary_input):
    classifier = get_classifier()
    result = classifier(input_data.title, KNOWN_TITLES)
    cleaned_title = result['labels'][0]
    match_score = result['scores'][0]
    
    if match_score > 0.8: confidence = "High"
    elif match_score > 0.5: confidence = "Medium"
    else: confidence = "Low"
    
    df = pd.DataFrame({
        "title": [cleaned_title],
        "location": [input_data.location],
        "years_experience": [input_data.years_of_experience],
        "tech_stack": [input_data.tech_stack],
        "seniority": [input_data.seniority],
        "company_size": [input_data.company_size]
    })
    base_prediction = int(get_salary_model().predict(df)[0])
    
    return {
        "prediction": {
            "average": base_prediction,
            "range": f"${int(base_prediction*0.9):,} - ${int(base_prediction*1.1):,}",
            "confidence_level": confidence,
            "match_accuracy": f"{match_score:.2%}"
        },
        "metadata": {"cleaned_title": cleaned_title}
    }

@app.post("/predict_salary_batch")
def predict_salary_batch(inputs:List[salary_input]):
    data=[item.dict()for item in inputs]
    df=pd.DataFrame(data)
    df=df.rename(columns={"years_of_experience":"years_experience"})
    predictions=get_salary_model().predict(df)
    return{"estimated_salaries":predictions.tolist()}

# ==================== FRONTEND ====================
from fastapi.responses import FileResponse

@app.get("/")
def read_root():
    return FileResponse("static/index.html")
