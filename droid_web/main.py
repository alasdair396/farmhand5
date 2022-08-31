#source env/bin/activate
#uvicorn main:app --reload --port 5000 --host 0.0.0.0
# to install fastapi on docker container https://www.youtube.com/watch?v=2a5414BsYqw - fast, basic video....
#to set local timezone on Ubuntu:sudo dpkg-reconfigure tzdata
import datetime
from datetime import datetime, timedelta, timezone, date
import time
import psycopg2

from time import timezone
from time import strftime, timezone
from fastapi import FastAPI, Query, Request, Depends, status, Form, Response, Path, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_400_BAD_REQUEST
from db import SessionLocal, engine, DBContext
import models, crud, schemas
from sqlalchemy.orm import Session
from fastapi_login import LoginManager
from dotenv import load_dotenv #pip3 install python-dotenv
import os
from passlib.context import CryptContext
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
import sqlite3
import json
import uuid


#connection = sqlite3.connect('droid.db',check_same_thread=False)
#connection = psycopg2.connect( database="exampledb", user="docker", password="docker", host="0.0.0.0")
connection = psycopg2.connect( database="droid", user="droid", password="r2d2droid", host="0.0.0.0")



# To modify database:
#alembic revision --autogenerate -m "changed this..."
#

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DROID_ID = os.getenv('DROID_ID')
ACCESS_TOKEN_EXPIRE_MINUTES=60

manager = LoginManager(SECRET_KEY, token_url="/login", use_cookie=True)
manager.cookie_name = "auth"

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    with DBContext() as db:
        yield db

def get_hashed_password(plain_password):
    return pwd_ctx.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_ctx.verify(plain_password,hashed_password)

@manager.user_loader()
def get_user(username: str, db: Session = None):
    if db is None:
        with DBContext() as db:
            return crud.get_user_by_username(db=db,username=username)
    return crud.get_user_by_username(db=db,username=username)

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db=db,username=username)
    if not user:
        return None
    if not verify_password(plain_password=password,hashed_password=user.hashed_password):
        return None
    return user

class NotAuthenticatedException(Exception):
    pass

def not_authenticated_exception_handler(request, exception):
    return RedirectResponse("/login")

manager.not_authenticated_exception = NotAuthenticatedException
app.add_exception_handler(NotAuthenticatedException, not_authenticated_exception_handler)

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Home"})

@app.get("/droid_list")
def get_droids_all(request: Request, db: Session = Depends(get_db), droid: schemas.Droid = Depends(manager)):
    droid_model= crud.get_droids_all(db=db)
    print(droid_model)
    return templates.TemplateResponse("/droid_list.html", {"request": request, "title": "Droids", "droid_model": droid_model})

@app.get("/droid_edit", response_class=HTMLResponse)
def do_droid_edit(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager),id: str = Query(...)):
    print(jsonable_encoder(crud.get_droid(db=db,id=id)))
    param =(crud.get_droid(db=db,id=id))
    if not param:
            return templates.TemplateResponse("droid_search.html", {"request": request, "id": id, "parameter": param, "title": "Edit droid parameters"}, status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse("droid_edit.html", {"request": request, "id": id, "parameter": param, "title": "Edit droid parameters"})

@app.get("/droid_add")
def get_register(request: Request):
    return templates.TemplateResponse("droid_add.html", {"request": request, "title": "Register"})

@app.post("/droid_save")
def do_droid_save(request: Request,
droid_name: str = Form(...),
droid_id: str = Form(...),
droid_description: str = Form(...),
feed_density: float = Form(...),
droid_server: str = Form(...),
command_set: str = Form(...),
db: Session = Depends(get_db)):
    invalid = False
    if crud.droid_by_droid_id_get(db=db,droid_id=droid_id):
        invalid = True
    if not invalid:
        crud.droid_save(db=db,
        droid_name=droid_name,
        droid_id=droid_id,
        droid_description=droid_description,
        feed_density=feed_density,
        droid_server=droid_server,
        command_set=command_set)
        response = RedirectResponse("/droid_list", status_code=status.HTTP_302_FOUND)
        return response
    else:
        return templates.TemplateResponse("droid_add.html",{"request": request, "title": "Register", "invalid": True},
        status_code=HTTP_400_BAD_REQUEST)

@app.post("/droid_parameters/{id}")
def update_parameters(request: Request,
    id: str,
    droid_name: Optional[str] = Form(None),
    droid_id: Optional[str] = Form(None),
    droid_description: Optional[str] = Form(None),
    feed_density: Optional[float] = Form(None),
    droid_server: Optional[str] = Form(None),
    command_set: Optional[str] = Form(None),
    user: schemas.User = Depends(manager),
    db: Session = Depends(get_db)
    ):
    sql_statement = crud.update_droid_sql(id,droid_name,droid_id,droid_description, feed_density, droid_server,command_set)
    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    connection.commit()
    return RedirectResponse(url="/droid_list", status_code=302)

@app.post("/tasks")
def add_task(request: Request,
    text: str = Form(...),
    complete: int = Form(...),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(manager)
    ):
    print("Got here 1")
    print(str(complete))
    added = crud.add_task(db=db,task=schemas.TaskCreate(text=text),complete=complete, id=user.id)
    print("Got here 2")
    if not added:
        return templates.TemplateResponse("tasks.html", {"request": request,
        "title": "Tasks",
        "user": user,
        "tasks": crud.get_tasks_by_user_id(db=db,id=user.id),
        "invalid": True}, status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return RedirectResponse("/tasks", status_code=status.HTTP_302_FOUND)

@app.get("/tasks")
def get_tasks(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    return templates.TemplateResponse("tasks.html", {"request": request, 
    "title": "Tasks", 
    "user": user, 
    "tasks": crud.get_tasks_by_user_id(db=db,id=user.id)})

@app.get("/tasks_test")
def get_tasks(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    task_html_data = db.query(models.Task).filter(models.Task.user_id == user.id).all()
    print(task_html_data)
    return templates.TemplateResponse("tasks.html", {"request": request, "title": "Tasks", "user": user,"tasks": task_html_data})

@app.get("/task_edit/{id}", response_class=HTMLResponse)
def do_task_edit(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager),id: str = Query(...)):
    print(jsonable_encoder(crud.get_task_by_id(db=db,id=id)))
    param =(crud.get_task_by_id(db=db,id=id))
    if not param:
            return templates.TemplateResponse("droid_search.html", {"request": request, "id": id, "parameter": param, "title": "Edit droid parameters"}, status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse("task_edit.html", {"request": request, "id": id, "parameter": param, "title": "Edit task details"})

@app.post("/task_update/{id}")
def do_task_update(request: Request,
id: str,
text: str = Form(...),
complete: int = Form(...),
db: Session = Depends(get_db)
):
    print("Hello")
    sql_statement = crud.task_update(id=id,text=text,complete=complete)
    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    connection.commit()
    return RedirectResponse(url="/tasks", status_code=302)

@app.get("/task/delete/{id}",response_class=RedirectResponse)
def delete_task(id: str = Path(...), db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    crud.delete_task(db=db,id=id)
    return RedirectResponse("/tasks")

@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@app.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(username=form_data.username,password=form_data.password,db=db)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request,
        "title": "Login",
        "invalid": True}, status_code=status.HTTP_401_UNAUTHORIZED)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = manager.create_access_token(
        data={"sub": user.username},
        expires=access_token_expires
    )
    resp = RedirectResponse("/tasks", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp,access_token)
    return resp

@app.get("/register")
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Register"})

@app.post("/register")
def register(request: Request,
username: str = Form(...),
email: str = Form(...),
name: str = Form(...),
password: str = Form(...),
db: Session = Depends(get_db)):
    hashed_password = get_hashed_password(password)
    invalid = False
    if crud.get_user_by_username(db=db,username=username):
        invalid = True
    if crud.get_user_by_email(db=db,email=email):
        invalid = True
    if not invalid:
        crud.user_create(db=db, user=schemas.UserCreate(username=username,email=email,name=name,hashed_password=hashed_password))
        response = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
        return response
    else:
        return templates.TemplateResponse("register.html",{"request": request, "title": "Register", "invalid": True},
        status_code=HTTP_400_BAD_REQUEST)

@app.get("/user_list")
def get_users_all(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    user_model= crud.get_users_all(db=db)
    print(user_model)
    return templates.TemplateResponse("/user_list.html", {"request": request, "title": "Users", "user_model": user_model})

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/")
    manager.set_cookie(response,None)
    return response

@app.get("/user_edit", response_class=HTMLResponse)
def do_user_edit(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager),id: str = Query(...)):
    param =(crud.get_user(db=db,id=id))
    if not param:
            return templates.TemplateResponse("droid_search.html", {"request": request, "id": id, "parameter": param, "title": "Edit user parameters"}, status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse("user_edit.html", {"request": request, "id": id, "parameter": param, "title": "Edit User parameters"})

@app.post("/user_update/{id}")
def do_user_update(request: Request,
id: str,
username: str = Form(...),
email: str = Form(...),
name: str = Form(...),
password: str = Form(...),
db: Session = Depends(get_db)):
    hashed_password = get_hashed_password(password)
    invalid = False
    if invalid == False:
        sql_statement = crud.user_update(id=id,username=username,email=email,name=name,hashed_password=hashed_password)
        print(sql_statement)
        cursor = connection.cursor()
        cursor.execute(sql_statement)
        connection.commit()
    return RedirectResponse(url="/user_list", status_code=302)


@app.get("/user/delete/{id}",response_class=RedirectResponse)
def do_user_delete(id: str = Path(...), db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    crud.user_delete(db=db,id=id)
    return RedirectResponse("/user_list")
    # This function is disabled because it deletes users even though sqlite should enforce
    # foreign key constraints. (you shouldn't be able to delete the user if the user is refered to in the task table.)
    # Need to find a way to enforce foreighn key restraints ... something about PRAGMA = ON?

@app.get("/state_test")
def do_state_test(request: Request, db: Session = Depends(get_db), current_state: schemas.CurrentState = Depends(manager)):
    instance = 1
    current_state_model= crud.current_state_get(db=db, droid_id=DROID_ID)
    print(jsonable_encoder(current_state_model))
    # test if feeder should be running now
    state_running=feeder_start_test(db)
    return templates.TemplateResponse("/current_state_test.html",
     {"request": request, 
     "title": "Current State",
     "current_state_model": current_state_model,
     "state_running": state_running,
     "DROID_ID": DROID_ID})

@app.get("/toggle_state/{switch}")
def do_toggle_still_in_feed_hrs(request: Request, db: Session = Depends(get_db),switch: int=Path(...), current_state: schemas.CurrentState = Depends(manager)):
    #find current overall state - is it running or stopped
    old_state_running = feeder_start_test(db)
    state = crud.current_state_get(db=db,droid_id=DROID_ID)[0][switch]
    if state == 1:
        state = 0
    else:
        state = 1
    #find information about droid
    droid_parameters =crud.droid_parameters(db=db,droid_id=DROID_ID)[0]
    droid_name=droid_parameters[1]
    droid_description=droid_parameters[3]
    feed_density_current=droid_parameters[4]
    command_set_current=droid_parameters[6]
    #update the table
    if switch == 1:
        field = "still_in_feed_hrs"
        reason = "feed hrs"
    if switch == 2:
        field = "daily_limit_not_reached"
        reason = "daily kg limit"
    if switch == 3:
        field = "trough_needs_filling"
        reason = "trough level"
    if switch == 4:
        field = "stop_button_released"
        reason = "stop button"
    crud.current_state_update(droid_id=DROID_ID, state_field_name=field, state = state)
    current_state_model= crud.current_state_get(db=db, droid_id=DROID_ID)
    #
    #assign variabes to all states
    still_in_feed_hrs = current_state_model[0][1]
    daily_limit_not_reached = current_state_model[0][2]
    trough_needs_filling = current_state_model[0][3]
    stop_button_released = current_state_model[0][4]
    #
    # test if feeder should be running now & log to database
    # depending on the command set call the appropriate routine to stop or start
    state_running=feeder_start_test(db)
    if state_running == 'go':
        log_write(db=db,droid_id=DROID_ID,action="start",reason=reason)
        if command_set_current == "pi":
            print("PI starting")
            print("put command to start pi here")
    if state_running == 'stop':
        if old_state_running == 'go':
            log_write(db=db,droid_id=DROID_ID,action="stop",reason=reason)
            if command_set_current == "pi":
                print("PI stopping")
                print("put command to stop pi here")
    #print total run time
    run_time_total = crud.run_time_total(db=db,droid_id=DROID_ID)[0][0]
    print("Run Time Total: " + str(round(run_time_total,1)))
    print(feed_density_current)
    feed_daily_total = round((crud.feed_daily_total(db=db,droid_id=DROID_ID)[0][0]),1)/1000
    print("daily total: " + str(round(feed_daily_total,1)))
    #
    #Work out the webpage appropriate title
    if command_set_current == "pi":
        page_title = "Manual Switching of "
        print(page_title)
    else:
        page_title = "Simulation of "
    
    #Display the last 10 records
    feed_log_last_10_model = crud.feed_log_last_10(db=db, droid_id=DROID_ID)
    print(feed_log_last_10_model)

    return templates.TemplateResponse("/current_state_test.html",
        {"request": request,
        "page_title": page_title,
        "droid_name": droid_name,
        "droid_description": droid_description,
        "current_state_model": current_state_model,
        "still_in_feed_hrs": still_in_feed_hrs,
        "daily_limit_not_reached": daily_limit_not_reached,
        "trough_needs_filling": trough_needs_filling,
        "stop_button_released": stop_button_released,
        "state_running": state_running,
        "feed_density_current": feed_density_current,
        "run_time_total": run_time_total,
        "feed_daily_total": round(feed_daily_total,2),
       # "feed_log_last_10_model": crud.feed_log_last_10(db=db,droid_id=DROID_ID),
        "feed_log_last_10_model": feed_log_last_10_model,
        "DROID_ID": DROID_ID})

def log_write(db,droid_id,action,reason):
    #Create a current time stamp and in seconds
    action_timestamp = time.strftime('%Y-%m-%d %H:%M:%S %Z %z', time.localtime())
    unix_seconds = time.time()
    run_seconds=0
    last_time=0

    #look up the feed density
    feed_density = crud.feed_density_get(db,droid_id=droid_id)
    feed_density = feed_density[0]
    feed_density = feed_density[0]
    print(feed_density)

    #find if log is consistent and current state
    #find last state of log
    droid_id = droid_id
    last_state_record = crud.feed_log_last_state(db=db,droid_id=droid_id)

    #if the table is empty set some defaults
    if last_state_record is None:
        last_state = "start"
        last_time = 0
        run_seconds=0
    print(last_state_record)
    last_state_record = last_state_record[0]
    print(last_state_record)
    last_state = last_state_record[3]
    last_time = last_state_record[2]
    print(last_time)

    #Make sure the log is in a consistent state 
    # If the machine is stopping calculate how long its been running for.
    write_extra_stop = False
    if action == "stop":
        if last_state == "start":
            print("start & stop - all good, subtract the difference and write a stop with time")
            run_seconds = unix_seconds - last_time
    # If the machine is starting make sure there is a preceding stop logged.
    if action == "start":
        if last_state == "stop":
            print(" all good, write a start")
            run_seconds = 0
    # Machine is starting but its missing a previous stop
    if action == "start":
        if last_state == "start":
            print("start & start -a stop has been missed write a stop 0, then a start")
            #Write an extra stop
            crud.feed_log_add(db=db,feed_log=schemas.FeedLogCreate(
            action_timestamp=action_timestamp,
            unix_seconds=unix_seconds,
            droid_id=DROID_ID,
            action="stop",
            feed_density=feed_density,
            run_seconds=0,
            reason=reason))
            run_seconds = 0
    # Machine is stopping but its missing a previous start
    if action == "stop":
        if last_state == "stop":
            print("stop & stop - a start has been missed write a stop 0")
            run_seconds = 0

    #Write to log
    added= crud.feed_log_add(db=db,feed_log=schemas.FeedLogCreate(action_timestamp=action_timestamp,
        unix_seconds=unix_seconds,
        droid_id=droid_id,
        action=action,
        feed_density=feed_density,
        run_seconds=round(run_seconds,0),
        reason=reason,
        method="blah"))
    return

def feeder_start_test(db):
    current_state = (crud.current_state_get(db=db,droid_id=DROID_ID))
    state_hrs=current_state[0][1]
    print(state_hrs)
    state_limit=current_state[0][2]
    print(state_limit)
    state_trough=current_state[0][3]
    print(state_trough)
    state_stop_button=current_state[0][4]
    print(state_stop_button)

    state = state_hrs + state_limit + state_trough + state_stop_button
    if state == 4:
        state_running = "go"
    else:
        state_running = "stop"

    return state_running

@app.get("/schedule_list")
def get_schedlue_list(request: Request, db: Session = Depends(get_db), schedule: schemas.ScheduleBase = Depends(manager)):
    print(DROID_ID)
    schedule_model= crud.get_schedule_28(db=db,droid_id=DROID_ID)
    print(schedule_model)
    return templates.TemplateResponse("/schedule_list.html", {"request": request, "title": "Feeding Schedule", "schedule_model": schedule_model, "droid_id": DROID_ID})

@app.get("/schedule_edit", response_class=HTMLResponse)
def do_schedule_edit(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager),id: str= Query(...)):
    print(jsonable_encoder(crud.schedule_date_get(db=db,id=id)))
    param =(crud.schedule_date_get(db=db,id=id))
    if not param:
            return templates.TemplateResponse("droid_search.html", {"request": request, "id": id, "parameter": param, "title": "Edit droid parameters"}, status_code=status.HTTP_404_NOT_FOUND)
    return templates.TemplateResponse("schedule_edit.html", {"request": request, "id": id, "parameter": param, "title": "Edit schedule parameters"})


@app.post("/schedule_parameters/{id}")
def update_parameters(request: Request,
    id: str,
    droid_id: Optional[str] = Form(None),
    schedule_date: Optional[str] = Form(None),
    meal_1_start: Optional[str] = Form(None),
    meal_1_stop: Optional[str] = Form(None),
    meal_2_start: Optional[str] = Form(None),
    meal_2_stop: Optional[str] = Form(None),
    meal_3_start: Optional[str] = Form(None),
    meal_3_stop: Optional[str] = Form(None),
    plan_kgs: int = Form(...),
    user: schemas.User = Depends(manager),
    db: Session = Depends(get_db)
    ):
    sql_statement = crud.schedule_update_sql(id,droid_id,schedule_date,meal_1_start, meal_1_stop, meal_2_start, meal_2_stop,meal_3_start, meal_3_stop, plan_kgs)
    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    connection.commit()
    return RedirectResponse(url="/schedule_list", status_code=302)

@app.get("/schedule_add")
def get_schedule_add(request: Request):
    droid_id = DROID_ID
    return templates.TemplateResponse("schedule_add.html", {"request": request, "title": "Register", "droid_id": droid_id})

@app.post("/schedule_save")
def do_schedule_save(request: Request,
        droid_id: str = Form(...),
        schedule_date: str = Form(...),
        meal_1_start: str = Form(...),
        meal_1_stop: str = Form(...),
        meal_2_start: str = Form(...),
        meal_2_stop: str = Form(...),
        meal_3_start: str = Form(...),
        meal_3_stop: str = Form(...),
        plan_kgs: int = Form(...),
        date_multiplier: int = Form(...),
        db: Session = Depends(get_db)):
    count=1
    print("plan kgs: " + str(plan_kgs))
    #Convert to a date here
    print(schedule_date)
    schedule_date_formated = datetime.strptime(schedule_date,"%Y-%m-%d") - timedelta(days=1)
    print(schedule_date_formated)

    while count <= (date_multiplier):
        # make it so that the multiplier over writes that numner of days ahead, using the same droid_id, and meal times
        #have to convert to a date, then add 1 day, then convert back to text
        #then overwrite to the database

        #add the count number of days here
        schedule_date_formated = schedule_date_formated + timedelta(days=1)
        schedule_date = schedule_date_formated.strftime("%Y-%m-%d")
        print(schedule_date)
        crud.delete_schedule_day_by_day(db=db,droid_id=droid_id,schedule_date=schedule_date)
        crud.schedule_save(db=db,
                droid_id=droid_id,
                schedule_date=schedule_date,
                meal_1_start=meal_1_start,
                meal_1_stop=meal_1_stop,
                meal_2_start=meal_2_start,
                meal_2_stop=meal_2_stop,
                meal_3_start=meal_3_start,
                meal_3_stop=meal_3_stop,
                plan_kgs=plan_kgs)
        count=count+1
    response = RedirectResponse("/schedule_list", status_code=status.HTTP_302_FOUND)
    return response


@app.get("/schedule_delete/{id}",response_class=RedirectResponse)
def delete_schedule_day(id: str = Path(...), db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    crud.delete_schedule_day(db=db,id=id)
    return RedirectResponse("/schedule_list")

#
#http://127.0.0.1:5000/pi_monitor?trough_needs_filling=1
#@app.get("/pi_monitor/")
#def do_pi_monitor( request: Request, db: Session = Depends(get_db),trough_needs_filling: int=0, user: schemas.User = Depends(manager)):
@app.get("/pi_monitor/")
def do_pi_monitor( request: Request, db: Session = Depends(get_db),user: schemas.User = Depends(manager)):
    #find current overall state - is it running or stopped?
    #what is the old state of the still in feed hours, and daily_limit_not_reached?
    old_state_running = feeder_start_test(db)
    current_state_model= crud.current_state_get(db=db, droid_id=DROID_ID)
    print(current_state_model)
    old_still_in_feed_hrs = current_state_model[0][1]
    print(old_still_in_feed_hrs)
    old_daily_limit_not_reached = current_state_model[0][2]
    print(old_still_in_feed_hrs)
    #print("trough needs filling:" + str(trough_needs_filling))
    old_trough_needs_filling = current_state_model[0][3]
    #
    #get basic info
    #find information about droid
    droid_parameters =crud.droid_parameters(db=db,droid_id=DROID_ID)[0]
    droid_name=droid_parameters[1]
    droid_description=droid_parameters[3]
    feed_density_current=droid_parameters[4]
    command_set_current=droid_parameters[6]
    trough_level_input_no = droid_parameters[7]
    #
    reason=""
    #check schedule - still_in_feed_hrs?
    still_in_feed_hrs=check_schedule(db=db,user=user)
    print("still_in_feed_hrs: " +str(still_in_feed_hrs))
    if still_in_feed_hrs != old_still_in_feed_hrs:
        reason = reason + "feed hrs"
        print(reason)
    # 
    #check if daily_limit_not_reached
    #find total fed out
    feed_daily_total = crud.feed_daily_total(db=db,droid_id=DROID_ID)
    if feed_daily_total:
        feed_daily_total = feed_daily_total[0][0]/1000
    else:
        feed_daily_total = 0
    print(feed_daily_total)
    #feed_daily_total = round((crud.feed_daily_total(db=db,droid_id=DROID_ID)[0][0]),1)/1000
    print("feed daily total" + str(feed_daily_total))
    #find plan_kgs (daily limit) and decide if the daily limit has been reached
    current_date = date.today()
    schedule_times = crud.schedule_get(db=db,droid_id=DROID_ID, current_date=current_date)
    plan_kgs = schedule_times[0][9]
    print(plan_kgs)
    if feed_daily_total < plan_kgs:
        daily_limit_not_reached=1
    else:
        daily_limit_not_reached=0
    print("daily_limit_not_reached: " + str(daily_limit_not_reached))
    if daily_limit_not_reached != old_daily_limit_not_reached:
        reason = reason + "-daily kg limit"
        print(reason)

    #check if trough full - this is set by the parameter passed to this function
    #trough_needs_filling = current_state_model[0][3]
    trough_needs_filling = check_trough_needs_filling(db=db,user=user,input_no=trough_level_input_no,trough_needs_filling_current=old_trough_needs_filling)
    reason = reason + "unknown"

    #stop button released set as default yes, as its un-used
    #stop_button_released = current_state_model[0][4]
    stop_button_released = 1
    reason = reason + "unknown"
    #
    #write to table
    crud.current_state_update_all(
        droid_id=DROID_ID,
        still_in_feed_hrs = still_in_feed_hrs,
        daily_limit_not_reached=daily_limit_not_reached,
        trough_needs_filling=trough_needs_filling,
        stop_button_released=stop_button_released) 
    #
    #diplay results
    current_state_model= crud.current_state_get(db=db, droid_id=DROID_ID)
    #print total run time total
    run_time_total = crud.run_time_total(db=db,droid_id=DROID_ID)
    if run_time_total:
        run_time_total=run_time_total[0][0]
    else:
        run_time_total=0
    print("Run Time Total: " + str(round(run_time_total,1)))
    print(feed_density_current)
    #feed_daily_total = round((crud.feed_daily_total(db=db,droid_id=DROID_ID)[0][0]),1)/1000
    print("daily total: " + str(round(feed_daily_total,1)))
    #Display the last 10 records
    feed_log_last_10_model = crud.feed_log_last_10(db=db, droid_id=DROID_ID)
    print(feed_log_last_10_model)
    
    #
    #Calculate the new feed daily total
    feed_daily_total = crud.feed_daily_total(db=db,droid_id=DROID_ID)
    if feed_daily_total:
        feed_daily_total = feed_daily_total[0][0]/1000
    else:
        feed_daily_total = 0
    print(feed_daily_total)

    state_running=feeder_start_test(db)

    return templates.TemplateResponse("/current_state_auto.html",
        {"request": request,
        "title": "Trough Status",
        "page_title": "Current Trough Status",
        "droid_name": droid_name,
        "droid_description": droid_description,
        "current_state_model": current_state_model,
        "still_in_feed_hrs": still_in_feed_hrs,
        "daily_limit_not_reached": daily_limit_not_reached,
        "trough_needs_filling": trough_needs_filling,
        "stop_button_released": stop_button_released,
        "state_running": state_running,
        "feed_density_current": feed_density_current,
        "run_time_total": run_time_total,
        "feed_daily_total": round(feed_daily_total,2),
        "feed_log_last_10_model": feed_log_last_10_model,
        "DROID_ID": DROID_ID})

#
#
#
def check_schedule(db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    print(current_time)

    #find the schedule for that date
    current_date = date.today()
    schedule_times = crud.schedule_get(db=db,droid_id=DROID_ID, current_date=current_date)
    schedule_date = schedule_times[0][2]
    #
    meal_start_1 = schedule_date +"T" + schedule_times[0][3]+":00.000Z"
    meal_end_1 = schedule_date +"T" + schedule_times[0][4]+":00.000Z"
    meal_start_2 = schedule_date +"T" + schedule_times[0][5]+":00.000Z"
    meal_end_2 = schedule_date +"T" + schedule_times[0][6]+":00.000Z"
    meal_start_3 = schedule_date +"T" + schedule_times[0][7]+":00.000Z"
    meal_end_3 = schedule_date +"T" + schedule_times[0][8]+":00.000Z"
    state = 0
    #Check Meal times
    if current_time >= meal_start_1:
        print("Its >= start_1")
        if current_time <= meal_end_1:
            print("its in the right period 1")
            state = state + 1
    else:
        print("Out of time 1 !")
        state = state + 0 
    if current_time >= meal_start_2:
        print("Its >= start_1")
        if current_time <= meal_end_2:
            print("its in the right period 2")
            state = state + 1
    else:
        print("Out of time 2!")
        state = state + 0
    if current_time >= meal_start_3:
        print("Its >= start_3")
        if current_time <= meal_end_3:
            print("its in the right period 3")
            state = state + 1
    else:
        print("Out of time 1 !")
        state = state + 0 
    print("state: " +str(state))

    if state > 0:
        return (1)
    else:
        return(0)

def check_trough_needs_filling(db: Session = Depends(get_db), user: schemas.User = Depends(manager),input_no: int=0, trough_needs_filling_current: int=0):
    droid_parameters =crud.droid_parameters(db=db,droid_id=DROID_ID)[0]
    command_set_current=droid_parameters[6]
    if command_set_current == "pi":
        #put code to read voltage of level sensor (the input) here
        #use the variable input_no which is set in the parameters of the droid
        #for now, just toggle the variable - OR NOT!
        print("Input Number is:" + str(input_no))
        if trough_needs_filling_current == 0:
            trough_needs_filling = 0
        else:
            trough_needs_filling = 1
    else:
        #we must be testing, so just toggle the current value of the sensor
        if trough_needs_filling_current == 0:
            trough_needs_filling = 0
        else:
            trough_needs_filling = 1
    return (trough_needs_filling)
    

        
    

