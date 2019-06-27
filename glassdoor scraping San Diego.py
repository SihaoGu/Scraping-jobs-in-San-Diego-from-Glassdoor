# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 20:40:20 2018

@author: 86151
"""

import urllib.request, urllib.error, urllib.parse
from urllib.request import urlopen
import time
import requests
from bs4 import BeautifulSoup
import re
import csv
import json
from time import sleep
import random
import numpy as np
from random import randint
site = 'https://www.glassdoor.com/Job/san-diego-business-analyst-jobs-SRCH_\
IL.0,9_IC1147311_KO10,26_IP1.htm'
site

def get_random_ua():
    random_ua = ''
    ua_file = 'assignment2/ua_file.txt'
    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_ua = lines[int(idx)].strip()
    except Exception as ex:
        print('Exception in random_ua')
        print(str(ex))
    finally:
        return random_ua

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

headers={'User-Agent':user_agent,} 

request=urllib.request.Request(site,None,headers) #The assembled request
response = urllib.request.urlopen(request)
html = response.read() 

soup = BeautifulSoup(html, "html5lib")

pages = []
for l in range(1,31):
    pages.append('https://www.glassdoor.com/Job/san-diego-business-analyst-\
                 jobs-SRCH_IL.0,9_IC1147311_KO10,26_IP'+ str(l)+ '.htm') 

# to get all the posting links from all search result pages
def get_job_links(soup):
    links = []
    for link in soup.find_all(class_ = "jobLink"):
        links.append('https://www.glassdoor.com'+link.get('href'))
    links = list(set(links))
    return(links)
    
# to open all pages
job_links = []

for i in range(0,len(pages)):
    request=urllib.request.Request(pages[i],None,headers) #The assembled request
    response = urllib.request.urlopen(request)
    html = response.read() 
    soup = BeautifulSoup(html, "html5lib")

    job_links.extend(get_job_links(soup))

# get job description
def get_job_content(soup):
    
    script = soup.find("script").get_text()
    script = script.replace('\n', ' ').replace('\t', ' ').replace("'", '"')
    myvars = re.search(r"window.gdGlobals\s*\|\|\s*\[({.*})\];", script).group(1);
    myvars = re.sub('\[\s*,', '[', myvars)
    myvars = json.loads(myvars)
    time.sleep(random.randint(0,5) + random.random())
    # find industry, employer, company size, title, city, state
    industry = myvars['employer']['industry']
    company = myvars['employer']['name']
    com_size = myvars['employer']['size']
    jobtitle = myvars['job']['jobTitle']
    city = myvars['job']['city']
    state = myvars['job']['state']
    time.sleep(random.randint(0,9) + random.random()) 
    # find expected salary
    est_sal = soup.find('h2', class_="salEst")
    if est_sal is None:
        est_sal = None
    else:
        est_sal = est_sal.get_text()
    
    # find JD
    text = soup.find(class_ = "jobDescriptionContent desc module pad noMargBot")
    text = text.get_text()
    text = ' '.join(text.split('.')[1:])
    
    #find company rating
    com_rating = soup.find(class_ = 'ratingNum')
    if com_rating is None:
        com_rating = None
    else:
        com_rating = com_rating.get_text()
    time.sleep(random.randint(0,5) + random.random()) 
    return([industry, company, com_size, jobtitle, city, state, est_sal, text,com_rating])



job_list = [['industry', 'company', 'com_size', 'jobtitle', 'city', 'state',\
             'est_sal', 'text','company rating']] 
# column names of the result
counter = 0
errcount = 0

# Get all the job postings out
for job in job_links:
    # track the progress of this loop
    print('overall count: ', counter, '\nprocessing link: ', job)
    headers={'User-Agent':get_random_ua(),}
    request = urllib.request.Request(job,None,headers) #The assembled request
    response = urllib.request.urlopen(request)
    html = response.read() 
    soup = BeautifulSoup(html, "html5lib")
    time.sleep(random.randint(0,9) + random.random())        
    # in case the posting is not in a format we expect, skip all the errors
    try:
        posting = get_job_content(soup)
        job_list.append(posting)

    except:
        # track how many errors happen when scrape
        errcount += 1
        print('errcount: ', errcount)
        
        # give up this posting and continue to get the next posting
        continue
    time.sleep(random.randint(0,9) + random.random())
    time.sleep(random.randint(0,4) + random.random()) 
    counter += 1
    
with open('San Diego.csv',  encoding='utf-8-sig',mode = 'w') as f:
    writer = csv.writer(f)
    writer.writerows(job_list)