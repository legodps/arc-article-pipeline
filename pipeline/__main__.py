import argparse
from pipeline import article_archiver, load_files

parser = argparse.ArgumentParser(description='Store articles into indices to mirror ARC-Solver setup')
parser.add_argument('-c','--config_file', default='pipelineConfig.yaml', help='A yaml config file to import settings from, defaults to pipelineConfig.yaml')


def process_articles(config_file):
    properties = load_files.load_config(config_file)
    print(properties)


args = parser.parse_args()

process_articles(args.config_file)