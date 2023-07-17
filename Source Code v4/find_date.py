import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import datefinder
import dateutil.parser as dparser

globalfds = []
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
                fds = regex.group()
                print('///FDS', fds)
                #print(f'Found date: {regex.group()}\n')
                self.date_found.append(fds)
                globalfds.append(fds)

        #return 

    def extract_date(self):
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
        
    
        # date_pattern = "^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}$"
        re.match(date_pattern, '12/12/2022')  # Returns Match object

        # Extract date from a string
        date_extract_pattern = "[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}"
        re.findall(date_extract_pattern, 'I\'m on vacation from 1/18/2021 till 1/29/2021')  # returns ['1/18/2021', '1/29/2021']



url = 'https://www.sigsac.org/ccs/CCS2022/call-for/call-for-papers.html'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

clean_data = soup.get_text(" ")
clean_data = clean_data.replace('\n',' ')
clean_data = re.sub('\s{2,}',' ',clean_data)
#print(clean_data)

def dateconverter(date):

    date_match = datefinder.find_dates(str(date))
    print("Date match", date_match)


    convert_dates = []
    for i in date:
        print("iiiiiiiiiiii",i)
        convert_dates.append((datetime.strptime('January 14, 2022', "%d %B %Y")))

    final_dates = set(convert_dates)

    print("Final Dates", final_dates)
    print('\n')
    print('\n')
    
    return final_dates



td = TrapDates(clean_data)
date = td.extract_date()

print('Global FDS',globalfds)
received_dates = dateconverter(globalfds)


#print("///////////  ", received_dates)

