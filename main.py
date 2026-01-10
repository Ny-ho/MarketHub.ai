from fastapi import FastAPI,HTTPException
from typing import Optional
from pydantic import BaseModel
import time
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from database import engine
import models
models.Base.metadata.create_all(bind=engine)
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
#to create or leave a job for applicants
class Job(BaseModel):
    id:int
    title:str
    location:str
    salary:int
@app.post("/jobs")
def create_job(job:Job,db: Session =Depends(get_db)):
   new_job=models.JobDB(
       title=job.title,
       location=job.location,
       salary=job.salary
   )
   db.add(new_job)
   db.commit()
   db.refresh(new_job)
   return new_job
#now to apply our resume or give information to jobs company
class Applicant(BaseModel):
    name:str
    position:str
    location:str
    projects_done:str
@app.post("/jobs/{job_id}/apply")
def apply_for_job(job_id:int,db:Session=Depends(get_db)):
    applying_for_job=db.query(models.JobDB).filter(models.JobDB.id==job_id).first()
    if applying_for_job is None:
            raise HTTPException(status_code=404,details="job dont exist")
    return applying_for_job

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
    username:str
    password:str
@app.post("/users")
def create_user(user:UserCreate,db:Session=Depends(get_db)):
    hashed_pwd=security.get_password_hash(user.password)
    new_user=models.UserDB(
        username=user.username,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    return{"message":"success"}

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
def for_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.UserDB).filter(models.UserDB.username == form_data.username).first()
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid username")
    if not security.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    token = security.create_access_token(data={"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")
@app.get("/me")
def to_check_token(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    username=security.decode_access_token(token)
    if username is None:
        raise HTTPException(status_code=404,detail="not with coorect jwt token")
    user=db.query(models.UserDB).filter(models.UserDB.username==username).first()
    return{"username of you":user.username,"id":user.id}
