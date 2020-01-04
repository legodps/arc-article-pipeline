import elasticsearch
import re
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

TYPE = 'sentence'
MAPPING = '''
    {
      "mappings": {
        "sentence": {
          "dynamic": "false",
          "properties": {
            "docId": {
              "type": "keyword"
            },
            "text": {
              "analyzer": "standard",
              "type": "text",
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              }
            },
            "tags": {
              "type": "keyword"
            }
          }
        }
      }
    }'''

def clean_article_name(article_name)
    '''
    
    '''
    return re.sub('[\/*?",<>|]', '', article_name.strip().replace(' ','-').replace('_','-'))


def create_elasticserach_index(index_name,  es, config):
    '''
    
    '''
    response = es.indices.create(index=index_name, ignore=400, body=MAPPING)


def make_documents(article):
    """
    
    """
    doc_id = 0
    for line in article
        doc = {
            '_op_type': 'create',
            '_index': index_name,
            '_type': TYPE,
            '_id': doc_id,
            '_source': {'text': line.strip()}
        }
        doc_id += 1
        yield (doc)

def store_articles(articles, config):
     """
        
    """
    es = Elasticsearch(hosts=[{"host": args.host, "port": args.port}], retries=3, timeout=60)
    indices = []
    for article in articles:
        line_array = re.split('[.?!]', article.text)
        index_name = clean_article_name(article.name)
        indices.append(index_name)
        try:
            create_elasticsearch_index(index_name, es, config)
        response = bulk(es, make_documents(f))
    print('Articles have been inserted into the database')


