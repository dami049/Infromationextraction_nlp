from multiprocessing import Event
from tkinter import S
from turtle import title
import feedparser
from datetime import timedelta, datetime
import random
import requests
from bs4 import BeautifulSoup
import spacy
import re
import metadata_parser
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span
import datefinder
import datetime
from flask import render_template

from persistence.crud import create_dates, create_deadline, create_event, create_venue, get_all_events, get_event_by_url, \
    get_event_deadlines, get_event_venues, get_event, update_event

#from main import display_admin

import os
import os.path
import ssl
import stat
import subprocess
import sys

from persistence.database import drop_table_session_factory, session_factory

STAT_0o775 = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
              | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
              | stat.S_IROTH | stat.S_IXOTH)


def main():
    openssl_dir, openssl_cafile = os.path.split(
        ssl.get_default_verify_paths().openssl_cafile)

    print(" -- pip install --upgrade certifi")
    subprocess.check_call([sys.executable,
                           "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi"])

    import certifi

    # change working directory to the default SSL directory
    os.chdir(openssl_dir)
    relpath_to_certifi_cafile = os.path.relpath(certifi.where())
    print(" -- removing any existing file or link")
    try:
        os.remove(openssl_cafile)
    except FileNotFoundError:
        pass
    print(" -- creating symlink to certifi certificate bundle")
    os.symlink(relpath_to_certifi_cafile, openssl_cafile)
    print(" -- setting permissions")
    os.chmod(openssl_cafile, STAT_0o775)
    print(" -- update complete")

scrap_success = True

def accept_url(url):

    # accept url from user input
    # persist url to event with date
    # return id

    global scrap_success
    response = requests.get(url)
    error_statement = 'The website is no longer'
    try:
        if response.status_code != 200:
            print('The website is no longer')
            scrap_success = False
            # return render_template('admin.htm', error_statement = 'The website is no dead')
            return error_statement
        else:
            scrap_success = True
            event_id = create_event(url, 0, None, None, None,None,'No')
            return event_id
    except:
        scrap_success = False
        return error_statement


def scrap_data(url):

        html = requests.get(url).content
        unicode_str = html.decode('utf8')
        news_soup = BeautifulSoup(unicode_str, "html.parser")

        clean_data = news_soup.get_text(" ")
        clean_data = clean_data.replace('\n',' ')
        clean_data = re.sub('\s{2,}',' ',clean_data)
        return clean_data


def call_spacy(clean_data):
    # function to pass scraped data through NLP library
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(clean_data)
    return doc, nlp

def clean_output(output):
    clean_result = re.sub(r'[^\w\s\/\-\–]''','',output)
    clean_result = clean_result.strip()
    return clean_result

def get_acronym(doc):
    try:
    # get acronym by using the token from spacy doc file and comparing it to a library of acronymns
        acronyms = ['TMA', 'WEIS','eCrimeEU', 'UbiComp', 'CQR', 'AMCIS','SBP-BRiMS','ECIR', 'IEEEVR','CIKM','IEEE TPS','PoPETs','MobiCom',
        'IEEE','MARBLE','SBP-BRIMS','Euro S&P', 'SecWeb','AH','IWSEC']
        for token in doc:
            if str(token) in acronyms:
                acronym = str(token)
                break
        else:
            acronym = 'None' 

        print('Returing acronym',acronym)
        return acronym

    except:
        pass

def get_title(doc,url):
    try:
    # get title using 3 methods
    # Method 1, fromt the metadata
        event_keyword = ['Conference','conference','Workshop','workshop','Symposium']

        page = metadata_parser.MetadataParser(url)
        title_found = page.get_metadatas('title')
        title = ' '.join(title_found)

        if len(title.split()) >= 3 :
            return title
        else:
        #Method 2, look for entities with more that 3 words and have a key word to indicate its an event
            titlemethod2 = []
            for ent in doc.ents:
                if len(ent.text.split()) > 3:
                    for i in event_keyword:
                        if i in ent.text:
                            titlemethod2.append(ent.text)

            #print('Method 2',titlemethod2[0]) 
            #title = titlemethod2[0]
            return titlemethod2[0]

    # Method 3, use regex for event th and identify sentence
    except Exception as e:
        print(e)

    #return title

def get_date(doc):
    try:
    # Using Spacy rule based pattern matcher function, identify event date
        nlp = spacy.load("en_core_web_sm")

        pattern_date = [{'IS_DIGIT': True, 'OP': '?'},
                        {'IS_PUNCT': True, 'OP': '?'},
                        {'IS_DIGIT': True, 'OP': '?'},
                        {'TEXT': {'REGEX': '\d+(th)|(TH)'}, 'OP': '?'},
                        {'LOWER': {'IN': ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                          'september',
                                          'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul',
                                          'aug',
                                          'sep', 'oct', 'nov', 'dec']}},
                        {'IS_DIGIT': True, 'OP': '?'},
                        {'IS_PUNCT': True, 'OP': '?'},
                        {'IS_DIGIT': True, 'OP': '?'},
                        {'IS_DIGIT': True, 'OP': '?'}]

        matcher = Matcher(nlp.vocab)

        matcher.add("DATE", [pattern_date])

        start_len = 0
        for match_id, start, end in matcher(doc):
            string_id = nlp.vocab.strings[match_id]  # Get string representation
            span = doc[start:end]  # The matched span

            if len(span) > start_len:
                event_date = span.text
                start_len = len(span)

        return event_date
    except:
        pass

def get_location(doc):
    try:
    # Using Spacy Named Entity Recognized, identify location using the Geographic Political Entities (GPE)
        count = 0
        event_loc = ''
        for ent in doc.ents:
            #To do: check if GPE is a valid city, country
            if ent.label_ == "GPE":    
                event_loc = event_loc + ' ' + str(ent.text)
                count = count + 1

            if count == 2:
                event_loc = event_loc
                break
        
        #to do check if after event_loc.split(' ') left = right? then find city or county
        return event_loc

    except:
        pass

def get_submission_date(nlp):
    #Get phrases used to describe paper submission type
    
    matcher_paper_submission = PhraseMatcher(nlp.vocab, attr='LOWER')
    patterns_paper_submission = [nlp.make_doc(name) for name in ['paper submission','papers submission','tutorial proposal','submission deadline']]
    matcher_paper_submission.add("Subtype", patterns_paper_submission)

    return matcher_paper_submission

    
#assigns labels to the spans identified for paper submission


# def find_submission_date_after(doc, nlp):
#     try:
#         matcher_paper_submission = get_submission_date(nlp)
#         sub_date = ' '
#         for match_id, start, end in matcher_paper_submission(doc):
#             print("Sub Matched", match_id, doc[start:end])
#             entity = Span(doc,start, end, label = 'SUB')
#             sub_date = doc[end:end+7]
#             print('Sub Date', sub_date)
#             doc.ents += (entity,)
#             print(entity.text)
#             sub_date = str(sub_date).lstrip('date')
#             print(sub_date)

#         date_match = list(datefinder.find_dates(str(sub_date)))


#         if len(date_match) > 0:
#             submission_date = date_match[0]
#             #date = submission_date
#             print('Sub date is ', datetime.date.strftime(submission_date,"%d %B %Y"))
#         else:
#             submission_date = 'No date'

#         return submission_date
    
#     except ValueError:
#         pass

def find_deadlines_dates(doc,nlp):
    try:
        matcher_cycle_type = PhraseMatcher(nlp.vocab, attr='LOWER')
        patterns_cycle_type = [nlp.make_doc(name) for name in ['summer deadlines','winter deadlines','first review cycle',
                                                            'second review cycle','Issue 1', 'Issue 2', 'Issue 3', 'Issue 4' ]]
        #matcher_subtype("SUBTYPE", [nlp('Paper Submission'), nlp('submission deadlines')])
        matcher_cycle_type.add("Cycle", patterns_cycle_type)

        cycle_list = []
        for match_id, start, end in matcher_cycle_type(doc):
            print("Cycle Matched", match_id, doc[start:end])
            cycle_list.append(doc[start:end])
        print(cycle_list)
    
        doc_str = str(doc)
    

        ## -- testing from variable
        print('Type', type(cycle_list))
        submission_deadline = {}
        for i in range(len(cycle_list)):
            start = doc_str.find(str(cycle_list[i])) #+ len(cycle_list[i])
            print('Start',start)
            print('Length',len(cycle_list[i]))
            j = i + 1
            if j < len(cycle_list):
                end = doc_str.find(str(cycle_list[j]))
                print('End', end)
            else:
                end = doc_str.find('\s\s', start)
                print(doc_str.find('\s\s', start))
        
        
            substring = doc_str[start:end]
            print('Substring', substring)

            submission_deadline.update({cycle_list[i]: substring})
        print('Submission Deadline in function', submission_deadline)
        return submission_deadline

    except ValueError:
        pass

def simple_date(doc,nlp):
    try:
        print('getting dates')

        # Get phrases used to describe important dates

        matcher_important_date = PhraseMatcher(nlp.vocab, attr='LOWER')
        patterns_important_date = [nlp.make_doc(name) for name in ['important dates','summer deadlines','winter deadlines',
            'first review cycle','second review cycle','Issue 1', 'Issue 2', 'Issue 3', 'Issue 4' ]]
        matcher_important_date.add("impdate", patterns_important_date)

         # assigns labels to the spans identified for important dates

    
        for match_id, start, end in matcher_important_date(doc):
            print("Matched", match_id, doc[start:end])
            entity = Span(doc, start, end, label='IMP')
            next_word = doc[end:end + 1]
            doc.ents += (entity,)
            print(entity.text)
    except ValueError:
        pass

    found_submission_date = ' '
    found_notification_date = ' '
    found_camera_date = ' '
    submission_date_found = ' '
    notification_date_found = ' '
    camera_date_found = ' '

    try:
        if str(next_word) in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', '1',
                                  '2', '3', '4', '5', '6', '7', '8', '9']:
            print('date before description ')
        else:
            print('date after description')

            found_submission_date = find_submission_date_after(doc,nlp)
            print('found_submission_date', found_submission_date)
            if found_submission_date != 'No date':
                # print('I found submission date ', datetime.date.strftime(found_submission_date, "%d %B %Y"))
                #submission_date_found = datetime.date.strftime(found_submission_date, "%d %B %Y")
                submission_date_found = found_submission_date

            else:
                print('No submission date')
                submission_date_found = 'No Date'
            print('I am here now')
            found_notification_date = find_notification_date_after(doc,nlp)

            if found_notification_date != 'No date':
                # print('I found notification date ', datetime.date.strftime(found_notification_date, "%d %B %Y"))
                #notification_date_found = datetime.date.strftime(found_notification_date, "%d %B %Y")
                notification_date_found = found_notification_date
            else:
                print('No submission date')
                notification_date_found = 'No Date'

            found_camera_date = find_camera_date_after(doc,nlp)

            if found_camera_date != 'No date':
                # print('I found camera date ', datetime.date.strftime(found_camera_date, "%d %B %Y"))
                #camera_date_found = datetime.date.strftime(found_camera_date, "%d %B %Y")
                camera_date_found = found_camera_date
            else:
                print('No submission date')
                camera_date_found = 'No Date'

        print('submission_date_found ',submission_date_found,' notification_date_found ',notification_date_found, ' camera_date_found ',camera_date_found )
        return submission_date_found,notification_date_found, camera_date_found
    except:
        pass



def find_submission_date_after(doc,nlp):
    # Get phrases used to describe paper submission type

    matcher_paper_submission = PhraseMatcher(nlp.vocab, attr='LOWER')
    patterns_paper_submission = [nlp.make_doc(name) for name in ['paper submission', 'papers submission', 
            'tutorial proposal','submission deadline']]
    # matcher_subtype("SUBTYPE", [nlp('Paper Submission'), nlp('submission deadlines')])
    matcher_paper_submission.add("Subtype", patterns_paper_submission)

    # assigns labels to the spans identified for paper submission
    try:
        sub_date = ' '
        for match_id, start, end in matcher_paper_submission(doc):
            print("Sub Matched", match_id, doc[start:end])
            entity = Span(doc, start, end, label='SUB')
            print('Entity 1', entity)
            sub_date = doc[end:end + 7]
            print('Sub Date 1', sub_date)
            doc.ents += (entity,)
            print('Entity text 1', entity.text)
            sub_date = str(sub_date).lstrip('date')
            print(sub_date)
            print('Submission date 1 ', sub_date)

        try:
            date_match = list(datefinder.find_dates(str(sub_date)))
        except:
            date_match = []

        if len(date_match) > 0:
            submission_date = date_match[0]

            # date = submission_date
            print('Sub date is ', datetime.date.strftime(submission_date, "%d %B %Y"))
            correct_sub_date = datetime.date.strftime(submission_date, "%d %B %Y")
            return correct_sub_date
            
        else:
            return 'No date'

        
        

    except ValueError:
        pass 

    # assigns labels to the spans identified for paper notification

def find_notification_date_after(doc, nlp):

    # Get phrases used to describe paper notification type

    matcher_paper_notification = PhraseMatcher(nlp.vocab, attr='LOWER')
    patterns_paper_notification = [nlp.make_doc(name) for name in
                                       ['paper notification', 'decision date', 'notification of acceptance','author notification','notification']]
    matcher_paper_notification.add("Nottype", patterns_paper_notification)

    try:
        not_date = ' '
        for match_id, start, end in matcher_paper_notification(doc):
            print("Not Matched", match_id, doc[start:end])
            entity = Span(doc, start, end, label='NOT')
            not_date = doc[end:end + 7]
            doc.ents += (entity,)
            print(entity.text)
            not_date = str(not_date).lstrip('date')
            print(not_date)

        daten_match = list(datefinder.find_dates(str(not_date)))

        if len(daten_match) > 0:
            notification_date = daten_match[0]
            # date = submission_date
            print('Not date is ', datetime.date.strftime(notification_date, "%d %B %Y"))
            correct_not_date = datetime.date.strftime(notification_date, "%d %B %Y")
            return correct_not_date
        else:
            return 'No date'


    except ValueError:
        pass 


def find_camera_date_after(doc, nlp):


    # Get phrases used to describe camera ready type

    matcher_camera_ready = PhraseMatcher(nlp.vocab, attr='LOWER')
    patterns_camera_ready = [nlp.make_doc(name) for name in ['camera ready', 'camera-ready', 'final papers due']]
    matcher_camera_ready.add("Nottype", patterns_camera_ready)

    # assigns labels to the spans identified for camera ready dates
    try:
        cam_date = ' '
        for match_id, start, end in matcher_camera_ready(doc):
            print("Camera Matched", match_id, doc[start:end])
            entity = Span(doc, start, end, label='CAM')
            cam_date = doc[end:end + 7]
            doc.ents += (entity,)
            print(entity.text)
            cam_date = str(cam_date).lstrip('date')
            print(cam_date)

        datec_match = list(datefinder.find_dates(str(cam_date)))

        if len(datec_match) > 0:
            camera_date = datec_match[0]
            # date = submission_date
            print('Camera date is ', datetime.date.strftime(camera_date, "%d %B %Y"))
            correct_camera_date = datetime.date.strftime(camera_date, "%d %B %Y")
            return correct_camera_date
            
        else:
            return 'No date'


    except ValueError:
        pass


def get_timezone(doc):
#Function to get if timezone was identified

    timezone = ['aoe', 'utc', 'anytime on earth', 'est', 'eet', 'pacific time', 'gmt']
    timezone_found = ' '
    for token in doc:
        if (str(token).lower()) in timezone:
            print(token)
            timezone_found = str(token)
            return(timezone_found)
            break 

def confirm_virtual(doc):
# Function to determine if there is event runs a virtual version using keywords

    try:
        virtual_names = ['virtual', 'online', 'all-digital', 'viturally']

        virtual_found = ' '
        for token in doc:
            if (str(token).lower()) in virtual_names:
                virtual_found = 'Yes'
                break
        return virtual_found
    except ValueError:
        pass
class TrapDates:

    def __init__(self, sentence):
        pass
        self.sentence = sentence
        self.back = 8
        self.front = 12
        self.date_found = []

    def process_date(self, month, string_to_scan):

        regex_set = [
            
            re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December) [\d]{1,2}, [\d]{4}'),
            re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December|Oct) [\d]{1,2}-[\d]{1,2}, [\d]{4}'),
            re.compile(r'd{1,4} [\_|\-|\/|\|] [0-9]{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{1,4}')
        ]

        for reg in regex_set:
            regex = reg.search(string_to_scan)
            if regex is not None:
                print(f'Found date: {regex.group()}\n')
                self.date_found.append({regex.group()})

        return

    def find_dates(self):
        pass
        # find months first
        date_pattern = re.compile(r'January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Oct|Nov|Dec')
        months_found = date_pattern.findall(self.sentence)

        # declare variable to hold short form of phrase
        short_sentence = self.sentence

        # declare next char pickup location
        next_start_char = 0
        for month in months_found:
            # select short phrase based on next character
            short_sentence = short_sentence[next_start_char: len(short_sentence)]

            # get first occurrence of the month
            month_regex = date_pattern.search(short_sentence)

            # determine next start of the phrase
            try:
                next_start_char = month_regex.span()[1] + self.front
            except:
                pass

            try:
                string_to_scan = short_sentence[month_regex.span()[0] - self.back:month_regex.span()[1] + self.front]
                print(f'Searched text: {string_to_scan}')
                self.date_found.append({string_to_scan})
            
                # self.process_month(month, month_regex)
                self.process_date(month, string_to_scan)
            except:
                pass
        return(self.date_found)
        #exit()

        # date_pattern = "^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}$"
        re.match(date_pattern, '12/12/2022')  # Returns Match object

        # Extract date from a string
        date_extract_pattern = "[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}"
        re.findall(date_extract_pattern, 'I\'m on vacation from 1/18/2021 till 1/29/2021')  # returns ['1/18/2021', '1/29/2021']


def dateconverter(date_list):
    try:

        date_match = list(datefinder.find_dates(str(date_list)))


        convert_dates = []
        for i in range(len(date_match)):
            convert_dates.append((datetime.date.strftime(date_match[i], "%d %B %Y")))

        final_dates = set(convert_dates)

        print("Final Dates", final_dates)
        return final_dates
    except:
        pass

class GetTitle:

    def __init__(self, sentence):
        pass
        self.sentence = sentence
        self.back = 5
        self.front = 75
        self.title_found = []


    def find_title(self):
        

        # Pattern for finding title with edition
        
        edition_pattern = re.compile(r'\d+\s?(rd|th|nd|st|RD|TH|ND|ST)(?![\w\d])')
        edition_found = edition_pattern.findall(self.sentence)

        # declare variable to hold short form of phrase
        short_sentence = self.sentence

        # declare next char pickup location#
        next_start_char = 0
        for edition in edition_found:
            # select short phrase based on next character
            short_sentence = short_sentence[next_start_char: len(short_sentence)]

            # get first occurrence of the month
            edition_regex = edition_pattern.search(short_sentence)

            # determine next start of the phrase
            try:
                next_start_char = edition_regex.span()[1] + self.front
            except:
                pass

            try:
                string_to_scan = short_sentence[edition_regex.span()[0] - self.back:edition_regex.span()[1] + self.front]
                print(f'Searched text: {string_to_scan}')
                self.title_found.append({string_to_scan})
            
                # self.process_month(month, month_regex)
                #self.process_date(month, string_to_scan)
            except:
                pass
        num_found = len(self.title_found)
        print("Number found",num_found)
        if num_found <4 and num_found != 0:
            print('First Title Assumed',str(self.title_found[0]))
            return str(self.title_found[0])
        else:
            return None



# Process function that call all other function to get the different fields of interest
def process_data(url, row_id):
    global scrap_success

    if not scrap_success:
        return
        #helpers.redirect(url_for('display_admin'))
    else:
        
        # row_id = accept_url(url)
        print("row_id ", row_id)
    # if row < 0

    
    #Scrape and clean the data retrieved
    clean_data = scrap_data(url)


    doc, nlp = call_spacy(clean_data)
    #print("doc ", doc)

    acronym = get_acronym(doc)
    #acronym = get_acronym(doc,url)
    print("acronym ", acronym)

    td = GetTitle(clean_data)
    title_long = td.find_title() 

    if title_long == None:
        title = get_title(doc,url)
        print("title ", title)
    else:
        title = str(title_long[3:-2])

    event_date = get_date(doc)
    event_date = clean_output(event_date)
    print("Event date ", event_date)

    #New function to get date
    td = TrapDates(clean_data)
    all_dates = td.find_dates()
    con_dates = dateconverter(all_dates)
    
    
    print("///////////  ", all_dates)
    try:
        print("************ Writing in DB")
        create_dates(row_id,all_dates)
    except:
        pass
    #received_dates = dateconverter(date_list)
    #print("********  ", received_dates)

    

    #Get location

    location = get_location(doc)
    location = clean_output(location)
    print("location ", location)

    timezone = get_timezone(doc)
    print('Timezone', timezone)

    virtual = confirm_virtual(doc)
    print('Virtual session available', virtual)

    #cycles & papers

    #dates
    submission_date = find_submission_date_after(doc, nlp)
    print("Submission date ", submission_date)

    #date complex
    deadlines = find_deadlines_dates(doc,nlp)
    print('Submission Deadline', deadlines)

    update_event(row_id, 0, acronym, title, event_date, location,virtual)
    try:
        if deadlines == {}:
            print ('No cycle')
            simpledates = simple_date(doc,nlp)
            if simpledates == None:
                s = ",".join(con_dates)
                create_deadline(row_id,0,None,None,None,None,None,None,timezone,s)
            else:
                s = ",".join(con_dates)
                create_deadline(row_id,0,None,None,simpledates[0],None,simpledates[1],simpledates[2],timezone,s)
            print('simple database entry created')
            print('Simple Dates ', simpledates)
        else:
            for key, value in deadlines.items():
                print('Ready to insert complex dates')
                doc_complex = nlp(str(value))
                simpledates = simple_date(doc_complex,nlp)
                if simpledates == None:
                    s = ",".join(con_dates)
                    create_deadline(row_id,0,str(key),str(value),None,None,None,None,timezone,s)
                else:
                    s = ",".join(con_dates)
                    print("^^^^^^^^^^^^^ I am here")
                    create_deadline(row_id,0,str(key),str(value),simpledates[0],None,simpledates[1],simpledates[2],timezone,s)
            
            return None
    except ValueError:
        pass



def drop_database():
    drop_table_session_factory()


if __name__ == "__main__":
    main()
    drop_database()
    # generate_rss_data('https://dev.to/feed')