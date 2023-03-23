#!/usr/bin/env python

import requests
import traceback
import sys
from datetime import datetime
import asyncio
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import apis as apis
import elasticindex as elasticindex

USERAGENT = "python-hn-client"
HEADERS = {'User-agent': USERAGENT}


def getItemData(itemId, count, itemType, session):

    try:
        with session.get(apis.STORY_INFO.format(itemId)) as response:
            if (response.status_code == 200):

                story_data = {}

                if (response.json() is not None):
                    if ('url' in response.json().keys()):
                        parsed_uri = urlparse(response.json()['url'])
                        result = None
                        result = '{uri.scheme}://{uri.netloc}'.format(
                            uri=parsed_uri)

                        print("[{}]. {} - {} - {}".format(
                            count,
                            response.json()['title'],
                            datetime.utcfromtimestamp(
                                response.json()['time']).strftime(
                                    '%Y-%m-%d %H:%M:%S'), result))

                        story_data = {
                            "title":
                            response.json()['title'],
                            "url":
                            response.json()['url'],
                            "score":
                            response.json()['score'],
                            "id":
                            response.json()['id'],
                            "added":
                            datetime.utcfromtimestamp(
                                response.json()['time']).strftime(
                                    '%Y-%m-%d %H:%M:%S')
                        }
                        #yyy-MM-dd'T'HH:mm:ss

                    else:
                        print("[{}]. {} - {}".format(
                            count,
                            response.json()['title'],
                            datetime.utcfromtimestamp(
                                response.json()['time']).strftime(
                                    '%Y-%m-%d %H:%M:%S'),
                            response.json()['score']))

                        story_data = {
                            "title":
                            response.json()['title'],
                            "url":
                            "",
                            "score":
                            response.json()['score'],
                            "id":
                            response.json()['id'],
                            "added":
                            datetime.utcfromtimestamp(
                                response.json()['time']).strftime(
                                    '%Y-%m-%d %H:%M:%S')
                        }
                        return story_data

                    return story_data
                else:
                    return 'error'
            else:
                print("ERROR: {}".format(response.text))
    except Exception as e:
        print(traceback.format_exc())


async def getStories(item,limit,session,indexing):
    try:

        url = apis.TOP_STORIES
        if (item == "new"):
            url = apis.NEW_STORIES

        stories = []
        with ThreadPoolExecutor(max_workers=10) as executor:

            response = session.get(url, headers=HEADERS)
            count = 0

            if (response.status_code == 200 and len(response.json()) > 0):
                print("===> {} stories found = {}, limit = {}".format(
                    item.upper(), len(response.json()), limit))

                for item_id in response.json():

                    count += 1
                    # Set any session parameters here before calling `getStoryData`
                    loop = asyncio.get_event_loop()
                    tasks_1 = [
                        loop.run_in_executor(
                            executor,
                            getItemData,
                            *(
                                item_id, count, item, session
                            )  # Allows us to pass in multiple arguments to `getStoryData`
                        )
                    ]

                    for response in await asyncio.gather(*tasks_1):
                        if (response == 'error'):
                            if (count >= 1):
                                count -= 1
                            else:
                                count = 0

                        if (type(response) == dict):
                            stories.append(response)

                        pass

                    #   time.sleep(2)
                    if (count == limit):
                        break

                if (indexing):
                    print('===> Adding Elasticsearch index.')
                    loop2 = asyncio.get_event_loop()
                    tasks_2 = [
                        loop2.run_in_executor(executor, addIndex, (stories))
                    ]

                    for response in await asyncio.gather(*tasks_2):
                        pass

            else:
                print("Failed to make request.")
                print(response.text)

    except Exception as e:
        print(traceback.format_exc())


def addIndex(stories):
    count = 0
    total = len(stories)
    for x in stories:
        count += 1

        response_code = elasticindex.addElasticIndex(x, x['id'], SESSION, ITEM)
        if (response_code == 201):

            print("===> Adding index [{}/{}]\r".format(count, total),
                  end="",
                  flush=False)
        else:
            print("===> {}/{} Failed to add index.".format(count, total),
                  end="",
                  flush=False)

    if (count == total):
        print("=====> Indexes added [{}].".format(count))


def getUserProfile(uid):
    try:
        response = SESSION.get(apis.USER_PROFILE.format(uid),
                               headers={
                                   "Content-Type": "application/json",
                                   "User-agent": USERAGENT
                               })

        print("++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("UserId = " + response.json()['id'])
        print("Karma = " + str(response.json()['karma']))
        print("++++++++++++++++++++++++++++++++++++++++++++++++++")

    except Exception as e:
        print(traceback.format_exc())


def main():

    parser = argparse.ArgumentParser(
        description='Gets list of top/new stories on HN.')

    parser.add_argument("--item",
                        help="Input 'new' / 'top' to get items.",
                        type=str,
                        required=True)
    parser.add_argument("--limit",
                        help="Limit the number of items to show - max = 500.",
                        type=int,
                        required=True)
    parser.add_argument("--index",
                        help="Turn on Elasticsearch indexing - yes/no",
                        type=str,
                        required=False)

    parser.add_argument("--userid",
                        help="Your HN User Id",
                        type=str,
                        required=False)

    args = parser.parse_args()


    item = None
    limit = 100
    indexing = False
    userid = None

    session = requests.Session()

    if (args.item and type(args.limit) is int and args.limit > 0 and args.item == "top" or args.item == "new"):
        item = args.item
        limit = int(args.limit)
        userid = args.userid

        if (args.index == 'yes'):
            indexing = True

    else:
        parser.print_help()
        sys.exit(1)

    if (indexing):
        elasticindex.deleteElasticIndex(item, session)

    if (userid is not None):
        getUserProfile(userid)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        future = asyncio.ensure_future(getStories(item,limit,session,indexing))
        loop.run_until_complete(future)
    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":

    main()
