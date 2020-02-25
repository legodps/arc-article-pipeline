# Contains strings used repeatedly, storing in this file for consistency
ANSWER_CHOICES = 'answerChoices'
ANSWER_KEY = 'answerKey'
ARC_DATA_SUBDIRECTORY = 'arc_data_subdirectory'
ARC_MODEL_SUBDIRECTORY = 'arc_model_subdirectory'
ARC_SOLVER_DIRECTORY = 'arc_solver_directory'
ARTICLE_DIRECTORY = 'article_directory'
BEING_ASKED = 'beingAsked'
BENCHMARK_SET_DIRECTORY = 'benchmark_set_directory'
CHOICES = 'choices'
CONDA_ENVIRONMENT_NAME = 'conda_environment_name'
CONFIG_FILE = 'config_file'
CORRECT_ANSWER = 'correctAnswer'
GLOBAL_ID = 'globalID'
HOST = 'host'
ID = 'id'
INDEX = 'index'
LABEL = 'label'
MAPPING = 'mapping'
METRICS = 'Metrics'
NON_DIAGRAM_QUESTIONS = 'nonDiagramQuestions'
PARA_BODY = 'para_body'
PARAGRAPHS = 'paragraphs'
PORT = 'port'
PROCESSED_TEXT = 'processedText'
QUESTION = 'question'
QUESTION_DIRECTORY = 'question_directory'
QUESTIONS = 'questions'
SENTENCE = 'sentence'
SQUID = 'squid'
STEM = 'stem'
TEXT = 'text'
TITLE = 'title'

# Elasticsearch mapping values
ELASTICSEARCH_ID = '_id'
ELASTICSEARCH_INDEX = '_index'
ELASTICSEARCH_TYPE = '_type'
ELASTICSEARCH_OP_TYPE = '_op_type'
ELASTICSEARCH_SOURCE = '_source'

# Files and Directories
ARC_DATA_FULL_WIPE_KEEP_FILES = [
    'ARC-Challenge-Dev.jsonl',
    'ARC-Challenge-Dev.csv',
    'ARC-Challenge-Train.jsonl',
    'ARC-Challenge-Train.csv',
    'ARC-Challenge-Test.csv'
]
ARC_DATA_SMALL_WIPE_KEEP_FILES = [
    'ARC-Challenge-Dev.jsonl',
    'ARC-Challenge-Dev.csv',
    'ARC-Challenge-Train.jsonl',
    'ARC-Challenge-Train.csv',
    'ARC-Challenge-Test.jsonl'
    'ARC-Challenge-Test.csv'
]
ARC_BENCHMARK_DIRECTORY = '/arc-benchmark'
ARC_CHALLENGE_TEST = 'ARC-Challenge-Test.jsonl'
BENCHMARK_CONFIG_YAML = 'benchmarkConfig.yaml'
ENV_DIRECTORY = '/env'
EVALUATE_SOLVER_FILEPATH = 'scripts/evaluate_solver.sh'
HTMLCOV_DIRECTORY = '/htmlcov'
JSON_EXTENSION = '.json'
JSONL_EXTENSION = '.jsonl'
TESTS_DIRECTORY = '/tests'
