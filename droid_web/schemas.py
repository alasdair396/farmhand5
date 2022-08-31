from ast import Num
import numbers
from xmlrpc.client import boolean
from pydantic import BaseModel
from typing import List, Optional

#Task Example
class TaskBase(BaseModel):
    text: str
    

class Task(TaskBase):
    id: str
    user_id: str
    complete: int
    class Config:
        orm_mode = True

class TaskCreate(TaskBase):
    pass

#Current State
class CurrentState(BaseModel):
    instance: int
    still_in_feed_hrs: int
    daily_limit_not_reached: int
    trough_needs_filling: int
    stop_button_release: int
    droid_id: str

    class Config:
        orm_mode = True
class CurrentStateCreate(CurrentState):
    pass

#Droid Tables
class DroidBase(BaseModel):
    droid_name: str
    droid_id: str
    droid_description: str
    feed_density: float
    droid_server: str
    command_set: str
    trough_level_input_no: float

class Droid(DroidBase):
    id: str
   
    class Config:
        orm_mode = True

class DroidCreate(DroidBase):
    pass       

#User Tables
class UserBase(BaseModel):
    username: str
    name: str
    email: str
    hashed_password: str

class User(UserBase):
    id: str
    tasks: List[Task] = []

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    pass


#feed_log
class FeedLogBase(BaseModel):
    #feed_id: int
    action_timestamp: str
    unix_seconds: float
    droid_id: str
    action: str
    feed_density: float
    run_seconds: float
    reason: str
    method: str

    class Config:
        orm_mode = True

class FeedLogCreate(FeedLogBase):
    pass

#schedule
class ScheduleBase(BaseModel):
    id: int
    droid_id: str
    schedule_date: str
    meal_1_start: str
    meal_1_stop: str
    meal_2_start: str
    meal_2_stop: str
    meal_3_start: str
    meal_3_stop: str
    plan_kgs: int
    class Config:
        orm_mode = True

class ScheduleBase(ScheduleBase):
    pass
