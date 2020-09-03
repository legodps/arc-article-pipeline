import re
from arc_benchmark.file_utils import read_jsonl_articles, load_tqa_articles
from arc_benchmark.constants import ELASTICSEARCH_DOC, ELASTICSEARCH_ID, ELASTICSEARCH_INDEX, ELASTICSEARCH_OP_TYPE, \
    ELASTICSEARCH_SOURCE, ELASTICSEARCH_TYPE, FILE, ID, INDEX, MAPPING, QUESTION_DIRECTORY, TEXT, TITLE


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
            config (dict): config file specified properties to use in running the benchmark
    """
    es.indices.create(index=index_name, ignore=400, body=config[MAPPING])


def make_documents(index_name, article, config):
    """ Yields a series of json objects to be used as documents for inserting into Elasticsearch
    
        Args:
            index_name (str): the name of the index to insert into the instance of Elasticsearch
            article (list): a list of sentences from an article
            config (dict): config file specified properties to use in running the benchmark
        
        Returns:
            generator: a iterable group of Elasticsearch compatible documents
    """
    doc_id = 0
    for line in article:
        doc = {
            ELASTICSEARCH_INDEX: index_name,
            ELASTICSEARCH_TYPE: ELASTICSEARCH_DOC,
            ELASTICSEARCH_OP_TYPE: INDEX,
            ELASTICSEARCH_ID: doc_id,
            ELASTICSEARCH_SOURCE: {TEXT: line.strip()}
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
            dict: a dict of files associated with their indices, used later in calculating results
    """
    question_set_indices = {}
    index_file = {}
    for article in articles:
        line_array = re.split('[.?!]', article[TEXT])
        index_name = clean_article_name(article[TITLE])
        if not es.indices.exists(index=index_name):
            create_elasticsearch_index(index_name, es, config)
            make_documents(index_name, line_array, config)
            bulk(es, make_documents(index_name, line_array, config))
        index_file[index_name] = article[FILE]
        if article[ID] in question_set_indices:
            question_set_indices[article[ID]].append(index_name)
        else:
            question_set_indices[article[ID]] = [index_name]
    return question_set_indices, index_file


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
    #for article in articles:
        #print(article['title'])
        #if article['title'] in ['rerank2_bert-darwin\'s theory of evolution', 'uvabottomup2-darwin\'s theory of evolution', 'dangnt-nlp-darwin\'s theory of evolution']:
        #    print(article['title'])
        #    print(article['text'])
        #    print('\n')
    return store_articles(articles, es, bulk, config)


def combine_indices(new_question_set_indices, question_set_indices):
    """ Combines the two sets of question set indices to get a master list

        Args:
            new_question_set_indices (dict): a set of indices and questions to be combined with the existing master list
            question_set_indices (dict): a set of existing indices and questions to be added to

        Returns:
            dict: the combined list of questions and indices
    """
    for question_set_key in new_question_set_indices:
        question_set_indices[question_set_key].append(new_question_set_indices[question_set_key][0])
    return question_set_indices


def load_and_store_tqa_articles(question_set_indices, es, bulk, config):
    """ Loads articles from the TQA dataset and stores them in the Elasticsearch Database

        Args:
            question_set_indices (dict): a list of indices by the questions set they are slated to answer
            es (object): the Elasticsearch Object used to insert into the database
            bulk (function): the Elasticsearch function to rapidly insert a large chunk of indices
            config (dict): config file specified properties to use in running the benchmark

        Returns:
            dict: the master list of normal article indices and tqa article indices by the question set they will
                answer
            dict: a dict of files associated with their indices, used later in calculating results
    """
    articles = load_tqa_articles(question_set_indices, config)
    #for article in articles:
        # print(article['title'])
    #    if article['title'] in ['tqa-darwins theory of evolution']:
     #       print(article['title'])
      #      print(article['text'])
       #     print('\n')
    tqa_question_set_indices, index_files = store_articles(articles, es, bulk, config)
    return combine_indices(tqa_question_set_indices, question_set_indices), index_files
