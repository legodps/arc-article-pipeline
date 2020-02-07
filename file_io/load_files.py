import json
import os
import yaml


def load_config(config_path):
    """ Imports a yaml configuration file and all of its properties

        Args:
            config_path (str): the path to a config file

        Returns:
            dict: a set of properties to use
    """
    with open(config_path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config


def process_article_line(article_line):
    """ Takes in a JSON formatted line from an article JSONL file and extracts the article of text

        Args:
            article_line (str): a line from a JSONL file that contains the correct formatting

        Returns:
            str: the extracted article put together
    """
    article_object = json.loads(article_line)
    article_text = ''
    for paragraph in article_object['paragraphs']:
        for text_piece in paragraph['para_body']:
            article_text += text_piece['text']
    return {'title': article_object['title'].lower(), 'text': article_text}


def process_article(filepath):
    """ Opens a JSONL file and returns all articles from it

        Args:
            filepath (str): the path to the file

        Returns:
            list: all articles in the file
    """
    articles = []
    # appends the JSONL extension if it does not exist in the path to the file
    filename = filepath if '.jsonl' in filepath else f'{filepath}.jsonl'
    with open(filename) as article_file:
        article_line = article_file.readline()
        while article_line:
            articles.append(process_article_line(article_line))
            article_line = article_file.readline()
    return articles


def read_jsonl_articles(filepath):
    """ Opens the file(s) at a given filepath, extracts the articles, and returns them

        Args:
            filepath (str): a path to a given file or directory containing JSONL files

        Returns:
            list: all articles at the filepath
    """
    all_articles = []
    try:
        # try to open filepath as a singular file
        all_articles = process_article(filepath)
    except (IsADirectoryError, FileNotFoundError):
        # if it errors, try to open it as a directory containing JSONL files
        for filename in os.listdir(filepath):
            if '.jsonl' in filename:
                all_articles += process_article(f'{filepath}/{filename}')

    return all_articles


def retrieve_questions(filepath):
    """

    """
    with open(filepath) as question_file:
        question_sets = json.load(question_file)

    parsed_questions = {}
    for question_set in question_sets:
        question_set_index = question_set['globalID']
        parsed_questions[question_set_index] = []
        question_id = 0
        for question_key in question_set['questions']['nonDiagramQuestions'].keys():
            digested_question = {
                'id': question_id,
                'question': {
                    'stem':
                        question_set['questions']['nonDiagramQuestions'][question_key]['beingAsked'][
                            'processedText'],
                    'choices': []
                },
                'answerKey':
                    question_set['questions']['nonDiagramQuestions'][question_key]['correctAnswer'][
                        'processedText']
            }
            for answer_key in question_set['questions']['nonDiagramQuestions'][question_key]['answerChoices'].keys():
                digested_question['question']['choices'].append({
                    "text": question_set['questions']['nonDiagramQuestions'][question_key]
                                        ['answerChoices'][answer_key]['processedText'],
                    'label': answer_key
                })
            parsed_questions[question_set_index].append(digested_question)
            question_id += 1

    return parsed_questions


def read_json_questions(filepath):
    """

    """
    all_questions = []
    try:
        all_questions = retrieve_questions(filepath)
    except (IsADirectoryError, FileNotFoundError):
        for filename in os.listdir(filepath):
            if '.json' in filename:
                all_questions += retrieve_questions(f'{filepath}/{filename}')

    return all_questions
