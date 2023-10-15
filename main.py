from tkinter import *
from tkinter import ttk
import requests as r
import sys
import os
import argparse
from bs4 import BeautifulSoup


def main(url, script):

    website_status = has_website_changed(url, script)
    if website_status == 0:
        print("Change to the website has occurred")
    elif website_status == 1:
        print("Change has not occurred")
    elif website_status == 2:
        print("First time site has entered cache")
    else:
        print("Some error prevented cache")

def clean_url(url):
    if url.startswith('http://') == False:
        url = 'http://' + url


def check_status(url):
    response = r.get(url)
    print(response.status_code)
    return r.status_codes

def has_website_changed(url, script):

    # headers and request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36', 'Cache-Control': 'no-cache'}
    response = r.get(url, headers=headers)

    # check if good response
    if response.status_code != 200:
        print("Weird response ...  " + str(response.status_code) + " check that url was entered correctly and try again.")
        return -1

    response_body = response.text

    # processing for easier file naming. Could make in to a seperate function.
    url = url.replace("https://", "")
    url = url.replace("http://", "")
    url = url.replace(".com", "")
    url = url.replace("www.", "")
    url = url.replace(".org", "")
    # cut the tailing slash
    url = url.replace("/", "")

    # cleans html
    response_Soup = clean_html(response_body, script)
    response_body = response_Soup.prettify()


    # opens file
    if os.path.isfile("./"+ url + ".txt"):
        with open('./' + url + ".txt", 'r', encoding='utf-8') as f:
            cache = f.read()

            # compares the strings of responses.
            if response_body != cache:
                # Website changed, make cache of new and then return 0.
                with open('./' + url + ".txt", 'w', encoding='utf-8') as g:
                    g.write(response_body)
                return 0

            # No change, return 1.
            return 1

    # new cache entirely
    with open('./' + url + ".txt", 'w+', encoding='utf-8') as f:
        f.write(response_body)
        return 2

def make_gui(script):
    root = Tk()
    frame = ttk.Frame(root, padding=20)
    frame.grid()

    ttk.Label(frame, text="Web-Test").grid(column=1, row=0)

    ttk.Label(frame, text="Enter your URL here:  ").grid(column=0, row=2)
    box = ttk.Entry(frame)
    box.grid(column=1, row=2)


    submit_stat = ttk.Button(root, text="Check the status of webpage", command=lambda: check_status(box.get())).grid(column=1, row =2)
    submit_changed = ttk.Button(root, text="See if the website has changed from cache", command=lambda: main(box.get(), script)).grid(column=1, row =2)


    root.mainloop()

def clean_html(dat, script):
    # Should delete any CSRF tokens of this format
    soup = BeautifulSoup(dat, features="html.parser")
    token = soup.find('input', {'name': 'csrfToken'})
    if token is not None:
        token.decompose()
    token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if token is not None:
        token.decompose()

    if not script:
        token = soup.find_all('script')
        if token is not None:
            for tag in token:
                tag.decompose()
    return soup



# collects arguments
parser = argparse.ArgumentParser(description='Check to see if a website has changed from last check', prog="Website Checker")

parser.add_argument("-gui", action='store_true', help="Make a gui")
parser.add_argument('-u', type=str, help="url of site")
parser.add_argument('-s', action='store_true', help="Do you want the status of the page only")
parser.add_argument('-S', action='store_true', help="If you want to include <script> tags in your comparisons. Default filters them." )

args = parser.parse_args()


if args.gui:
    make_gui(args.S)
elif args.s:
    check_status(args.u)
else:
    main(args.u, args.S)
