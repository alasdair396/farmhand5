from sqlalchemy.orm import Session
import models, schemas
import uuid

import psycopg2
from fastapi.encoders import jsonable_encoder
from db import SessionLocal, engine, DBContext

connection = psycopg2.connect( database="droid", user="droid", password="r2d2droid", host="0.0.0.0")

def get_user(db: Session, id: str):
    return db.query(models.User).filter(models.User.id == id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users_all(db: Session, skip: int = 0, limit: int = 100):
    users_all = db.query(models.User).all()
    return users_all

def user_create(db: Session, user: schemas.UserCreate):
    id = uuid.uuid4()
    while get_user(db=db,id=str(id)):
        id = uuid.uuid4()
    db_user = models.User(id=str(id),username=user.username,name=user.name,email=user.email,hashed_password=user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def user_update(id,username,name,email,hashed_password):
    sql_statement = f'''
        UPDATE "user"
        SET "username"=       '{username}',
        "name"=               '{name}',
        "email"=              '{email}',
        "hashed_password"=           '{hashed_password}'
        WHERE
        "id" = '{id}'
        '''
    return sql_statement

def user_delete(db: Session, id: str):
    db.query(models.User).filter(models.User.id == id).delete()
    db.commit()
    return

def get_droid(db: Session, id: str):
    return db.query(models.Droid).filter(models.Droid.id == id).first()

def get_current_state(db: Session, instance: str):
    return db.query(models.CurrentState).filter(models.CurrentState.instance == instance).first()

def droid_save(db: Session,droid_name,droid_id,droid_description,feed_density,droid_server,command_set):
    id = uuid.uuid4()
    while get_droid(db=db,id=str(id)):
        id = uuid.uuid4()
    # sql_statement=f'''
    #     INSERT INTO "droid"db.query(models.User).filter(models.User.username == username).first()
    #     ("id","droid_name","droid_id","droid_description","feed_density","droid_server","command_set")
    #     VALUES ('{id}','{droid_name}','{droid_id}','{droid_description}',{feed_density},'{droid_server}','{command_set}')
    #     ;'''
    sql_statement=f'''
        INSERT INTO "droid"
        ("id","droid_name","droid_id","droid_description","feed_density","droid_server","command_set")
        VALUES ('{id}','{droid_name}','{droid_id}','{droid_description}',{feed_density},'{droid_server}','{command_set}')
        ;'''
    print(sql_statement)

    cursor = connection.cursor()
    cursor.execute(sql_statement)
    connection.commit()

    connection.close
    instance = uuid.uuid4()
    while get_current_state(db=db, instance=str(instance)):
        instance = uuid.uuid4()
    sql_statement=f'''
        INSERT INTO current_state 
        (instance, still_in_feed_hrs, daily_limit_not_reached, trough_needs_filling, stop_button_released, droid_id)
        VALUES
        ('{instance}', 0, 0, 0, 0,'{droid_id}')
        ;'''
    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    connection.commit()
    connection.close
    return 

def current_state_save(db: Session, droid_id):
    db_current_state = models.CurrentState(
    still_in_feed_hrs=0,
    daily_limit_not_reached=0,
    trough_needs_filling=0,
    stop_button_released=0,
    droid_id=droid_id)

    print("boo")
    db.add(db_current_state)
    db.commit()
    db.refresh(db_current_state)
    return db_current_state

def current_state_add(db:Session, droid_id):
    instance = uuid.uuid4()
    while get_current_state(db=db, instance=str(instance)):
        instance = uuid.uuid4()
    sql_statement=f'''
        INSERT INTO current_state 
        (instance, still_in_feed_hrs, daily_limit_not_reached, trough_needs_filling, stop_button_released, droid_id)
        VALUES
        ('{instance}', 0, 0, 0, 0,'{droid_id}');
        '''
    print(sql_statement)
    connection.execute(sql_statement)
    return

def update_droid_sql(id,droid_name,droid_id, droid_description, feed_density, droid_server, command_set):
    sql_statement = f'''
        UPDATE "droid"
        SET "droid_name"=     '{droid_name}',
        "droid_id"=           '{droid_id}',
        "droid_description"=  '{droid_description}',
        "feed_density"=       '{feed_density}',
        "droid_server"=       '{droid_server}',
        "command_set"=        '{command_set}'
        WHERE
        "id" = '{id}';
        '''
    print(sql_statement)
    return sql_statement

def droid_by_droid_id_get(db,droid_id):
    return db.query(models.Droid).filter(models.Droid.droid_id == droid_id).first()

def get_tasks_by_user_id(db: Session, id: str, skip: int = 0, limit: int = 100):
    #print(db.query(models.Task).filter(models.Task.user_id == id).offset(skip).limit(limit).all())
    #print(jsonable_encoder(db.query(models.Task).filter(models.Task.user_id == id).offset(skip).limit(limit).all()))
    return db.query(models.Task).filter(models.Task.user_id == id).offset(skip).limit(limit).all()

def get_droids_all(db: Session, skip: int = 0, limit: int = 100):
    droids_all = db.query(models.Droid).all()
    return droids_all

def get_task_by_id(db: Session, id: str):
    return db.query(models.Task).filter(models.Task.id == id).first()

def add_task(db: Session, task: schemas.TaskCreate, complete: int, id: str):
    if not get_user(db=db,id=str(id)):
        return None
    task_id = uuid.uuid4()
    while get_task_by_id(db=db,id=str(task_id)):
        task_id = uuid.uuid4()
    
    db_task = models.Task(id=str(task_id),text=task.text,complete=complete,user_id=id)
    db.add(db_task)
    db.commit() 
    db.refresh(db_task)
    return db_task

def current_state_get(db: Session, droid_id: str):
    sql_statement = f'''
        SELECT * FROM current_state
        WHERE
        "droid_id" =              '{droid_id}';
        '''
    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    current_state = cursor.fetchall()
    print("next is current state:")
    print(current_state)
    connection.commit()
    connection.close
    return current_state

def current_state_update(droid_id, state_field_name, state):
    sql_statement = f'''
        UPDATE "current_state"
        SET '{state_field_name}' =  {state}
        WHERE
        "droid_id" =              '{droid_id}';
        '''
    connection.execute(sql_statement)
    connection.commit()
    return

def current_state_update_all(droid_id,still_in_feed_hrs,daily_limit_not_reached,trough_needs_filling, stop_button_released):
    sql_statement = f'''
        UPDATE "current_state"
        SET "still_in_feed_hrs" =     {still_in_feed_hrs},
        "daily_limit_not_reached" =   {daily_limit_not_reached},
        "trough_needs_filling" =      {trough_needs_filling},
        "stop_button_released" =      {stop_button_released}
        WHERE
        "droid_id" =              '{droid_id}';
        '''
    do_sql(sql_statement)
    return



def feed_log_last_state(db: Session, droid_id):
    sql_statement = f'''
        SELECT max(feed_id), droid_id,unix_seconds,action
        FROM feed_log
        WHERE droid_id = '{droid_id}';
    '''

    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    feed_log_last_state = cursor.execute(sql_statement).fetchall()
    connection.commit()
    connection.close

    #feed_log_last_state = connection.execute(sql_statement).fetchall()

    return (feed_log_last_state)

def feed_log_add(db: Session, feed_log: schemas.FeedLogCreate):
    
    db_feed_log = models.FeedLog(action_timestamp=feed_log.action_timestamp,
    unix_seconds=feed_log.unix_seconds,
    droid_id=feed_log.droid_id,
    action=feed_log.action,
    feed_density=feed_log.feed_density,
    run_seconds=feed_log.run_seconds,
    reason=feed_log.reason)

    db.add(db_feed_log)
    db.commit() 
    db.refresh(db_feed_log)

    return db_feed_log

def feed_density_get(db: Session, droid_id):
    sql_statement = f'''
        SELECT feed_density
        FROM droid
        WHERE droid_id = '{droid_id}';
        '''
    feed_density = connection.execute(sql_statement).fetchall()
    db.commit()
    db.close
    return (feed_density)

def run_time_total(db: Session, droid_id):
    sql_statement = f'''
    SELECT sum(run_seconds)
    FROM feed_log
    WHERE Date('now','localtime') = substr(action_timestamp,0,11)
    AND
    droid_id = '{droid_id}'
    GROUP BY substr(action_timestamp,0,11);
    '''
    print(sql_statement)
    run_time_total = connection.execute(sql_statement).fetchall()
    db.commit()
    db.close
    return (run_time_total)

def run_time_total(db: Session, droid_id):
    sql_statement = f'''
    SELECT sum("run_seconds"*"feed_density") 
    FROM "feed_log"
    WHERE "action_timestamp" > now() - interval '1 day'
    AND
    "droid_id" = '{droid_id}'
    GROUP BY date("action_timestamp")
    '''
    run_time_total = return_sql_results(sql_statement)
    return (run_time_total)

def feed_density_current(db: Session, droid_id):
    sql_statement = f'''
    SELECT feed_density
    FROM droid
    WHERE droid_id = '{droid_id}'
    '''
    print(sql_statement)
    feed_density_current = connection.execute(sql_statement).fetchall()
    db.commit()
    db.close
    return (feed_density_current)

def feed_daily_total(db: Session, droid_id):
    sql_statement = f'''
    SELECT sum("run_seconds"*"feed_density") 
    FROM "feed_log"
    WHERE "action_timestamp" > now() - interval '1 day'
    AND
    "droid_id" = '{droid_id}'
    GROUP BY date("action_timestamp")
    ;
    '''
    # print(sql_statement)
    # feed_daily_total = connection.execute(sql_statement).fetchall()
    # db.commit()
    # db.close
    feed_daily_total = return_sql_results(sql_statement)
    return (feed_daily_total)

def command_set_current(db: Session, droid_id):
    sql_statement = f'''
    SELECT command_set
    FROM droid
    WHERE droid_id = '{droid_id}'
    '''
    print(sql_statement)
    command_set_current = connection.execute(sql_statement).fetchall()
    db.commit()
    db.close
    return (command_set_current)

def droid_parameters(db: Session, droid_id):
    sql_statement = f'''
    SELECT *
    FROM droid
    WHERE droid_id = '{droid_id}'
    '''
    # print(sql_statement)
    # droid_parameters = connection.execute(sql_statement).fetchall()
    # db.commit()
    # db.close

    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    droid_parameters = cursor.fetchall()
    print("next droid_parameters:")
    print(droid_parameters)
    connection.commit()
    connection.close

    return (droid_parameters)

def feed_log_last_10(db: Session, droid_id):
    feed_log_all = db.query(models.FeedLog).filter(models.FeedLog.droid_id == droid_id).order_by(models.FeedLog.action_timestamp.desc()).limit(10)
    return feed_log_all

def get_schedule_28(db: Session, droid_id):
    schedule_28 = db.query(models.Schedule).filter(models.Schedule.droid_id == droid_id).order_by(models.Schedule.schedule_date.asc()).limit(28)
    return schedule_28


#def get_schedule_date(db: Session, id: str):
#    return db.query(models.Schedule).filter(models.Schedule.id == id).first()


def schedule_update_sql(id,droid_id,schedule_date,meal_1_start, meal_1_stop, meal_2_start, meal_2_stop,meal_3_start, meal_3_stop, plan_kgs):
    sql_statement = f'''
        UPDATE schedule
        SET droid_id=      '{droid_id}',
        schedule_date=     '{schedule_date}',
        meal_1_start=      '{meal_1_start}',
        meal_1_stop=       '{meal_1_stop}',
        meal_2_start=      '{meal_2_start}',
        meal_2_stop=       '{meal_2_stop}',
        meal_3_start=      '{meal_3_start}',
        meal_3_stop=       '{meal_3_stop}',
        plan_kgs=           {plan_kgs}
        WHERE
        id = '{id}';
        '''
    print(sql_statement)
    return sql_statement

def schedule_date_get(db,id):
    return db.query(models.Schedule).filter(models.Schedule.id == id).first()

def schedule_save(db,droid_id,schedule_date,meal_1_start, meal_1_stop, meal_2_start, meal_2_stop,meal_3_start, meal_3_stop, plan_kgs):
    id = uuid.uuid4()
    print("id: " + str(id))
    while schedule_date_get(db=db,id=str(id)):
        id = uuid.uuid4()
    sql_statement=f'''
        INSERT INTO schedule
        (id,droid_id,schedule_date,meal_1_start, meal_1_stop, meal_2_start, meal_2_stop,meal_3_start, meal_3_stop, plan_kgs)
        VALUES ('{id}','{droid_id}','{schedule_date}','{meal_1_start}','{meal_1_stop}','{meal_2_start}','{meal_2_stop}','{meal_3_start}','{meal_3_stop}','{plan_kgs}')
        ;'''
    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    connection.commit()
    connection.close
    return

def delete_schedule_day(db: Session, id: str):
    db.query(models.Schedule).filter(models.Schedule.id == id).delete()
    db.commit()

def delete_schedule_day_by_day(db: Session,droid_id,schedule_date):
    sql_statement=f'''
        DELETE FROM "schedule"
        WHERE
        "droid_id" = '{droid_id}' AND
        schedule_date = '{schedule_date}'
        ;''' 
    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    connection.commit()
    connection.close
    return 

def schedule_get(db: Session, droid_id: str, current_date: str):
    sql_statement = f'''
        SELECT * FROM "schedule"
        WHERE
        "droid_id" =              '{droid_id}'
        AND
        "schedule_date" = '{current_date}';
        '''
    # schedule_times=connection.execute(sql_statement).fetchall()
    # db.commit()
    # db.close

    # print(sql_statement)
    # cursor = connection.cursor()
    # cursor.execute(sql_statement)
    # schedule_times = cursor.fetchall()
    # print("next schedule_times:")
    # print(droid_parameters)
    # connection.commit()
    # connection.close
    schedule_times = return_sql_results(sql_statement)

    return(schedule_times)

def return_sql_results(sql_statement):
    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    result = cursor.fetchall()
    print(result)
    connection.commit()
    connection.close
    return result

def do_sql(sql_statement):
    print(sql_statement)
    cursor = connection.cursor()
    cursor.execute(sql_statement)
    connection.commit()
    connection.close
    return