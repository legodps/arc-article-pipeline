import json
import os
from arc_benchmark.constants import ADJUNCT_TOPICS, ANSWER_CHOICES, ANSWER_KEY, ARC_CHECKPOINT_FILE, BEING_ASKED, \
    CHECKPOINT_DIRECTORY, CHOICES, CONTENT, CORRECT_ANSWER, DIAGRAM_ANNOTATIONS, FILE, GLOBAL_ID, ID, INDEX, \
    INSTRUCTIONAL_DIAGRAMS, JSONL_EXTENSION, JSON_EXTENSION, LABEL, LESSON_NAME, NON_DIAGRAM_QUESTIONS, PARA_BODY, \
    PARAGRAPHS, PROCESSED_TEXT, QUESTION, QUESTION_DIRECTORY, QUESTION_SET, QUESTIONS, SQUID, STEM, TEXT, TITLE, \
    TOPICS, TQA


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


def retrieve_questions(filepath, question_set_ids):
    """ Retrieves questions grouped by an ID to be used in benchmarking sets of articles. This extraction was designed
        for questions from the TQA dataset.

        Args:
            filepath (str): the path to the question file

        Returns:
            dict: groups of questions to be stored for later benchmarking
            dict: the count of questions by the number of possible answers
    """
    question_answer_count = {}
    question_count = 0
    filename = filepath if JSON_EXTENSION in filepath else f'{filepath}{JSON_EXTENSION}'
    with open(filename) as question_file:
        question_sets = json.load(question_file)

    parsed_questions = {}
    for question_set in question_sets:
        temp_question_count = 0
        question_set_index = question_set[GLOBAL_ID]
        question_id = 0
        for question_key in question_set[QUESTIONS][NON_DIAGRAM_QUESTIONS].keys():
            answer_count = 0
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
                answer_count += 1
                digested_question[QUESTION][CHOICES].append({
                    TEXT: question_set[QUESTIONS][NON_DIAGRAM_QUESTIONS][question_key]
                                      [ANSWER_CHOICES][answer_key][PROCESSED_TEXT],
                    LABEL: answer_key
                })
            if question_set_index in question_set_ids:
                question_count += 1
                temp_question_count += 1
                if question_set_index in parsed_questions:
                    parsed_questions[question_set_index].append(digested_question)
                else:
                    parsed_questions[question_set_index] = [digested_question]
                question_id += 1
                if str(answer_count) not in question_answer_count:
                    question_answer_count[str(answer_count)] = 1
                else:
                    question_answer_count[str(answer_count)] += 1
    return parsed_questions, question_answer_count


def add_question_counts(total_counts, new_counts):
    """ Combines two python dicts of counts, summing over existing keys

        Args:
            total_counts (dict): the previous total
            new_counts (dict): the new counts retrieved from a question file

        Returns:
            dict: the combined totals from total_counts being summed with new_counts
    """
    if len(total_counts.keys()) == 0:
        return new_counts

    for answer_count in new_counts.keys():
        if answer_count not in total_counts:
            total_counts[answer_count] = new_counts[answer_count]
        else:
            total_counts[answer_count] += new_counts[answer_count]

    return total_counts


def read_json_questions(filepath, question_set_ids):
    """ Opens the file(s) at a given filepath, extracts the questions, and returns them

        Args:
            filepath (str): a path to a singular, or directory of, JSON question files
            question_set_ids (list): a list of all the questions that should be loaded in

        Returns:
            dict: all sets of grouped questions
            dict: the total number of questions by the number of possible answers
    """
    all_questions = {}
    try:
        all_questions, total_question_answer_counts = retrieve_questions(filepath, question_set_ids)
    except (IsADirectoryError, FileNotFoundError):
        total_question_answer_counts = {}
        for filename in sorted(os.listdir(filepath)):
            if JSON_EXTENSION in filename:
                new_questions, new_question_answer_counts = retrieve_questions(
                    f'{filepath}/{filename}',
                    question_set_ids
                )
                all_questions = {
                    **all_questions,
                    **new_questions
                }
                total_question_answer_counts = add_question_counts(
                    total_question_answer_counts,
                    new_question_answer_counts
                )

    return all_questions, total_question_answer_counts


def create_or_load_arc_checkpoint(config):
    """ Loads in the JSONL checkpoint file if it exists or creates it if it doesn't

        Args:
            config (dict): config file specified properties to use in running the benchmark

        Returns:
            file: a file to write to during the ARC_Solver runs to keep checkpoints
            object: an object containing any entries loaded from a checkpoint file
    """
    if not os.path.isdir(config[CHECKPOINT_DIRECTORY]):
        os.mkdir(config[CHECKPOINT_DIRECTORY])

    if not os.path.isfile(f'{config[CHECKPOINT_DIRECTORY]}/{config[ARC_CHECKPOINT_FILE]}'):
        checkpoint_file = open(f'{config[CHECKPOINT_DIRECTORY]}/{config[ARC_CHECKPOINT_FILE]}', 'w+')
        completed_entries = {}
    else:
        checkpoint_read = open(f'{config[CHECKPOINT_DIRECTORY]}/{config[ARC_CHECKPOINT_FILE]}', 'r')
        completed_entries = {}
        for line in checkpoint_read.readlines():
            json_line = json.loads(line)
            completed_entries[(json_line[INDEX], json_line[QUESTION_SET])] = json_line
        checkpoint_read.close()
        checkpoint_file = open(f'{config[CHECKPOINT_DIRECTORY]}/{config[ARC_CHECKPOINT_FILE]}', 'a+')

    return checkpoint_file, completed_entries


def load_json(filename, config):
    """ Imports a json formatted file, it will return None if the file does not exist

        Args:
            filename (str): the name of the file that would be stored in the checkpoints directory
            config (dict): config file specified properties to use in running the benchmark

        Returns:
            various: Either None if the file does not exist or the python object equivalent of the json in the file
    """
    if not os.path.isdir(config[CHECKPOINT_DIRECTORY]) \
            or not os.path.isfile(f'{config[CHECKPOINT_DIRECTORY]}/{filename}'):
        return None

    json_file = open(f'{config[CHECKPOINT_DIRECTORY]}/{filename}', 'r')
    parsed_file = json.load(json_file)
    json_file.close()
    return parsed_file


def store_json(results, filename, config):
    """ Writes results from a python object to a JSON file

        Args:
            results (object): a python object containing the results from running ARC Solver
            filename (str): the name of the json file to write to
            config (dict): config file specified properties to use in running the benchmark
    """
    json_file = open(f'{config[CHECKPOINT_DIRECTORY]}/{filename}', 'w')
    json.dump(results, json_file)
    json_file.close()


def load_tqa_articles(question_set_indices, config):
    """

    """
    articles = []
    tqa_file = open(config[QUESTION_DIRECTORY], 'r')
    tqa_dataset = json.load(tqa_file)
    tqa_file.close()

    for question_set in tqa_dataset:
        if question_set[GLOBAL_ID] in question_set_indices:
            tqa_text = ''

            for topic in question_set[TOPICS].keys():
                tqa_text += question_set[TOPICS][topic][CONTENT][TEXT]
            for topic in question_set[ADJUNCT_TOPICS].keys():
                if CONTENT in question_set[ADJUNCT_TOPICS][topic] \
                        and TEXT in question_set[ADJUNCT_TOPICS][topic][CONTENT]:
                    tqa_text += question_set[ADJUNCT_TOPICS][topic][CONTENT][TEXT]
            for diagram in question_set[DIAGRAM_ANNOTATIONS].keys():
                for annotation in question_set[DIAGRAM_ANNOTATIONS][diagram]:
                    if TEXT in annotation:
                        tqa_text += f' {annotation[TEXT]}.'
            for diagram in question_set[INSTRUCTIONAL_DIAGRAMS].keys():
                if PROCESSED_TEXT in question_set[INSTRUCTIONAL_DIAGRAMS][diagram]:
                    tqa_text += question_set[INSTRUCTIONAL_DIAGRAMS][diagram][PROCESSED_TEXT]

            articles.append({
                TITLE: f'{TQA}-{question_set[LESSON_NAME].lower()}',
                TEXT: tqa_text,
                ID: question_set[GLOBAL_ID],
                FILE: config[QUESTION_DIRECTORY].split('/')[-1]
            })
    return articles
