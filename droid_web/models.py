from email.policy import default
from xmlrpc.client import Boolean
from sqlalchemy import Float, String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "user"
    id = Column(String, unique=True,primary_key=True, index=True, nullable=False)
    email = Column(String, unique= True, index=True, nullable=False)
    name = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password= Column(String, nullable=False)
   
    items = relationship("Task", back_populates="user" )


class Task(Base):
    __tablename__ = "task"

    id = Column(String, primary_key=True, index=True, nullable=False)
    text = Column(String, index=True, nullable=False)
    complete = Column(Integer,index = True, default = 0)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)

    user = relationship("User", back_populates="items")

class Droid(Base):
    __tablename__ = "droid"

    id = Column(String, unique=True, primary_key=True, index=True, nullable=False)
    droid_name  = Column(String, unique=True, index=True, nullable=False)
    droid_id = Column(String, unique=True, index=True, nullable=False)
    droid_description = Column(String, index=True, nullable=False)
    feed_density= Column(Float, nullable=False)
    droid_server= Column(String)
    command_set = Column(String, index = True, nullable = False)
    trough_level_input_no = Column(Float, nullable=False)

class CurrentState(Base):
    __tablename__ = "current_state"

    instance = Column(Integer, unique=True, primary_key=True, index=True, nullable=False)
    still_in_feed_hrs  = Column(Integer, nullable=False)
    daily_limit_not_reached  = Column(Integer, nullable=False)
    trough_needs_filling  = Column(Integer, nullable=False)
    stop_button_released  = Column(Integer, nullable=False)
    droid_id = Column(String, index=True, nullable=False)

class FeedLog(Base):
    __tablename__ = "feed_log"

    feed_id = Column(Integer, unique=True, primary_key=True, index=True, nullable=False)
    action_timestamp = Column(String, index=True, nullable=False)
    unix_seconds = Column(Float, nullable=False)
    droid_id = Column(String, index=True, nullable=False)
    action = Column(String, index=True, nullable=True)
    feed_density = Column(Float, index=True, nullable=True)
    run_seconds = Column(Float, index=True, nullable=False) 
    reason = Column(String, index=True, nullable=False)
    method = Column(String, index=True, nullable=False)

class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, unique=True, primary_key=True, index=True, nullable=False)
    droid_id = Column(String, index=True, nullable=False)
    schedule_date = Column(String, index=True, nullable=False)
    meal_1_start = Column(String, index=True, nullable=True)
    meal_1_stop = Column(String, index=True, nullable=True)
    meal_2_start = Column(String, index=True, nullable=True)
    meal_2_stop = Column(String, index=True, nullable=True)
    meal_3_start = Column(String, index=True, nullable=True)
    meal_3_stop = Column(String, index=True, nullable=True)
    plan_kgs = Column(Float, index=True, nullable=True)




    