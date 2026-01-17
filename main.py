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
        print("DATABASE BOOT: OK")
    except Exception as e:
        print(f"DATABASE BOOT ERROR: {str(e)}")

init_db()

from sqlalchemy.orm import Session
from fastapi import Depends
from database import SessionLocal
import security
from fastapi.security import OAuth2PasswordBearer

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
        raise HTTPException(status_code=404,detail="not with correct jwt token")
    user=db.query(models.UserDB).filter(models.UserDB.email==username).first()
    if user is None:
        raise HTTPException(status_code=401,detail="user not found")
    return user

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.middleware("http")
async def get_call_time_seconds(request:Request,call_next):
    start_time=time.time()
    response=await call_next(request)
    process_time=time.time()-start_time
    response.headers["X-process-time"]=str(process_time)
    return response

# ==================== JOBS ====================
@app.get("/jobs")
def get_jobs(db:Session =Depends(get_db)):
    return db.query(models.JobDB).all()

@app.get("/jobs/{job_id}")
def get_job_by_id(job_id:int,db:Session=Depends(get_db)):
    job_to_get=db.query(models.JobDB).filter(models.JobDB.id==job_id).first()
    if job_to_get is None:
        raise HTTPException(status_code=404,detail="job not found")
    return job_to_get

class Job(BaseModel):
    title: str
    location: str
    salary: int
    description: Optional[str] = None

@app.post("/jobs")
def create_job(job: Job, db: Session = Depends(get_db)):
    try:
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
        print(f"JOB CREATE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@app.post("/jobs/{job_id}/apply")
async def apply_for_job(job_id: int, db: Session = Depends(get_db), current_user: models.UserDB = Depends(get_current_user)):
    job = db.query(models.JobDB).filter(models.JobDB.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Application sent successfully."}

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
    return{"message":"job is updated"}

# ==================== USERS ====================
class UserCreate(BaseModel):
    email:EmailStr
    username:str
    password:str

@app.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_email = db.query(models.UserDB).filter(models.UserDB.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered.")
        
        existing_username = db.query(models.UserDB).filter(models.UserDB.username == user.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken.")

        new_user = models.UserDB(
            email=user.email,
            username=user.username,
            hashed_password=security.get_password_hash(user.password)
        )
        db.add(new_user)
        db.commit()
        return {"message": "User created successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        print(f"USER CREATE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
def for_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.UserDB).filter(
        (models.UserDB.email == form_data.username) | (models.UserDB.username == form_data.username)
    ).first()
    
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not security.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    token = security.create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def view_profile(current_user:models.UserDB=Depends(get_current_user)):
    return{"email":current_user.email,"username":current_user.username,"id":current_user.id}

@app.get("/community")
def get_community(db:Session=Depends(get_db)):
    users = db.query(models.UserDB).all()
    return [{"id": u.id, "username": u.username or "Anonymous"} for u in users]

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

# ==================== AI DISABLED ====================
# AI salary prediction endpoints are temporarily disabled
# to reduce memory usage on free hosting tier.

@app.post("/predict_salary")
def predict_salary():
    return {"error": "AI salary prediction is temporarily disabled", "message": "This feature will be available soon."}

@app.post("/predict_salary_batch")
def predict_salary_batch():
    return {"error": "AI batch prediction is temporarily disabled"}

# ==================== FRONTEND ====================
from fastapi.responses import FileResponse

@app.get("/")
def read_root():
    return FileResponse("static/index.html")
