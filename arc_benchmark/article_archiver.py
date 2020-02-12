import re
from arc_benchmark.load_files import read_jsonl_articles


def clean_article_name(article_name):
    """ Strips an article name of illegal characters and replaces typical spacing characters with valid ones
    
        Args:
            article_name (str): the name of the article to be cleaned
        
        Returns:
            str: the cleaned article name
    """
    return re.sub('[\\\\/*?",<>|.\']', '', article_name.strip().replace(' ', '-').replace('_', '-'))


def create_elasticsearch_index(index_name,  es, config):
    """ Creates the Elasticsearch index for a given article

        Args:
            index_name (str): the name of the index to be created
            es (object): an Elasticsearch instance to use for creating indices
            config (dict): an object containing configurations
    """
    es.indices.create(index=index_name, ignore=400, body=config['mapping'])


def make_documents(index_name, article, config):
    """ Yields a series of json objects to be used as documents for inserting into Elasticsearch
    
        Args:
            index_name (str): the name of the index to insert into the instance of Elasticsearch
            article (list): a list of sentences from an article
            config (dict): an object containing configurations
        
        Returns:
            generator: a iterable group of Elasticsearch compatible documents
    """
    doc_id = 0
    for line in article:
        doc = {
            '_index': index_name,
            '_id': doc_id,
            '_source': {'text': line.strip()}
        }
        doc_id += 1
        yield doc


def store_articles(articles, es, bulk, config):
    """ Takes in a series of articles and inserts them into Elasticsearch
        
        Args:
            articles (list of dicts): a list of articles to insert into Elasticsearch
            es (object): an Elasticsearch client object to store articles with
            bulk (function): a function for the Elasticsearch library, passed in for ease of unit testing
            config (dict): config file specified properties to use in running the benchmark

        Returns:
            dict: a list of Elasticsearch indices by the set of questions they are associated with
    """
    question_set_indices = {}
    for article in articles:
        line_array = re.split('[.?!]', article['text'])
        index_name = clean_article_name(article['title'])
        create_elasticsearch_index(index_name, es, config)
        bulk(es, make_documents(index_name, line_array, config))
        if article['id'] in question_set_indices:
            question_set_indices[article['id']].append(index_name)
        else:
            question_set_indices[article['id']] = [index_name]
    print('Articles have been inserted into the database')
    return question_set_indices


def load_and_store_articles(article_directory, es, bulk, config):
    """ Orchestrates the loading of JSONL article files and the storage of the articles into Elasticsearch

        Args:
            article_directory (str): the filepath to a singular, or directory of, JSONL article files
            es (object): the instantiated Elasticsearch connection
            bulk (function): the bulk operation function used to perform Elasticsearch operations en masse
            config (dict): config file specified properties to use in running the benchmark

        Returns:
            dict: a list of Elasticsearch indices by the set of questions they are associated with
    """
    articles = read_jsonl_articles(article_directory)
    try:
        return store_articles(articles, es, bulk, config)
    except:
        print('an elasticsearch error has occurred')
