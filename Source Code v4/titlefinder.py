import requests
from bs4 import BeautifulSoup
import re
import metadata_parser

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

            span_value = edition_regex.span()
            print("Span Value", span_value)
            span_index = span_value[0]
            print("Span Index", span_index)
            # determine next start of the phrase
            if span_index > 5:
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
            else:
                try:
                    next_start_char = edition_regex.span()[1] + self.front
                except:
                    pass
                try:
                    string_to_scan = short_sentence[edition_regex.span()[0] + self.front]
                    print(f'Searched text 2: {string_to_scan}')
                    self.title_found.append({string_to_scan})
                except:
                    pass
            

        #exit()


#url = 'https://ubicomp.org/ubicomp2022/cfp/workshop-papers/' #- too many
#url = 'https://www.marble-conference.org/marble2022-cfp' #- non
#url = 'https://www.marble-conference.org/marble2022' #- worked
#url = 'https://sigmobile.org/mobicom/2022/' #- worked
#url = 'https://petsymposium.org/'
#url = 'https://ieeevr.org/2022/contribute/workshops/' #-worked
#url = 'https://weis2022.econinfosec.org/program/call-for-papers/'
#url = 'http://www.sis.pitt.edu/lersais/conference/tps/2021/calls.html'
url = 'http://sbp-brims.org/2022/cfp/'

html = requests.get(url).content
unicode_str = html.decode('utf8')
news_soup = BeautifulSoup(unicode_str, "html.parser")

clean_data = news_soup.get_text(" ")
clean_data = clean_data.replace('\n',' ')
clean_data = re.sub('\s{2,}',' ',clean_data)


td = GetTitle(clean_data)
title = td.find_title()

print("///////////  ", title)

if title == None:
    print("Use Old method")

