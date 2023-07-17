from datetime import date
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Date, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from persistence.database import Base

db=Base

class Event(db):
    __tablename__ = 'event'
    eventid=Column('eventid', Integer, autoincrement=True, nullable=True, primary_key=True)
    url=Column(String(200), nullable=False)
    data_processed=Column(Integer, nullable=False)
    acronym=Column(String(200), nullable=True)
    event_name=Column(String(200), nullable=True)
    event_date=Column(String(200), nullable=True)
    location=Column(String(200), nullable=True)
    virtual=Column(String(10), nullable=True)
    created = Column(DateTime(timezone=True),server_default=func.now())

    # deadlines = relationship("Deadline", back_populates="deadlines")
    # venues = relationship("Venue", back_populates="venue")
    
    def __init__(self, url, data_processed, acronym, event_name, event_date,location,virtual):
        self.url = url
        self.data_processed=data_processed
        self.acronym=acronym
        self.event_name=event_name
        self.event_date=event_date
        self.location=location
        self.virtual=virtual



class Deadline(db):
    __tablename__ = 'deadlines'
    deadlineid=Column('deadlineid', Integer, autoincrement=True, nullable=False, primary_key=True)
    # eventid=Column(Integer, nullable=False)
    data_processed=Column(Integer, nullable=False)
    cycle=Column(String(200), nullable=True)
    document_type=Column(String(400), nullable=True)
    submission_date=Column(String(200), nullable=True)
    rebuttal_period=Column(String(200), nullable=True)
    notification_date=Column(String(200), nullable=True)
    cameraready_date=Column(String(200), nullable=True)
    timezone=Column(String(200), nullable=True)
    date_list=Column(String(600), nullable=True) #just
    #event_date=Column(String(200), nullable=True)
    created = Column(DateTime(timezone=True),server_default=func.now())
    eventid = Column(Integer, ForeignKey('event.eventid'))
    # event = relationship("Event", back_populates="events")
    event = relationship("Event")

# class Deadline(db):
#     __tablename__ = 'deadlines'
#     deadlineid=Column('deadlineid', Integer, autoincrement=True, nullable=False, primary_key=True)
#     # eventid=Column(Integer, nullable=False)
#     data_processed=Column(Integer, nullable=False)
#     cycle=Column(String(200), nullable=True)
#     document_type=Column(String(400), nullable=True)
#     created = Column(DateTime(timezone=True),server_default=func.now())
#     eventid = Column(Integer, ForeignKey('event.eventid'))
#     # event = relationship("Event", back_populates="events")
#     event = relationship("Event")
    

    def __init__(self, eventid, data_processed, cycle, document_type,submission_date, 
    rebuttal_period, notification_date, cameraready_date, timezone,date_list):
        self.eventid = eventid
        self.data_processed=data_processed
        self.cycle=cycle
        self.document_type=document_type
        self.submission_date=submission_date
        self.rebuttal_period=rebuttal_period
        self.notification_date=notification_date
        self.cameraready_date=cameraready_date
        self.timezone=timezone
        self.date_list=date_list
        #self.event_date=event_date
        # self.event=event

    # def __init__(self, eventid, data_processed, cycle, document_type):
    #     self.eventid = eventid
    #     self.data_processed=data_processed
    #     self.cycle=cycle
    #     self.document_type=document_type
    #     # self.event=event



class Venue(db):
    __tablename__ = 'venue'
    venueid=Column('venueid', Integer, autoincrement=True, nullable=True, primary_key=True)
    # eventid=Column(Integer, nullable=False)
    city=Column(Integer, nullable=True)
    country=Column(String(200), nullable=True)
    created = Column(DateTime(timezone=True),server_default=func.now())
    eventid = Column(Integer, ForeignKey('event.eventid'))
    event = relationship("Event")
    # event = relationship("Event", back_populates="events")


    def __init__(self, eventid, city, country, event_date):
        self.eventid = eventid
        self.city=city
        self.country=country
        self.event_date=event_date
        # self.event=event

class Dates(db):
    __tablename__ = 'dates'
    dateid=Column('dateid', Integer, autoincrement=True, nullable=True, primary_key=True)
    date_list=Column(String(400), nullable=True)
    created = Column(DateTime(timezone=True),server_default=func.now())
    eventid = Column(Integer, ForeignKey('event.eventid'))
    event = relationship("Event")

    def __init__(self, eventid, datelist):
        self.eventid = eventid
        self.date_list = datelist