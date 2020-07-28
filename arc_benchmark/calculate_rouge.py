import re
import json
import os
import sys
import nltk
from scipy.stats import sem

print(os.getcwd())
sys.path.append('../arc-pipeline')

from file_utils import read_jsonl_articles, load_tqa_articles
from constants import FILE, ID, QUESTION_DIRECTORY, TEXT

decimal_digits = 4
article_directory = '../generated_articles'
config_for_tqa_load = {QUESTION_DIRECTORY: 'question-for-extraction/tqa_v1_train.json'}
results_file = 'checkpoints/rouge_1_results.json'

nltk.download('wordnet')


def clean_and_split(text):
    """

    """
    lemmatizer = nltk.WordNetLemmatizer()
    stop_words = set(nltk.corpus.stopwords.words('english'))

    word_tokens = nltk.word_tokenize(re.sub('[!?.,]', '', text))

    filtered_sentence = []
    for word in word_tokens:
        if word not in stop_words:
            filtered_sentence.append(lemmatizer.lemmatize(word))
    return filtered_sentence


def get_unigram_overlap(algorithm_unigrams, reference_unigrams):
    """

    """
    overlap = 0
    for word in algorithm_unigrams:
        if word in reference_unigrams:
            overlap += 1
    return overlap


def calculate_rouge_metrics(article_text, reference_text):
    """

    """
    article_unigrams = clean_and_split(article_text)
    reference_unigrams = clean_and_split(reference_text)
    overlap = get_unigram_overlap(article_unigrams, reference_unigrams)

    rouge_precision = overlap / len(article_unigrams)
    rouge_recall = overlap / len(reference_unigrams)
    rouge_f1 = 2 * ((rouge_precision * rouge_recall) / (rouge_precision + rouge_recall))

    return {
        'precision': rouge_precision,
        'recall': rouge_recall,
        'f1': rouge_f1
    }


def get_algorithm_rouge_score(articles, reference_chapters):
    """

    """
    f1_scores = []
    precision_scores = []
    recall_scores = []

    for article in articles:
        reference_chapter = {}
        for chapter in reference_chapters:
            if article[ID] == chapter[ID]:
                reference_chapter = chapter

        scores = calculate_rouge_metrics(article[TEXT], reference_chapter[TEXT])
        f1_scores.append(scores['f1'])
        precision_scores.append(scores['precision'])
        recall_scores.append(scores['recall'])

    return {
        'average_f1': round(sum(f1_scores) / len(f1_scores), decimal_digits),
        'f1_std_dev': round(sem(f1_scores), decimal_digits),
        'average_precision': round(sum(precision_scores) / len(precision_scores), decimal_digits),
        'precision_std_dev': round(sem(precision_scores), decimal_digits),
        'average_recall': round(sum(recall_scores) / len(recall_scores), decimal_digits),
        'recall_std_dev': round(sem(recall_scores), decimal_digits)
    }


def calculate_algorithm_rouge_1():
    print('Loading in articles for to evaluate with Rouge')

    all_articles = read_jsonl_articles(article_directory)

    algorithm_articles = {}
    chapter_ids = {}
    for article in all_articles:
        chapter_ids[article[ID]] = ''
        if article[FILE] not in algorithm_articles:
            algorithm_articles[article[FILE]] = []
        algorithm_articles[article[FILE]].append(article)

    reference_articles = load_tqa_articles(chapter_ids, config_for_tqa_load)

    rouge_results = []
    algorithm_count = 1
    for article_filename in algorithm_articles.keys():
        print(f'Calculating Rouge 1 for algorithm {algorithm_count}')
        algorithm_results = get_algorithm_rouge_score(algorithm_articles[article_filename], reference_articles)
        algorithm_results[FILE] = article_filename
        rouge_results.append(algorithm_results)
        algorithm_count += 1

    json_file = open(f'{results_file}', 'w')
    json.dump(rouge_results, json_file)
    json_file.close()

    print(f'Rouge 1 results stored to {results_file}')

calculate_algorithm_rouge_1()