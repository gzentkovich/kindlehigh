#!/usr/bin/env python
"""Kindle highlights downloader

Download the highlights stored on every user's Kindle book and dump them to a file. 

"""

__version__ = "1.0"
__license__ = "BSD"
__copyright__ = "Copyright 2012, Luciano Fiandesio"
__author__ = "Luciano Fiandesio <http://fiandes.io/>"

import re
import sys
from bs4 import BeautifulSoup
from optparse import OptionParser
import mechanize


xstr = lambda s: s or ""

def printx(str,f):
    f.write(str +'\n')

def getOptions():  
   arguments = OptionParser()  
   arguments.add_options(["--email", "--password"])  
   return arguments.parse_args()[0]  

def printHighlights(resp,file):

    soup = BeautifulSoup(resp.read())
    title = soup.find("span", {"class":'title'})
    
    if title:
        book_title = xstr(title.string).strip()
        print "::: Processing %s" % book_title
        printx ("# " + book_title,file)
        printx ("## " + xstr(soup.find("span", {"class":'author'}).string).strip(), file)

        for highlight in soup.findAll("span", {"class": "highlight"}):
            printx ("- " + highlight.string.encode('utf-8'),file)

        printx ("\r\n",file)

if __name__ == "__main__":
    f = open('kindle.md','w')

    options = getOptions()
    # Browser
    br = mechanize.Browser()

    br.set_handle_robots(False)  

    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    try:
        sign_in = br.open("https://kindle.amazon.com/your_highlights")  
        sign_in.set_data(re.sub('<!DOCTYPE(.*)>', '', sign_in.get_data()))      
        
        br.set_response(sign_in)
        br.select_form(name="signIn")  
        br["email"] = options.email  
        br["password"] = options.password   
        
        resp = br.submit()
        print "::: Logging in to Amazon"
        printHighlights(resp,f)
        while True:
            resp = br.follow_link(text='Next Book')
            printHighlights(resp,f)
    except mechanize._mechanize.LinkNotFoundError:
        # Ignore this exceotion
        print "::: No more books"
    except Exception, e:
        print >>sys.stderr, "Error logging in to AWS"
        raise


