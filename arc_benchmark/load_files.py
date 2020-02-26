import json
import os
from arc_benchmark.constants import ANSWER_CHOICES, ANSWER_KEY, BEING_ASKED, CHOICES, CORRECT_ANSWER, FILE, GLOBAL_ID, \
    ID, JSONL_EXTENSION, JSON_EXTENSION, LABEL, NON_DIAGRAM_QUESTIONS, PARA_BODY, PARAGRAPHS, PROCESSED_TEXT, \
    QUESTION, QUESTIONS, SQUID, STEM, TEXT, TITLE


def process_article_line(article_line, filename):
    """ Takes in a JSON formatted line from a JSONL article file and extracts salient article information like
        the text, title, and corresponding question set ID

        Args:
            article_line (str): a line from a JSONL file that contains the correct formatting
            filename (str): the file the article line came from, added to the title for clarity of Elasticsearch index
                during article index creation and storage

        Returns:
            dict: the title, text, and question set id of an article from the JSONL article file
    """
    article_object = json.loads(article_line)
    article_text = ''
    for paragraph in article_object[PARAGRAPHS]:
        for text_piece in paragraph[PARA_BODY]:
            article_text += text_piece[TEXT]
    return {
        TITLE: f'{filename}-{article_object[TITLE].lower()}',
        TEXT: article_text,
        ID: article_object[SQUID].split(':')[1],
        FILE: filename
    }


def process_article(filepath):
    """ Opens a JSONL article file and returns all articles from it

        Args:
            filepath (str): the path to the file

        Returns:
            list: a list of formattted article dicts gotten from the JSONL article file
    """
    articles = []
    # appends the JSONL extension if it does not exist in the path to the file
    filename = filepath if JSONL_EXTENSION in filepath else f'{filepath}{JSONL_EXTENSION}'
    with open(filename) as article_file:
        article_line = article_file.readline()
        while article_line:
            articles.append(
                process_article_line(article_line, filename.split(JSONL_EXTENSION)[0].split('/')[-1].lower())
            )
            article_line = article_file.readline()
    return articles


def read_jsonl_articles(filepath):
    """ Opens the file(s) at a given filepath, extracts the articles, and returns them

        Args:
            filepath (str): a path to a singular file, or directory of, JSONL article files

        Returns:
            list: all articles at the filepath
    """
    all_articles = []
    try:
        # try to open filepath as a singular file
        all_articles = process_article(filepath)
    except (IsADirectoryError, FileNotFoundError):
        # if it errors, try to open it as a directory containing JSONL files
        for filename in sorted(os.listdir(filepath)):
            if JSONL_EXTENSION in filename:
                all_articles += process_article(f'{filepath}/{filename}')

    return all_articles


def retrieve_questions(filepath):
    """ Retrieves questions grouped by an ID to be used in benchmarking sets of articles. This extraction was designed
        for questions from the TQA dataset.

        Args:
            filepath (str): the path to the question file

        Returns:
            dict: groups of questions to be stored for later benchmarking
    """
    filename = filepath if JSON_EXTENSION in filepath else f'{filepath}{JSON_EXTENSION}'
    with open(filename) as question_file:
        question_sets = json.load(question_file)

    parsed_questions = {}
    for question_set in question_sets:
        question_set_index = question_set[GLOBAL_ID]
        parsed_questions[question_set_index] = []
        question_id = 0
        for question_key in question_set[QUESTIONS][NON_DIAGRAM_QUESTIONS].keys():
            digested_question = {
                ID: str(question_id),
                QUESTION: {
                    STEM:
                        question_set[QUESTIONS][NON_DIAGRAM_QUESTIONS][question_key][BEING_ASKED][PROCESSED_TEXT],
                    CHOICES: []
                },
                ANSWER_KEY:
                    question_set[QUESTIONS][NON_DIAGRAM_QUESTIONS][question_key][CORRECT_ANSWER][PROCESSED_TEXT]
            }
            for answer_key in question_set[QUESTIONS][NON_DIAGRAM_QUESTIONS][question_key][ANSWER_CHOICES].keys():
                digested_question[QUESTION][CHOICES].append({
                    TEXT: question_set[QUESTIONS][NON_DIAGRAM_QUESTIONS][question_key]
                                      [ANSWER_CHOICES][answer_key][PROCESSED_TEXT],
                    LABEL: answer_key
                })
            parsed_questions[question_set_index].append(digested_question)
            question_id += 1

    return parsed_questions


def read_json_questions(filepath):
    """ Opens the file(s) at a given filepath, extracts the questions, and returns them

        Args:
            filepath (str): a path to a singular, or directory of, JSON question files

        Returns:
            dict: all sets of grouped questions

    """
    all_questions = {}
    try:
        all_questions = retrieve_questions(filepath)
    except (IsADirectoryError, FileNotFoundError):
        for filename in sorted(os.listdir(filepath)):
            if JSON_EXTENSION in filename:
                all_questions = {
                    **all_questions,
                    **retrieve_questions(f'{filepath}/{filename}')
                }

    return all_questions
