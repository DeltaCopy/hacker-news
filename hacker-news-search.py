#!/usr/bin/env python

import requests
import traceback
import sys
from datetime import datetime
import argparse
import json
import apis as apis
import re

USERAGENT = "python-hn-client"
HEADERS = {'User-agent': USERAGENT}
# search term = none default
SEARCH_TERM = None


def searchHN(session, url,term):
    if(url is not None):
        response = session.get(apis.SEARCH_URL.format(url))
    if(term is not None):
        response = session.get(apis.SEARCH_STORY.format(term))

    if(response.status_code == 200 and len(response.json()) > 0):
        index = 0
        results = response.json()['hits']
        hits_count = response.json()['nbHits']
        hits_page = response.json()['hitsPerPage']
            
        print("===> Search url: {}, hits: {}, hits/page: {}".format(term,hits_count,hits_page))


        if(len(results) == hits_count):
            for i in range(index,hits_count):

                #print(re.findall(term,results[i]['title']))


                #if (term.lower() in results[i]['title'].lower()):
                print("[{}] {} [{}] - {}".format(results[i]['points'],results[i]['title'],results[i]['created_at'],results[i]['url']))
        else:
            for i in range(index,hits_page):

                #if(term.lower() in results[i]['title'].lower()):
                print("[{}] {} [{}] - {}".format(results[i]['points'],results[i]['title'],results[i]['created_at'],results[i]['url']))

def main():

    parser = argparse.ArgumentParser(
        description='Search top/new stories on HN.')

    parser.add_argument("--url", help="Search url", type=str, required=False)
    parser.add_argument("--term", help="Search url", type=str, required=False)


    args = parser.parse_args()

    if (args.url is not None or args.term is not None):
        with requests.Session() as session:

            searchHN(session, args.url, args.term)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":

    main()
