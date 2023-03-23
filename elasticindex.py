import requests
import traceback
import apis
import json
import sys
# deletes entire index

def deleteElasticIndex(item,session):
    try:
        
        data = '{"query" : { "match_all": {} }}'
       
        if (item == "new"):
            response = session.post(
                apis.ELASTIC_INDEX_NEW + "_delete_by_query?conflicts=proceed",
                headers={"Content-Type": "application/json"},
                data=data)
        elif (item == "top"):
            response = session.post(
                apis.ELASTIC_INDEX_TOP + "_delete_by_query?conflicts=proceed",
                headers={"Content-Type": "application/json"},
                data=data)

        

    except Exception as e:
        print(traceback.format_exc())

# adds a JSON document to specified index

def addElasticIndex(data, id, session, story_type):
    try:
        if (story_type == "new"):
            response = session.put(
                apis.ELASTIC_INDEX_NEW + "_doc/{}".format(id),
                headers={"Content-Type": "application/json"},
                data=json.dumps(data))

            return response.status_code
        elif (story_type == "top"):

            response = session.put(
                apis.ELASTIC_INDEX_TOP + "_doc/{}".format(id),
                headers={"Content-Type": "application/json"},
                data=json.dumps(data))

            return response.status_code

    except Exception as e:
        print(traceback.format_exc())
