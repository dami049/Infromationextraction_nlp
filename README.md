# Infromationextraction_nlp
Conference event retrieval system

The Conference event retrieval system allows users automatically retrieve relevant information from conference websites.
The application has two groups of users - the admin user and the application user. The admin user enters the website address for a conference website. The system automatically retrieves the event name, event title, acronym, event date, event location, deadlines (submission, notification, rebuttal, camera-ready) if available and an indication as to if the event would also be held online.

This project is my dissertation project as part of the requirements for the completion of an MSc in Artificial Intelligence. My interest in Natural Language processing motivated this project.. 


Tech Stack
NLP: spaCy (open-source library for advanced NLP processing) - https://spacy.io/, Tecoholic (Annotation) - https://tecoholic.github.io/ner-annotator/

Frontend: Python, HTML, CSS

Backend: SQLite, Python

Web framework: Flask

## Application Files

**./persistence/aggregrator.db:** 
This is the database that stores the application

**/persistence/crud.py** 
This contains the classes for interacting with the database (insert, update, delete, view))

**/persistence/model.py** 
Script that creates the database

**/persistence/database.py**
Manages the database connections, session and deleting tables

**/Static/..** 
Contains the static files for reading the web pages (CSS and javascript)

**/template/admin.htm** 
This is the ***** home page (frontend)

**/template/event.htm** 
This ** the application user home page (frontend)

**/template/event_update.htm** 
This is the details page that allows the admin review entries(frontend)

**/template/event_detail.htm** 
This shows the details of the event to the application user

**/main.py** 
This is the main python code that runs the application

**/n_processor.py** 
This is the main process engine that contains the functions that retrieve each of the attributes 

## Libraries used

**OS:** This module provides a portable way of using operating system dependent functionality.

**request:** The requests module allows the applicaiton send HTTP requests using Python

**datatime:** The datetime module supplies classes for manipulating dates and times.

**BeautifulSoup:** This is a library that makes it easy to scrape information from web pages. It sits atop an HTML or XML parser

**re:** 
A regular expression (or RE) specifies a set of strings that matches it; the functions in this module let applicaiton check if a particular string matches a given regular expression (or if a given regular expression matches a particular string, which comes down to the same thing)

**datefinder:** A python module for locating dates inside text.

**datatime:** The datetime module supplies classes for manipulating dates and times.

**flask:** A framework for building web apps

**sqlalchemy:**  library that facilitates the communication between Python programs and databases.



## Running application

To run application from an IDE like Phycharm or VSCode 
    1. Open folder/source code with prefer IDE 
    2. Run n_processor.py to create database and main.py to run the applicaiton

Run using: http://127.0.0.1:5000/admin or http://Localhost:5000/admin
