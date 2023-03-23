# HN

TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
NEW_STORIES = "https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty"
STORY_INFO = "https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty"
USER_PROFILE = "https://hacker-news.firebaseio.com/v0/user/{}.json?print=pretty"
SEARCH_STORY = "https://hn.algolia.com/api/v1/search_by_date?query={}&tags=story"
SEARCH_URL = "http://hn.algolia.com/api/v1/search?query={}&restrictSearchableAttributes=url"
# Elastic search index

ELASTIC_INDEX_NEW = "http://diskstation:9200/hn-new/"
ELASTIC_INDEX_TOP = "http://diskstation:9200/hn-top/"