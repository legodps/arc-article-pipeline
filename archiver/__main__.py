import argparse
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from file_io.load_files import load_config, read_jsonl_articles
from archiver import article_archiver

parser = argparse.ArgumentParser(description='Store articles into indices to mirror ARC-Solver setup')
parser.add_argument(
    '-f',
    '--filepath',
    default=None,
    help='a filepath to a singular article file or a directory of files'
)
parser.add_argument(
    '-c',
    '--config_file',
    default='archiverConfig.yaml',
    help='A yaml config file to import settings from, defaults to archiverConfig.yaml'
)


def process_articles(filepath, config_file):
    """ This orchestrates the processing of articles, and then the insertion of the sentences into elasticsearch

        Args:
            filepath (various): the command line argument of the filepath to load articles from
            config_file (str): the command line argument of the config file to use
    """
    properties = load_config(config_file)
    directory = filepath

    # default to use the command line argument if not specified use the config file if present
    if not directory and 'data_directory' in properties.keys():
        directory = properties['data_directory']

    if directory:
        articles = read_jsonl_articles(directory)
        print(len(articles))
        try:
            es = Elasticsearch(hosts=[{'host': properties['host'], 'port': properties['port']}], retries=3, timeout=60)
            article_archiver.store_articles(articles, properties, es, bulk)
        except:
            print('an elasticsearch error has occurred')
    else:
        print('no data directory given please specify one with \'-f\' via the commandline or the config file')


args = parser.parse_args()

process_articles(args.filepath, args.config_file)
