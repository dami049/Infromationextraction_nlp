from calendar import c
import metadata_parser
import requests
from bs4 import BeautifulSoup
import spacy
import re
from spacy.matcher import Matcher, PhraseMatcher
import datefinder, datetime
from spacy.tokens import Span
import pytz
import geonamescache

##from PIL import Image
#import pytesseract as pt

def date_test(doc):
    print('test')

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
    print('Submission Deadline in test module', submission_deadline)

    return submission_deadline
    '''
        #find dates in the substring
        date_match = list(datefinder.find_dates(substring))
        
        date_found = []
    
        submission_type = []
        for i in range(len(date_match)):
            date = datetime.date.strftime(date_match[i],"%d %B %Y")
            
            date_found.append(date)
            print('Date found', date_found[i])
    '''
            #start_sub = substring.find(date_found[i]) 
            #print('start_sub',start_sub)
            #submission_type.append(substring.partition(date))
            #print('submission',submission_type)
            #type_pattern = '([^/\n]*(\w*)).[aA]ugust'
            #i type_pattern = '([^\n]*(\w*)).{date_found[i]}'
            #print('type pattern', type_pattern)
            #n type_match = re.findall(type_pattern,substring)
            # print('What i found', type_match)
            #submission_type.update({type_match: date})
            #print('Dic worked', submission_type)
            #submission_type = substring.split("May", 1)[0]
        
        


    # Code for getting title 

    # event_keyword = ['Conference','conference','Workshop','workshop','Symposium']

    # page = metadata_parser.MetadataParser(url)
    # title_found = page.get_metadatas('title')
    # title = ' '.join(title_found)
    # #print(title)
    # # print(title_found)
    # if len(title.split()) > 4:
    #     print('Title found', title)
    # else:
    # # #Method 2, look for entities with more that 3 words and have a key word to indicate its an event
    #     titlemethod2 = []
    #     for ent in doc.ents:
    #         if len(ent.text.split()) > 3:
    #             for i in event_keyword:
    #                 if i in ent.text:
    #                     titlemethod2.append(ent.text)
    #     print('Method 2',titlemethod2[0]) 

def get_country_test(doc):
    print('now testing geonames')
   

    gc = geonamescache.GeonamesCache()

    #get countries
    countries = gc.get_countries()

    #get cities
    #cities = gc.get_cities()
    name = 'lagos'
    
    cities = gc.search_cities('Enschede',case_sensitive=False)
    #country = gc.get_countries('GB')
    if len(cities) <= 0:
        print("City not found")
    else:
        for x in range(len(cities)):
            print(cities[x])
            country_code = cities[x]['countrycode']
            print(pytz.country_names[country_code])
            #print(country)
    #print(cities(1))
    #print('This should work',cities[0][3])


    def gen_dict_extract(var, key):
        if isinstance(var, dict):
            for k, v in var.items():
                if k == key:
                    yield v
                if isinstance(v, (dict, list)):
                    yield from gen_dict_extract(v, key)
        elif isinstance(var, list):
            for d in var:
                yield from gen_dict_extract(d, key)

    cities = [*gen_dict_extract(cities, 'name')]
    countries = [*gen_dict_extract(countries, 'name')]

    count = 0
    event_loc = ''
    for ent in doc.ents:
        
        if ent.label_ == "GPE": 
            print('Ent', ent.label_)
            #To do: check if GPE is a valid city, country
            if ent.text in countries:
                print(f"Country : {ent.text}")   
            event_loc = event_loc + ' ' + str(ent.text)
            count = count + 1

            if count == 2:
                event_loc = event_loc
                break
        
        #to do check if after event_loc.split(' ') left = right? then find city or county
        return event_loc

def simple_date(doc,nlp):
    print('getting dates')

    # Get phrases used to describe important dates

    matcher_important_date = PhraseMatcher(nlp.vocab, attr='LOWER')
    patterns_important_date = [nlp.make_doc(name) for name in ['important dates','summer deadlines','winter deadlines',
            'first review cycle','second review cycle','Issue 1', 'Issue 2', 'Issue 3', 'Issue 4' ]]
    matcher_important_date.add("impdate", patterns_important_date)

    # assigns labels to the spans identified for important dates

    try:
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

        date_match = list(datefinder.find_dates(str(sub_date)))

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

def find_notification_date_after(doc,nlp):

    # Get phrases used to describe paper notification type

    matcher_paper_notification = PhraseMatcher(nlp.vocab, attr='LOWER')
    patterns_paper_notification = [nlp.make_doc(name) for name in
                                       ['paper notification', 'decision date', 'notification of acceptance','author notification','notification']]
    matcher_paper_notification.add("Nottype", patterns_paper_notification)

    try:
        not_date = ' '

        for match_id, start, end in matcher_paper_notification(doc):
            print("Notf Matched", match_id, doc[start:end])
            entity = Span(doc, start, end, label='NOT')
            not_date = doc[end:end + 6]
            doc.ents += (entity,)
            print(entity.text)
            not_date = str(not_date).lstrip('date')
            print(not_date)
            break

        daten_match = list(datefinder.find_dates(str(not_date)))

        if len(daten_match) > 0:
            notification_date = daten_match[0]
            # date = submission_date
            print('Not date is ', datetime.date.strftime(notification_date, "%d %B %Y"))
            correct_not_date = datetime.date.strftime(notification_date, "%d %B %Y")
            return correct_not_date
        else:
            return 'No date'

        return (notification_date)

    except ValueError as e:
        print('Error is',e)


def find_camera_date_after(doc,nlp):


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
            break

        datec_match = list(datefinder.find_dates(str(cam_date)))

        if len(datec_match) > 0:
            camera_date = datec_match[0]
            # date = submission_date
            print('Camera date is ', datetime.date.strftime(camera_date, "%d %B %Y"))
            correct_camera_date = datetime.date.strftime(camera_date, "%d %B %Y")
            return correct_camera_date
            
        else:
            return 'No date'

        return (camera_date)

    except ValueError as e:
        print('Error is',e)

def get_timezone(doc):
    timezone = ['aoe', 'utc', 'anytime on earth', 'est', 'eet', 'pacific time', 'gmt', 'global']
    timezone_found = ' '
    for token in doc:
        if (str(token).lower()) in timezone:
            print(token)
            timezone_found = str(token)
            return(timezone_found)
            break      

def confirm_virtual(doc):
    try:
    #Determine if there is event runs a virtual version using keywords
        virtual_names = ['virtual', 'online', 'all-digital', 'viturally']

        virtual_found = ' '
        for token in doc:
            if (str(token).lower()) in virtual_names:
                virtual_found = 'Yes'
                break
        return virtual_found
    except ValueError:
        pass
    
def extract_date():
    #test_extracted = """Today is 29th of May, 2020. In UK is written as 05/29/2020, or 5/29/2020 or you can even find it as 5/29/20. Instead of / you can either use - or . like 5-29-2020 or 5.29.2020. In Greece, the date format is dd/mm/yy, which means that today is 29/05/2020 and again we can use dots or hyphen between date parts like 29-05-20 or 29.05.2020. We can also add time, like 29/05/2020 19:30. Personally, my favorite date format is Y/mm/dd so, I would be happy to convert easily all these different dates to 2020/05/29"""
    test_extracted = """Issue 2 Paper submission deadline: August 31, 2022 (firm) Rebuttal period: October 12–17, 2022 Author notification: November 1, 2022 Camera-ready deadline for accepted papers and minor revisions (if accepted by the shepherd): December 15, 2022 Issue 2 None None None None"""
    date_match = list(datefinder.find_dates(test_extracted,source=True))
    return(date_match)

def get_location(doc):

    gc = geonamescache.GeonamesCache()
    #get countries
    countries = gc.get_countries()

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
        event_loc = event_loc.lstrip()
        word_list = event_loc.split()
        num_of_words = len(word_list)
        print ('Length', num_of_words)
        if num_of_words == 1:
            #get cities
            cities = gc.search_cities(event_loc,case_sensitive=False)
            print('Length of cities', cities)
            #country = gc.get_countries('GB')
            if len(cities) <= 0:
                return event_loc
            else:
                for x in range(len(cities)):
                    country_code = cities[x]['countrycode']
                    country_name = pytz.country_names[country_code]
                
                event_loc = event_loc + ' ' + country_name

        return event_loc

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
        titlewords = title.split()

        if len(titlewords) >= 3 and event_keyword in titlewords :
            return title
        else:

            for token in doc:
                title = ' '
                tokenid = token.i
                part = re.match("\d{1,}rd|\d{1,}th",str(token))
                if part != None:
                    print(part)
                    for sent in doc.sents:
                        for token in sent:
                            print(token.text, token.i - sent.start)
                            if token.i >= tokenid:
                                tokentext = token.text
                                title = title + ' ' + tokentext
                            #if tokentext == re.match("\(",str(token)):
                                if (token.i - sent.start) - tokenid == 10:
                                    break
                    # worked for x in range(tokenid, 10): 
                        # worked print([token.text for token in doc if token.i == x])
                        #token = token.next
                        #title = title + ' ' + token[token.i]
                        print("Title", title)
                        return(title)
                    

    # Method 3, use regex for event th and identify sentence
    except Exception as e:
        print(e)

if __name__ == "__main__":
    #simple
    #url = 'https://ubicomp.org/ubicomp2022/cfp/workshop-papers/'
    #url = 'https://tma.ifip.org/2022/'
    #url = 'https://www.marble-conference.org/marble2022-cfp'
    #url = 'https://tma.ifip.org/2021/'
    #url = 'https://www.marble-conference.org/marble2022'
    #url = 'http://infotheory.ca/bsc2020/'
    #url = 'http://hotspot.compute.dtu.dk/'
    #url = 'http://www.cs.columbia.edu/~hgs/nossdav/2020/'
    #url = 'https://sigmobile.org/mobicom/2022/'
    url = 'http://sbp-brims.org/2022/cfp/'

    #complex
    #url = 'https://petsymposium.org/' 
    #url = 'https://sigmobile.org/mobicom/2022/' 
    #url = 'https://www.sigsac.org/ccs/CCS2022/call-for/call-for-papers.html' 

    response = requests.get(url)
    if response.status_code == 404:
        print('The website is no longer')
    elif response.status_code == 200:
        print('The website is good')
        soup = BeautifulSoup(response.text, 'html.parser')
        clean_data = soup.get_text(" ")
        clean_data = clean_data.replace('\n',' ')
        clean_data = clean_data.replace('\r','')
        clean_data = clean_data.replace('\t','')
    else:
        print('Something went wrong with the website')


    nlp = spacy.load("en_core_web_sm")
    doc = nlp(clean_data)


    #different functions being tested

    # commeting the section for returning deadline dates for complex websites

    ''' 
    deadlines = date_test(doc)
    print('dealines i found', deadlines)
    if deadlines == {}:
        print ('No cycle')
    else:
        for key, value in deadlines.items():
            print('I am thanking God')
            doc_complex = nlp(str(value))
            simpledates = simple_date(doc_complex,nlp)
            #create_deadline(row_id,0,'None',' ',simpledates[0],'None',simpledates[1],simpledates[2],'Nil')
            
            print(simpledates)
            print('Please Work','row_id',0,str(key),str(value),simpledates[0],'None',simpledates[1],simpledates[2],'Nil')
            #create_deadline(row_id,0,str(key),str(value),'None','None','None','None','None')
    '''
    #timezone = get_timezone(doc)
    #print('Found time ', timezone)
    #country = get_country_test(doc)
    #print('country found', country)
    #country_in_live = get_location(doc)
    #print('Country in Live', country_in_live)

    titleintext = get_title(doc,url)
    print('title in text', titleintext)

    #simpledate = simple_date(doc,nlp)
    #if simpledate == None:
        #print('No dates')
    #else:
        #print(simpledate)
    #virtual = confirm_virtual(doc)
    #print(virtual)

    #datelist = extract_date()
    #print('Date List', datelist)
    #for i in range(4):
    #first_date = datelist[0]
        #dataidentified = print('Date ' + datetime.date.strftime(datelist[i], "%d %B %Y"))
        #print('This is a win',dataidentified)

                                               <div class="form-group">
                                                    <label for="date">Rebuttal Period</label>
                                                    <select name="rebuttal_period" class="dropdown">
                                                        {% for c in my_list %}
                                                        <option value={{c.rebuttal_period}}>{{c}}</option>
                                                        {% endfor %}
                                                    </select>                                                    
                                                </div>

                                                <div class="form-group">
                                                    <label for="date">Notification Date</label>
                                                    <select name="notification_date" class="dropdown">
                                                        {% for c in my_list %}
                                                        <option value={{c.notification_date}}>{{c}}</option>
                                                        {% endfor %}
                                                    </select>                                                     
                                                </div>

                                                <div class="form-group">
                                                    <label for="date">Camera Ready</label>
                                                    <select name="cameraready_date" class="dropdown">
                                                        {% for c in my_list %}
                                                        <option value={{c}}>{{c}}</option>
                                                        {% endfor %}
                                                    </select>                                                      
                                                </div>
