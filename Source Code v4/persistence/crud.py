from persistence.database import Base, session_factory
from persistence.model import Dates, Event, Deadline, Venue
from sqlalchemy.sql import select
from sqlalchemy import desc,asc,update
import traceback


db=session_factory

def create_event(url, data_processed, acronym, event_name, event_date,location,virtual):
    event = Event(url, data_processed, acronym, event_name, event_date,location,virtual)
    session = session_factory()
    session.add(event)
    session.commit()
    return event.eventid


        # event = Event.query.filter(Event.eventid == str(eventid)).first()

def update_event(event_id, data_processed, acronym, title, event_date, location,virtual):
    try:

        # event = session.query(Event).query.filter(Event.eventid == event_id).first()
        # event.acronym = str(acronym)
        # event.title = str(title)
        # event.location = str(location)

        # update({Customers.name:"Mr."+Customers.name}, synchronize_session = False)

        u = update(Event)
        u = u.values(
            {Event.acronym:acronym, Event.data_processed:data_processed, Event.event_name:title, Event.event_date: event_date, Event.location: location,
            Event.virtual: virtual})
        u = u.where(Event.eventid == event_id)

        print(u)
        session = session_factory()
        session.execute(u)
        session.commit()
        session.flush()
        session.close()
    except:
        print('Error in def update_event')
        traceback.print_exc()

def update_deadline(eventid, data_processed, cycle,submission_date,rebuttal_period,notification_date,
cameraready_date,timezone,date_list):
    try:

        # event = session.query(Event).query.filter(Event.eventid == event_id).first()
        # event.acronym = str(acronym)
        # event.title = str(title)
        # event.location = str(location)

        # update({Customers.name:"Mr."+Customers.name}, synchronize_session = False)

        u = update(Deadline)
        u = u.values(
            {Deadline.data_processed:data_processed, Deadline.cycle:cycle,  
            Deadline.submission_date: submission_date, Deadline.rebuttal_period: rebuttal_period,
            Deadline.notification_date: notification_date, Deadline.cameraready_date: cameraready_date,
            Deadline.timezone: timezone,Deadline.date_list: date_list})
        u = u.where(Deadline.eventid == eventid)

        print(u)
        session = session_factory()
        session.execute(u)
        session.commit()
        session.flush()
        session.close()
    except:
        print('Error in def update_deadline')
        traceback.print_exc()

def confirm_event(event_id,data_processed):
    try:

        u = update(Event)
        u = u.values(
            {Event.data_processed:data_processed })
        u = u.where(Event.eventid == event_id)

        print(u)
        session = session_factory()
        session.execute(u)
        session.commit()
        session.flush()
        session.close()
    except:
        print('Error in def confirm_event')
        traceback.print_exc()

def confirm_deadline(event_id,data_processed):
    try:

        u = update(Deadline)
        u = u.values(
            {Deadline.data_processed:data_processed })
        u = u.where(Deadline.eventid == event_id)

        print(u)
        session = session_factory()
        session.execute(u)
        session.commit()
        session.flush()
        session.close()
    except:
        print('Error in def update_event')
        traceback.print_exc()


def create_deadline(eventid, data_processed, cycle, document_type,submission_date,rebuttal_period,notification_date,cameraready_date,timezone,date_list):

    deadline = Deadline(eventid, data_processed, cycle, document_type,submission_date,rebuttal_period,notification_date,cameraready_date,timezone,date_list)
    session = session_factory()
    session.add(deadline)
    session.commit()
    
    return deadline.deadlineid

def create_dates(eventid, dates):

    dates = Dates(eventid, dates)
    session = session_factory()
    session.add(dates)
    session.commit()
    
    return dates.dateid

def create_venue(eventid, city, country, event_date):
    venue = Venue(eventid, city, country, event_date)
    session = session_factory()
    session.add(venue)
    session.commit()
    return venue.venueid

def get_all_events(direction):
    session = session_factory()
    events_query = session.query(Event)
    if(direction > 0):
        events_query.order_by(asc(Event.created))
    else:
        events_query.order_by(desc(Event.created))
    session.close
    return events_query.all()

def get_event_deadlines(eventid):
    session = session_factory()
    deadlines_query = session.query(Deadline).join(Event, Deadline.event).filter(Event.eventid == eventid)
    session.close
    return deadlines_query.all()

def get_event_venues(eventid):
    session = session_factory()
    venues_query = session.query(Venue).join(Event, Venue.event).filter(Event.eventid == eventid)
    session.close
    return venues_query.all()

def get_event_dates(eventid):
    session = session_factory()
    dates_query = session.query(Dates).join(Event, Dates.event).filter(Event.eventid == eventid)
    session.close
    return dates_query.all()

def get_event(eventid):
    session = session_factory()
    event = session.query(Event).get(eventid)
    return event

def get_event_by_url(event_url):
    session = session_factory()
    event_q = session.query(Event).filter(Event.url==event_url).all()
    return event_q

def get_event_cycles(eventid):
    session = session_factory()
    deadlines_query = session.query(Deadline).join(Event, Deadline.event).filter(Event.eventid == eventid).filter(Deadline.cycle is not None)
    session.close
    return deadlines_query.all()

def get_event_deadline(eventid):
    session = session_factory()
    deadlines_query = session.query(Deadline).join(Event, Deadline.event).filter(Event.eventid == eventid).filter(Deadline.cycle == None)
    session.close
    return deadlines_query.first()