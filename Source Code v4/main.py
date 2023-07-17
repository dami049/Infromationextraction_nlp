import os
from n_processor import accept_url, process_data
from persistence.crud import create_event, create_venue, get_all_events, get_event_dates, \
    get_event_deadlines, get_event_venues, get_event, get_event_deadline, \
    get_event_cycles, confirm_event, update_event, confirm_deadline, update_deadline
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

events = []


@app.route('/', methods=["GET"])
def user_page():
    events = get_all_events(1)
    return render_template('event.htm', page_title='Event Page', events=events)


@app.route('/event_detail')
def event_detail():
    selected_event = request.args.get('event_id', type = int, default=None)
    if selected_event is None:
        events = get_all_events(1)
        return render_template('event.htm', page_title='Event Page', events=events)
    else:
        event = get_event(selected_event)
        if event is None:
            events = get_all_events(1)
            return render_template('event.htm', page_title='Event Page', events=events)
        else:
            upcomingevents = get_all_events(1)
            venues = get_event_venues(event.eventid)
            deadline = get_event_deadline(event.eventid)
            
            cycles = get_event_cycles(event.eventid)
            
            return render_template('event_detail.htm', page_title=event.event_name, event=event, venues=venues, 
                deadline=deadline, upcomingevents=upcomingevents, cycles=cycles)

@app.route('/event_update', methods=["GET", "POST"])
def event_update():
    
    if request.method == "POST":
        rss_url = request.form.get("rss_url")
        eventid = request.form.get("eventId")
        print("######## Eventid received", eventid)
        print("????????????printing request", request.form)

        if request.form['submit'] == 'confirm':
            # update data_processed=1
            confirm_event(eventid, 1)
            confirm_deadline(eventid,1)
            print('####################### Event Confirmed')
        elif request.form['submit'] == 'edit':
            # update data_processed=2
            acronym = request.form.get("acronym")
            title = request.form.get("event_name")
            event_date = request.form.get("date")
            location = request.form.get("location")
            virtual = request.form.get("virtual")
            cycle = request.form.get("cycle")
            submission_date = request.form.get("submission_date")
            rebuttal_period = request.form.get("rebuttal_period")
            notification_date = request.form.get("notification_date")
            cameraready_date = request.form.get("cameraready_date")
            timezone = request.form.get("timezone")
            date_list = request.form.get("date_list")

            update_event(eventid, 2, acronym, title, event_date, location,virtual)
            print("?????????????????Check date updates",submission_date,notification_date)
            update_deadline(eventid, 2, cycle, submission_date,rebuttal_period,notification_date,
            cameraready_date,timezone,date_list)
            print('################ Event Updated')
        return redirect(url_for('display_admin'))
    else:
        selected_event = request.args.get('event_id', type = int, default=None)
        if selected_event is None:
            events = get_all_events(1)
            return render_template('event.htm', page_title='Event Page', events=events)
        else:
            event = get_event(selected_event)
            if event is None:
                events = get_all_events(1)
                return render_template('event.htm', page_title='Event Page', events=events)
            else:
                my_list=[]
                upcomingevents = get_all_events(1)
                venues = get_event_venues(event.eventid)
                deadline = get_event_deadline(event.eventid)
                if deadline is not None:
                    my_list = deadline.date_list.split(",")
                
                cycles = get_event_cycles(event.eventid)
                dates = get_event_dates(event.eventid)
                return render_template('event_update.htm', page_title=event.event_name, event=event, venues=venues, 
                    deadline=deadline, upcomingevents=upcomingevents, cycles=cycles, dates=dates, my_list = my_list)



@app.route('/admin', methods=["GET", "POST"])
def display_admin():
    
    if request.method == "POST":
        rss_url = request.form.get("rss_url")
        if(rss_url is None):
            print("emty post")
        else:
            # generate_rss_data(rss_url)
            row_id = accept_url(rss_url)
            str_rwo_id = str(row_id)
            if str_rwo_id.isnumeric():
                process_data(rss_url, row_id)
                return redirect(url_for('display_admin'))
            else:
                events = get_all_events(0)
                return render_template('admin.htm', page_title='Event Admin Page', events=events, error_statement = row_id)
    else:
        events = get_all_events(0)
        return render_template('admin.htm', page_title='Event Admin Page', events=events)
        
        
    

if __name__ == "__main__":
    app.run() #(debug=True)
    events = get_all_events(1)
    for event in events:
        print(f'{event.url} running on {event.created}')



