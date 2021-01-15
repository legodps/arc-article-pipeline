import json


QUESTION_SET_METRICS_FILEPATH = 'checkpoints/question_set_metrics.json'
QRELS_FILEPATH = 'question-for-extraction/trec-car-benchmarkY3test-section.qrels'


def load_question_set_ids():
    """

    """
    question_set_json = json.load(open(QUESTION_SET_METRICS_FILEPATH, 'r'))
    return list(question_set_json.keys())


def load_paragraph_assessments(question_set_ids):
    """

    """
    relevance_assessments = {}
    for question_set_id in question_set_ids:
        relevance_assessments[question_set_id] = {'1': 0, '2': 0, '3': 0}

    qrels_file = open(QRELS_FILEPATH, 'r')
    line = qrels_file.readline()
    while line:
        paragraph_entry = line.split(' ')
        question_set_id = paragraph_entry[0].split(':')[1].split('/')[0]
        relevance_assessments[question_set_id][paragraph_entry[3].strip()] += 1
        line = qrels_file.readline()

    return relevance_assessments


def calculate_paragraph_relevance():
    """

    """
    question_set_ids = load_question_set_ids()
    relevance_assessments = load_paragraph_assessments(question_set_ids)
    for set_id, relevance_assessment in relevance_assessments.items():
        print(f'{set_id}: {relevance_assessment}')


calculate_paragraph_relevance()
