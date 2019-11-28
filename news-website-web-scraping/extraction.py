# website text extraction
import feedparser
import subprocess
import os
import math
import re
import html2text
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
import time
import datetime
import articleDateExtractor


# globally set driver to use later for taking screenshot of homepage
# recommendation: Selenium is deprecated, use another package in the future
driver = webdriver.PhantomJS()
driver.set_window_size(1024, 768)


# Display article_data table from the database
def display_article_data(conn):
        cur = conn.cursor()
        cur.execute("SELECT * FROM article_data")
        rows = cur.fetchall()
        for row in rows:
                print(row)


# RSS Feed extraction: not in use, but could be helpful later
def rss_feed(url):
        rss = feedparser.parse(url)
        cols = rss.entries[1].keys()
        print('RSS info available', cols)

        print('\nNumber of RSS posts : ' + str(len(rss.entries)) + '\n\n')

        for i in range(1,len(rss.entries)):
                print('Title: ' + str(rss.entries[i].title) + '\n' + 'Link: ' + 
                        str(rss.entries[i].link) + '\n\n')
        return


# Checks that a url is valid and does not return an error
def is_valid_url(url):
        try:
                url_page = requests.get(url)
        except:
                return False
        return True


# Checks that a Twitter account for the given handle exists
def is_valid_handle(handle):
        try:
                url_page = requests.get('https://twitter.com/' + handle)
        except:
                return False
        return True


# Takes a screenshot of home page
def save_screenshot(url, direct_site, site_key):
        driver.save_screenshot(direct_site + site_key + '.png')


# get plain text of an article
def get_preview(soup_article):
        h = html2text.HTML2Text()
        h.ignore_links = True # comment out if you want links
        h.ignore_images = True # comment out if you want images
        return h.handle(str(soup_article).decode('utf-8'))


# Create local directories for a given site
def save_homepage(url, site_key):
        if not os.path.exists(os.path.join(os.path.dirname(__file__), site_key+'/')):
                # create the local folder for the site if it does not already exist
                os.makedirs(os.path.join(os.path.dirname(__file__), site_key+'/'))
        driver.get(url)
        direct_site = os.path.join(os.path.dirname(__file__), site_key + '/')
        # save screenshot of homepage to {site_key}/
        save_screenshot(url, direct_site, site_key)
        page = requests.get(url)
        # parse homepage and save as HTML
        soup = BeautifulSoup(page.text)
        # save parsed homepage to {site_key}/
        w = open(direct_site + 'parsedHomepage.txt', 'w+')
        w.write(str(soup))
        w.close()
        # return soup of the homepage
        return soup


# Takes a list of article links, loops through and saves HTML in a text file for each
def write_articles(url, articleLinks, site_key, folder, cur, conn):
        # keep count variable for identification of articles in their names
        # note: this implementation rewrites the folder every time - can be changed later to save all history
        count = 1
        for article in articleLinks:
                # loop through the list of article links stripped from homepage
                if (is_valid_url(article)):
                        try:
                                page_article = requests.get(article)
                        except:
                                print(article + " caused a problem!")
                                continue # moves on to the next article link
                        soup_article = BeautifulSoup(page_article.text)
                        # saves the HTML to the folder with the given naming convention
                        w = open(folder + site_key + str(count) + '.txt','w+')
                        w.write(str(soup_article))
                        w.close()
                        count += 1
        # call the authors function to save author(s) + Twitter handle(s) to database
        # this function does the majority of the extraction work
        insert_authors_articles(url, site_key, articleLinks, cur, conn)


# Scrapes the homepage and finds all (potential) article links
def find_articles(url, site_key, soup, cur, conn):
        # create directory if it doesn't exist
        folder = os.path.join(os.path.dirname(__file__), site_key + '/articles/')
        if not os.path.exists(folder):
                os.makedirs(folder)
        else: # clear the directory to write new files
                for article in os.listdir(folder):
                        file_path = os.path.join(folder, article)
                        try:
                                if os.path.isfile(file_path):
                                        os.unlink(file_path)
                        except Exception as e:
                                print(e)

        if site_key == 'cnn': # implementation as of March 2019
                # for CNN: the div class "cd__content" usually holds the a href for article
                # but this is not shown in the html.parser, instead they're in {"uri": /link/}
                # note: they're all under {articleList: [list of articles]}
                # use regular expressions to extract url value for 'uri' attribute:
                articleList = re.search('(?<=("articleList":)).+?(?=}])', str(soup)).group(0)
                # get all the urls
                articleLinks = re.findall('((?<=("uri":")).+?(?="))', articleList)
                articleLinks = [x for x, y in articleLinks]
                articleLinks = [(url+x) if x[0]=='/' else x for x in articleLinks]

                # go into each of these links and get links / references, also save and clean text
                # save each article to {site_key}/articles/, author info to db
                write_articles(url, articleLinks, site_key, folder, cur, conn)
        
        elif site_key == 'foxnews': # implementation as of March 2019
                # Fox News is formatted differently from CNN, some articles may have been missed
                # took the ones that had header class="title"<a href = "url"></a>
                # print(str(soup))
                articleList = re.findall(r'class="title"><a href="(.+?)">', str(soup))
                # print('articleList: ')
                # print(articleList)
                # get rid of all special characters at beginning of string
                articleLinks = [re.sub(r'^\W+', 'https://', x) for x in articleList]
                articleLinks = [x for x in articleLinks if "www." in x]
                # print(articleLinks)
                # save each article to {site_key}/articles/, author info to db
                write_articles(url, articleLinks, site_key, folder, cur, conn)

        else:
                # implementation as of April 2019
                # create generalized process for other sites (keeping CNN and Fox News because already implemented)
                # go from specific -> general, FUTURE WORK: keep adding footprints here
                if (url == "https://cnbc.com/politics"):
                        url = "https://cnbc.com" # cnbc specific case because of how the links are extracted
                if (len(re.findall('((?<=("type":"article","link":")).+?(?="))', str(soup))) != 0):
                        articleList = re.findall('((?<=("type":"article","link":")).+?(?="))', str(soup))
                elif (len(re.findall('((?<=(href=")).+?(?=\stitle=))', str(soup)))):
                        articleList = re.findall('((?<=(href=")).+?(?="\stitle=))', str(soup))
                elif (len(re.findall('((?<=(href=")).+?(?=">))', str(soup)))):
                        articleList = re.findall('((?<=(href=")).+?(?=">))', str(soup))
                # clean article list
                articleList = [x for x,y in articleList]
                # remove any backslashes / misc. characters
                articleList = [x.replace("\\u002F", "/") for x in articleList]
                articleList = [x.replace("\\", "/") for x in articleList]
                articleList = [x.replace("//", "/") for x in articleList]
                articleLinks = [(url+x) if (x[0]=='/') else x for x in articleList]

                # print(articleLinks)

                # call write_articles to save all the content from each link to a file in the directory
                write_articles(url, articleLinks, site_key, folder, cur, conn)


# Scrapes all the information from each of the articles and adds to database
def insert_authors_articles(url, site_key, articleLinks, cur, conn):
        # iterate through the site_key's directory of articles
        for article in articleLinks:
                # check that the link is valid before opening and saving
                # if invalid, skip to next URL
                if not is_valid_url(article):
                        continue
                
                page_article = requests.get(article)
                soup_article = BeautifulSoup(page_article.text)
                
                if site_key == 'cnn': # implementation as of March 2019, specific to CNN
                        # get title of article
                        title = re.search('(?<=(<title>)).+?(?=</title>)', str(soup_article))
                        if (title != None):
                                title = title.group(0)
                        else:
                                continue
                        # get category of article
                        category = re.search('(?<=(meta content="https://www.cnn.com/)).+?(?=")', str(soup_article))
                        if (category != None):
                                category = category.group(0)
                                if (category[0:6] == "videos"):
                                        category = category[7:].split('/')[0]
                                        if (category[0].isdigit()):
                                                category = None
                                else:
                                        category = category[11:].split('/')[0]
                        # get the date it was written
                        date_written = articleDateExtractor.extractArticlePublishedDate(article)
                        # note: the publish times seem to be fairly inaccurate, only take year/month/day
                        date_written = date_written.strftime('%Y-%m-%d')
                        # this is the current date, to check if date written extracted correctly
                        ts = time.time()
                        date_current = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                        # note: the following date/year cutoff can change - I'm assuming that if the year is
                        # older than 5 years, it likely would not have shown up on the front page 
                        # if date is not in a valid range [date_cutoff_low, current_time)
                        date_cutoff_low = 2015
                        if (date_written[0:3] < date_cutoff_low or date_written > date_current):
                                date_written = None # date will be inserted as NULL
                        # get content of the article
                        content = get_preview(soup_article)

                        # extract author string from HTML
                        # clean to get one name (take everything after 'by', separate by 'and')
                        # Note: make sure 'by' and 'and' are NOT case-sensitive
                        authorList = re.search('(?<=("author":")).+?(?=")', str(soup_article))
                        if (authorList != None): # in this I'm only adding to database articles with authors
                                authorList = authorList.group(0)
                                authors = re.split('by ', authorList, flags=re.IGNORECASE)
                                if len(authors) >= 2:
                                        authors = authors[1:]
                                authors = re.split(' and ', ','.join(authors), flags=re.IGNORECASE)
                                authors = re.split(',', ','.join(authors))
                                # special case for CNN - CNN will show up in the author list
                                authors = [x for x in authors if "CNN" not in x]
                                # additional cleaning
                                authors = [x for x in authors if x is not '"' and x is not '']

                                # format for CNN: "profileUrl":"/profiles/*****"
                                links = re.findall('((?<=("profileUrl":")).+?(?="))', str(soup_article))
                                links = [x for x,y in links]
                                links = [(url+x) if x[0]=='/' else x for x in links]

                                # if the length of the authors list equals list of available links and it's not empty
                                # note: I have this equality restriction imposed for simplicity of making sure authors match up with profiles
                                # this is further explained in report
                                if (len(authors) == len(links) and len(authors) != 0):
                                        # store everything in a dictionary - only did this for CNN, leaving in case it's helpful later
                                        authorInfo = {}
                                        for i in range(0,len(links)):
                                                # match author with link
                                                author = authors[i]
                                                authorInfo[author] = {}
                                                authorInfo[author]["link"] = links[i]
                                                if (is_valid_url(links[i])):
                                                        author_page = requests.get(links[i])
                                                        author_soup = BeautifulSoup(author_page.text)
                                                        handle = author_soup.find('div', attrs={'class': 'social-description__follow-icon social-description__follow-icon--twitter cnn-icon'})
                                                        if (handle is not None):
                                                                handle = handle.find('a')['href']
                                                                handle = handle[14:]
                                                                if (handle[0] == '@' or handle[0] == '/'):
                                                                        handle = handle[1:]
                                                                if '.' in handle: # this is not a valid handle!
                                                                        handle = None
                                                        if (is_valid_handle(handle)):
                                                                authorInfo[author]["handle"] = handle
                                                        else:
                                                                authorInfo[author]["handle"] = None
                                                else:
                                                        authorInfo[author]["handle"] = None

                                        # loop through dictionary and add to database
                                        for author in authorInfo:
                                                # for now, only insert if a handle exists, since we're using it as the primary key
                                                if (authorInfo[author]["handle"] is not None):
                                                        # add all extracted values into article_data
                                                        cur.execute('INSERT OR IGNORE INTO article_data (article_link, article_date, author_name, author_handle, site, article_title,'
                                                        ' category, text_preview) VALUES (?,?,?,?,?,?,?,?)', (article, date_written, author, authorInfo[author]["handle"], site_key, title, category, content))

                else: # any other website - generalized implementation
                        if (url == "https://cnbc.com/politics"):
                                url = "https://cnbc.com" # cnbc specific case, because I used the politics section
                        # FIRST: find handle on the article page, if it exists
                        # get the date it was written
                        date_written = articleDateExtractor.extractArticlePublishedDate(article)
                        if date_written != None:
                                # note: the publish times seem to be fairly inaccurate, only take year/month/day
                                date_written = date_written.strftime('%Y-%m-%d')
                                # this is the current date, to check if date written extracted correctly
                                ts = time.time()
                                date_current = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                                # note: the following date/year cutoff can change - I'm assuming that if the year is
                                # older than 5 years, it likely would not have shown up on the front page 
                                # if date is not in a valid range [date_cutoff_low, current_time)
                                date_cutoff_low = 2015
                                if (date_written[0:3] < date_cutoff_low or date_written > date_current):
                                        date_written = None # date will be inserted as NULL
                        # get content of the article
                        content = get_preview(soup_article)
                        # initialize empty lists for handles and authors
                        handleList = []
                        authorList = []
                        # footprints listed below for handle extraction - can add more for higher success rate
                        if (len(re.findall('(?i)((?<=(on Twitter <a href="https://twitter.com/)).+?(?=[^\w_]))', str(soup_article))) != 0):
                                handleList = re.findall('(?i)((?<=(on Twitter <a href="https://twitter.com/)).+?(?=[^\w_]))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=(on Twitter @)).+?(?=[^\w_]))', str(soup_article))) != 0):
                                handleList = re.findall('(?i)((?<=(on Twitter @)).+?(?=[^\w_]))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=("twitter":")).+?(?="))', str(soup_article))) != 0):
                                handleList = re.findall('(?i)((?<=("twitter":")).+?(?="))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=(twitter-url"><a href=")).+?(?="))', str(soup_article))) != 0):
                                handleList = re.findall('(?i)((?<=(twitter-url"><a href=")).+?(?="))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=(:"https://twitter.com/)).+?(?="))', str(soup_article))) != 0):
                                handleList = re.findall('(?i)((?<=(:"https://twitter.com/)).+?(?="))', str(soup_article))
                        # SECOND: find the author name on the article page, if it exists
                        # make sure that handle matches up with authors
                        # using (?i) is important to ignore case-sensitivity
                        if (len(re.findall('(?i)((?<=("fullname":")).+?(?="))', str(soup_article))) != 0):
                                authorList = re.findall('(?i)((?<=("fullname":")).+?(?="))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=("authorname":")).+?(?="))', str(soup_article))) != 0):
                                authorList = re.findall('(?i)((?<=("authorname":")).+?(?="))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=("author":{"name":")).+?(?="))', str(soup_article))) != 0):
                                authorList = re.findall('(?i)((?<=("author":{"name":")).+?(?="))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=("author":")).+?(?="))', str(soup_article))) != 0):
                                authorList = re.findall('(?i)((?<=("author":")).+?(?="))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=("author":\s")).+?(?="))', str(soup_article))) != 0):
                                authorList = re.findall('(?i)((?<=("author":\s")).+?(?="))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=("url" rel="author">)).+?(?=</a>))', str(soup_article))) != 0):
                                authorList = re.findall('(?i)((?<=("url" rel="author">)).+?(?=</a>))', str(soup_article))
                        elif (len(re.findall('(?i)((?<=("Person","name":")).+?(?="))', str(soup_article))) != 0):
                                authorList = re.findall('(?i)((?<=("Person","name":")).+?(?="))', str(soup_article))
        
                        # remove duplicates if they exist
                        authorList = [x for x,y in authorList]
                        authorList = list(dict.fromkeys(authorList))

                        # clean authors
                        newAuthorList = []
                        if (len(authorList) != 0): # in this project I'm only adding articles with authors
                                for i in range(len(authorList)):
                                        print(authorList[i])
                                        authors = re.split('by ', authorList[i], flags=re.IGNORECASE)
                                        if len(authors) >= 2:
                                                authors = authors[1:]
                                        authors = re.split(' and ', ','.join(authors), flags=re.IGNORECASE)
                                        authors = re.split(',', ','.join(authors))
                                        for j in range(len(authors)):
                                                newAuthorList.append(authors[j])
                        authorList = newAuthorList

                        # if handle has not been found yet, go into author profile page
                        if len(newAuthorList) != len(handleList):
                                # find author profile page if it exists, go find handle there
                                # can and should add more footprints here - many other ways to get the author's profile page
                                authorLinks = []
                                handleList = []
                                if (len(re.findall('(?i)((?<=(href="/author/)).+?(?="))', str(soup_article))) != 0):
                                        authorLinks = re.findall('(?i)((?<=(href="/author/)).+?(?="))', str(soup_article))
                                        authorLinks = [url+"/author/"+x for x,y in authorLinks]
                                elif (len(re.findall('(?i)((?<=(<span><a href=")).+?(?="))', str(soup_article))) != 0):
                                        authorLinks = re.findall('(?i)((?<=(<span><a href=")).+?(?="))', str(soup_article))
                                        authorLinks = [x for x,y in authorLinks]
                                # add url if not included already
                                authorLinks = [(url+x) if x[0]=='/' else x for x in authorLinks]
                                # visit each link
                                for i in range(len(authorLinks)):
                                        # only open if link is valid
                                        if is_valid_url(authorLinks[i]):
                                                author_page = requests.get(authorLinks[i])
                                                soup_author = BeautifulSoup(author_page.text)
                                                handleResults = []
                                                # search in the HTML for the author page to find twitter handle
                                                if (len(re.findall('(?i)((?<=(on Twitter <a href="https://twitter.com/)).+?(?=[^\w_]))', str(soup_author))) != 0):
                                                        handleResults = re.findall('(?i)((?<=(on Twitter <a href="https://twitter.com/)).+?(?=[^\w_]))', str(soup_author))
                                                elif (len(re.findall('(?i)((?<=(on Twitter @)).+?(?=[^\w_]))', str(soup_author))) != 0):
                                                        handleResults = re.findall('(?i)((?<=(on Twitter @)).+?(?=[^\w_]))', str(soup_author)) 
                                                elif (len(re.findall('(?i)((?<=("twitter":")).+?(?="))', str(soup_author))) != 0):
                                                        handleResults = re.findall('(?i)((?<=("twitter":")).+?(?="))', str(soup_author))
                                                elif (len(re.findall('(?i)((?<=(user\?screen_name=)).+?(?="))', str(soup_author))) != 0):
                                                        handleResults = re.findall('(?i)((?<=(user\?screen_name=)).+?(?="))', str(soup_author))
                                                elif (len(soup_author.find_all('span',attrs={'class': 'icon'})) != 0):
                                                        # might be hidden in icon tag
                                                        spans = soup_author.find_all('span',attrs={'class': 'icon'})
                                                        handleResults = re.findall('(?i)((?<=(<a href="https://twitter.com/)).+?(?="))', str(soup_author))
                                                
                                                if len(handleResults) != 0:
                                                        for j in range(len(handleResults)):
                                                                handleList.append(handleResults[j])
                        # clean handleList
                        handleList = [x for x,y in handleList if x != "Twitter"]
                        handleList = [x.replace("\\u002F", "/") for x in handleList]
                        for x in range(len(handleList)):
                                temp = handleList[x]
                                if temp[0] == '@':
                                        handleList[x] = temp[1:]
                                if len(temp.split(".com/",1)) > 1:
                                        handleList[x] = handleList[x].split(".com/",1)

                        if len(authorList) == 0:
                                continue # break out of loop, no need to continue
                        if len(authorList) != len(handleList):
                                continue # break out of loop

                        # find title and category of article
                        # TITLE FINDER: (title can be null) - more conditions can be added later, this finds first title tag
                        title = soup_article.title.string
                        # CATEGORY FINDER: (title can be null) - more conditions can (and should) be added later
                        if (re.search('(?i)((?<=(category":{"title":")).+?(?="))', str(soup_article)) != None):
                                category = re.search('(?i)((?<=(category":{"title":")).+?(?="))', str(soup_article)).group(0).lower()
                        elif (re.search('(?i)((?<=(.com/)).+?(?=/))', article) != None):
                                category = re.search('(?i)((?<=(.com/)).+?(?=/))', article).group(0).lower()
                                # only add if it does not include a special symbol (we are assuming this means it's one word)
                                if category != "":
                                        if not re.match("^[a-zA-Z0-9]*$", category):
                                                category = None
                        else:
                                category = None
                        for author_index in range(len(authorList)):
                                author_name = authorList[author_index]
                                author_handle = handleList[author_index]
                                if (is_valid_handle(author_handle)): # only add if handle is valid
                                        # add to database if all necessary information is available
                                        cur.execute('INSERT OR IGNORE INTO article_data (article_link, article_date, author_name, author_handle, site, article_title,'
                                        ' category, text_preview) VALUES (?,?,?,?,?,?,?,?)', (article, date_written, author_name, author_handle, site_key, title, category, content))
                                



### MAIN ###

def main():
        # use this connection for SQL queries
        conn = sqlite3.connect('extraction_db.sqlite')
        conn.text_factory = str
        cur = conn.cursor()

        # define sites and their site "keys": these keys are important for creating directories
        # I also used these site keys as identification in the database
        sites = ['https://cnn.com', 'https://foxnews.com','https://news.yahoo.com', 'https://cnbc.com/politics', 'https://time.com', 'https://thehill.com' ]
        site_keys = ['cnn', 'foxnews', 'yahoonews', 'cnbc', 'time', 'thehill'] # site keys are the unique ID
        # below code, commented out, is for individual testing of sites
        # site = sites[5]
        # site_key = site_keys[5]

        # loop through sites and their identifying site keys
        for idx in range(len(sites)):
                site = sites[idx]
                site_key = site_keys[idx]
                if not is_valid_url(site):
                        print(site + " cannot be accessed.")
                        continue
                # save homepage as soup variable, also save screenshot
                soup = save_homepage(site, site_key)
                # use homepage to find articles and then insert them into database
                # currently, this function calls other functions within it,
                # we can change it in the future so it calls them one at a time,
                # independent of one another
                find_articles(site, site_key, soup, cur, conn)
        # print out current state of table after insertions
        display_article_data(conn)

        # MANUAL: export data to csv through sqlite, then upload to Google Cloud bucket

        # make sure to commit so the changes to the database remain
        conn.commit()
        conn.close()

main()