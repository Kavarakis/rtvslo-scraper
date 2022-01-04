#!/usr/bin/env python
# coding: utf-8

# # Project 1: Web scraping and basic summarization
# *University of Ljubljana, Faculty for computer and information science* <br />
# *Course: Introduction to data science*

# In this Project you need to implement missing parts of this Jupyter notebook. All the code in the notebook must be reproducible and runnable, so include instructions for the environment setup or other specifics needed to run the notebook. The overview of the repository and setup should be put to README.md
# 
# The idea of this Project is to automatically retrieve structured data from pages [rtvslo.si](https://www.rtvslo.si) or [24ur.com](https://www.24ur.com). 

# ## Environment setup

# Write instructions how to setup the environment to run this notebook, which libraries are installed, etc. Also provide installation sources.
# 
# `TODO: environment setup description`

# In[1]:


# Load all the libraries needed for running the code chunks below
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
from os import path
get_ipython().run_line_magic('load_ext', 'memory_profiler')


# In[2]:


# CONSTANTS
WEB_DRIVER_LOCATION = "/home/kavarakis/projects/fri/ids/project-1-Kavarakis-1/chromedriver"
NO_ARTICLES=4
TIMEOUT = 5
filename = 'data.json'


# In[3]:


def save_json(data):
    # Check if file exists
    if path.isfile(filename) is False:
        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump([data],
                      outfile,
                      indent=4,
                      sort_keys=True,
                      ensure_ascii=False)
    else:
        arr = json.load(open(filename))
        with open(filename, 'w', encoding='utf-8') as outfile:
            arr.append(data)
            json.dump(arr,
                      outfile,
                      indent=4,
                      sort_keys=True,
                      ensure_ascii=False)
            del arr
    print('Successfully appended to the JSON file')


# In[13]:


def get_comment(url):
    chrome_options = Options()
    chrome_options.add_argument('user-agent=Mozilla/5')
    print(f"Retrieving page | URL: {url}")
    driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)
    driver.get(url)
    time.sleep(TIMEOUT)
    try:
        cookies = driver.find_element(By.XPATH,
                                      '//a[contains(text(),"Strinjam se")]')
        cookies.click()
    except:
        print('Cookies approval failed!')
    time.sleep(2)
    try:
        comms = driver.find_element(By.XPATH,
                                    '//*[@class="link-show-comments"]')
        comms.click()
    except:
        print('Comments cannot be opened!')

    time.sleep(2)
    try:
        while(1):
            show_more = driver.find_element(
                By.XPATH, '//button[contains(text(),"Prikaži več")]')
            show_more.click()
            time.sleep(1)
    except:
        print("Does not have extra comments!")
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    comments = []
    for c in soup.find_all('div', class_='comment'):
        comment_text = ''
        if (c.find('p')):
            comment_text = c.find('p').text
        comment_author = ''
        if (c.find('ul', class_='comment-header-meta-text')):
            comment_author = c.find('ul',
                                    class_='comment-header-meta-text').find(
                                        'a', class_='profile-name').text
        if (comment_text != '' and comment_author != ''):
            comments.append({"user": comment_author, "comment": comment_text})
    driver.close()
    return comments


# ## Web scraping

# News portals generally provide a search functionality to search for news of interest. Your goal is to (a) programatically open a news site (rtvslo.si or 24ur.com), (b) enter query term `koronavirus`, (c) iterate through all the results and (d) parse each news article.
# 
# An example of Web pages from rtvslo.si:
# 
# <table>
#     <tr>
#         <td style="text-align: left;">rtvslo.si search results page</td>
#         <td style="text-align: left;">rtvslo.si news article page</td>
#     </tr>
#     <tr>
#         <td><img src="./rtvslo1.png" /></td>
#         <td><img src="./rtvslo2.png" /></td>
#     </tr>
# </table>
# 
# Export the extracted data in a JSON format. Also define the schema of your data, for example as follows:
# 
# ```
# [
#   {
#     "type": "news",
#     "author": "Ai. Ma.",
#     "datetime_published": "20. oktober 2021 22:53 CET",
#     "title": "Lejko Zupanc: Starost ljudi, ki potrebujejo najbolj invazivno podporo, se znižuje",
#     "subtitle": "Pogovor s strokovnjakinjo v Odmevih",
#     "headline": "Strokovnjaki se bojijo mrzlih in prazničnih dni, ko se bodo ljudje več družili v zaprtih prostorih in manj prezračeva...",
#     "content": "Podatki o širjenju virusa niso dobri. Kakšne so trenutno razmere na vaši kliniki? 
# Trenutne razmere so nekje na robu zmogljivosti, ki smo jih predvideli za covidne bolnike, tako v enoti intenzivne ter ...",
#     "tags": ["Novi koronavirus", "Covid-19", "Tatjana Lejko Zupanc"]
#     "comments": [
#         {
#             "user": "anonymous",
#             "comment": "Upajmo, da bo vse ok ..."
#         }, ...
#     ]
#     
#   }, 
#   {
#     ...
# ]
# ```
# 
# Schema could be defined also using [JSON Schema guidelines](https://json-schema.org/).

# `TODO: definition and short description of JSON data schema of the extracted data.`

# Proposed structure of the implementation is below. You can also import code from the accompanying *.py* files in the repository, so the code is clearer or organize code completely by yourself.

# In[14]:


def load_page(url):
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5'})
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


# In[15]:


# Implement news article page parsing
def parse_news_article(url):
    print(url)

    content = load_page(url)
    try:
        
        data = content.find('div', class_='news-container')
        author_name = data.find('div', class_='author-name').text
        publish_meta = data.find('div', class_='publish-meta').text
        datetime = (publish_meta.strip().splitlines()[0]).replace('ob ', '')
        datetime += ' CET'
        title = data.find('h1').text
        subtitle = data.find('div', class_='subtitle').text
        headline = data.find('p', class_='lead').text
        body = data.find('article', class_='article')
        content = "\n".join([i.text for i in body.find_all('p')])
        footer = data.find('div', class_='article-footer')
        tags = [i.text for i in footer.find_all('a', class_='tag')]
        comments = get_comment(url)
        _dict = {
            "type": "news",
            "author": author_name,
            "datetime_published": datetime,
            "title": title,
            "subtitle": subtitle,
            "headline": headline,
            "content": content,
            "tags": tags,
            "comments": comments
        }
        return _dict
    except AttributeError as err:
        print(f"Error for {url}: ",err)
        return {}


# In[16]:


def get_article_links(html):
    links = []
    r = BeautifulSoup(html, "html.parser")
    data = r.find(id='main-cointaner')
    news = r.find_all('div', class_='md-news')
    for art in news:
        res = art.find('a', 'image-link')['href'].strip()
        
        if res == 'https://www.rtvslo.si/zdravje/novi-koronavirus':
            return []
        res = 'https://www.rtvslo.si' + res
        links.append(res)
    return links


# In[17]:


def get_links(url='https://www.rtvslo.si'):
    links = []
    chrome_options = Options()
    chrome_options.add_argument('user-agent=Mozilla/5')
    chrome_options.add_argument("window-size=1200,800")
    print(f"Retrieving page | URL: {url}")

    driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)
    driver.get(url)
    time.sleep(2)
    try:
        cookies = driver.find_element(By.XPATH,
                                      '//a[contains(text(),"Strinjam se")]')
        cookies.click()
    except:
        print('Cookies approval failed!')
    time.sleep(2)
    _input = driver.find_element_by_id('header-search-input')
    _input.send_keys("koronavirus")
    _input.submit()
    i=0
    while (1):

        links += get_article_links(driver.page_source)
        plinks = driver.find_elements_by_xpath('//a[@class="page-link"]')
        page_link_texts = driver.find_elements_by_xpath(
            '//span[@class="sr-only"]')
        if page_link_texts.pop().text == 'Nazaj':
            break
        if(i>NO_ARTICLES):
            break
        plinks.pop().click()
        time.sleep(1)
        if(i%10 == 0):
            print('links:', len(links))
        i+=10
    driver.close()
    return links


# In[18]:


# Implement parsing, data merging and final representation

def search():
    links = get_links()
    print(f'Retrieved {len(links)} links!')
    data = []
    for i,l in enumerate(links):
        print(f"Getting data for: {l}")
        _dict = parse_news_article(l)
        save_json(_dict)
        if i%10 == 0:
            print(f"{i} articles scraped.")
    return data


# In[19]:


data = search()


# In[ ]:


with open(filename) as output:
    print(len(json.load(output)))


# In[ ]:


# Implement search results page parsing


def parse_search_results(url):
    ...
    return results, next_page_url


# In[ ]:


# Main program and data export into a JSON

MAIN_URL = "https://www.rtvslo.si"

data = search()
# Save data to UTF-8 encoded JSON
...


# ## Basic summarization
# 
# Prepare and show at least five basic visualizations of the extracted data as presented in the chapter *Summarizing data - the basics* of the course's e-book. Explain each visualization of the data.

# In[ ]:


# Read data from JSON

data = ...


# ### Visualization 1
# 
# `TODO: name the visualization and describe it`

# In[ ]:


# Visualization 1 code

...


# ### Visualization 2
# 
# `TODO: name the visualization and describe it`

# In[ ]:


# Visualization 2 code

...


# ### Visualization 3
# 
# `TODO: name the visualization and describe it`

# In[ ]:


# Visualization 3 code

...


# ### Visualization 4
# 
# `TODO: name the visualization and describe it`

# In[ ]:


# Visualization 4 code

...


# ### Visualization 5
# 
# `TODO: name the visualization and describe it`

# In[ ]:


# Visualization 5 code

...

if __name__ == '__main__':
    data = search()