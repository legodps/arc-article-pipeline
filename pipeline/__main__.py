import argparse
from pipeline import article_archiver, load_files

parser = argparse.ArgumentParser(description='Store articles into indices to mirror ARC-Solver setup')
parser.add_argument('filepath', help='a filepath to a singular article file or a directory of files')
parser.add_argument(
    '-c',
    '--config_file',
    default='pipelineConfig.yaml',
    help='A yaml config file to import settings from, defaults to pipelineConfig.yaml'
)


def process_articles(filepath, config_file):
    """

    """
    properties = load_files.load_config(config_file)
    articles = load_files.read_jsonl_articles(filepath)
    print(len(articles))
    article_archiver.store_articles(articles, properties)


args = parser.parse_args()

process_articles(args.filepath, args.config_file)
