import json
import random
from scipy.stats import kendalltau, spearmanr, sem

# Numbering of algorithms
rerank2_bert = 1
dangnt_nlp = 2
bert_cknrm_50 = 3
irit_run2 = 4
rerank3_bert = 5
ict_b_convk= 6
irit_run1 = 7
bm25_populated = 8
unh_tfidf_ptsim = 9
irit_run3 = 10
unh_bm25_ecmpsg = 11
ecnu_bm25_1 = 12
ict_b_drmmtks = 13
uvabottomupchangeorder = 14
uvabm25rm3 = 15
uvabottomup2 = 16

DECIMAL_DIGITS = 4
RESULTS_FILE = 'checkpoints/aggregated_correlation_metrics.json'
INFORMATIVENESS = 'informativeness'
KENDALL = 'kendall'
MAP = 'map'
NDCG = 'ndcg'
RANKING = 'ranking'
ROUGE = 'rouge'
RPREC = 'rprec'
SPEAR = 'spear'
TIE = 'tie'
TIES = 'ties'
TIE_RERUNS = 10

# excluding rerank3 bert and irit-run1 until I get results from laura
informativeness = {
    RANKING: [
        rerank2_bert, dangnt_nlp, bert_cknrm_50, irit_run2, rerank3_bert, ict_b_convk, irit_run1, bm25_populated,
        unh_tfidf_ptsim, irit_run3, unh_bm25_ecmpsg, ecnu_bm25_1, ict_b_drmmtks, uvabottomupchangeorder, uvabm25rm3,
        uvabottomup2
    ]
}

# tie between unh-bm25-ecmpsg and unh-tfidf-tsim, irit-run3 and irit-run2
rprec = {
    RANKING: [
        dangnt_nlp, rerank3_bert, rerank2_bert, TIE, ecnu_bm25_1, ict_b_convk, bm25_populated, TIE, bert_cknrm_50,
        uvabm25rm3, uvabottomupchangeorder, uvabottomup2, ict_b_drmmtks
    ],
    TIES: [[irit_run1, irit_run2, irit_run3], [unh_bm25_ecmpsg, unh_tfidf_ptsim]]
}

# tie between irit-run2 and irit-run3, unh-tfidf-ptsim and unh-bm25-ecmpsg
map = {
    RANKING: [
        dangnt_nlp, rerank3_bert, rerank2_bert, TIE, ecnu_bm25_1, ict_b_convk, bm25_populated, TIE, bert_cknrm_50,
        uvabm25rm3, uvabottomupchangeorder, uvabottomup2, ict_b_drmmtks
    ],
    TIES: [[irit_run1, irit_run2, irit_run3], [unh_bm25_ecmpsg, unh_tfidf_ptsim]]
}

# tie between unh-tfidf-ptsim and unh-bm25-ecmpsg, irit-run2 and irit-run3
ndcg = {
    RANKING: [
        dangnt_nlp, rerank3_bert, rerank2_bert, TIE, ecnu_bm25_1, ict_b_convk, bm25_populated, TIE, bert_cknrm_50,
        uvabm25rm3, uvabottomupchangeorder, uvabottomup2, ict_b_drmmtks
    ],
    TIES: [[irit_run1, irit_run2, irit_run3], [unh_bm25_ecmpsg, unh_tfidf_ptsim]]
}

# excluding irit-run1 and rerank3-bert
rouge = {
    RANKING: [
        ecnu_bm25_1, bert_cknrm_50, uvabm25rm3, uvabottomupchangeorder, irit_run2, irit_run3, irit_run1, rerank3_bert,
        unh_bm25_ecmpsg, bm25_populated, unh_tfidf_ptsim, rerank2_bert, dangnt_nlp, uvabottomup2, ict_b_convk,
        ict_b_drmmtks
    ]
}

metric_rankings = {
    INFORMATIVENESS: informativeness,
    RPREC: rprec,
    MAP: map,
    NDCG: ndcg,
    ROUGE: rouge
}


def decide_tie(tied_algorithms):
    """ Randomly orders a list of algorithms that are tied

        Args:
            tied_algorithms (list): a list of algorithms that are all tied

        Returns:
            list: a randomly permuted list sampled without replacement from tied_algorithms
    """
    return random.sample(tied_algorithms, len(tied_algorithms))


def generate_randomized_rankings(ranking, run_count):
    """ Generates run_count number of lists, if a ranking has any ties, randomize the ties to create a permuted list

        Args:
            ranking (dict): contains the order and ties of a ranking of algorithm runs
            run_count (int): the number of rankings that should be generated

        Returns:
            list: a list containing all of the rankings generated from an initial ranking
    """
    randomized_rankings = []
    count = 0
    while count < run_count:
        if TIES not in ranking.keys():
            randomized_rankings.append(ranking[RANKING])
        else:
            randomized_ranking = []
            tie_count = 0
            for algorithm in ranking[RANKING]:
                if algorithm != TIE:
                    randomized_ranking.append(algorithm)
                else:
                    randomized_ranking = randomized_ranking + decide_tie(ranking[TIES][tie_count])
                    tie_count += 1
            randomized_rankings.append(randomized_ranking)

        count += 1
    return randomized_rankings


def correlate_rankings(randomized_rankings):
    """ Calculates the kendall's Tau and Spearman's rank correlation between two rankings

        Args:
            randomized_rankings (dict): a dictionary containing the generated rankings to be evaluated for correlation

        Returns:
            dict: a dictionary containing the correlations between all metrics per generated ranking
    """
    metric_correlations = {}
    metric_index = 0
    while metric_index < len(randomized_rankings.keys()) - 1:
        for second_metric_index in range(metric_index + 1, len(randomized_rankings.keys())):
            first_metric_name = list(randomized_rankings.keys())[metric_index]
            second_metric_name = list(randomized_rankings.keys())[second_metric_index]
            first_second_metric_kendall = []
            first_second_metric_spear = []
            for run_index in range(len(randomized_rankings[list(randomized_rankings.keys())[metric_index]])):
                kendall_correlation, _ = kendalltau(
                    randomized_rankings[first_metric_name][run_index],
                    randomized_rankings[second_metric_name][run_index]
                )
                first_second_metric_kendall.append(kendall_correlation)
                spear_correlation, _ = spearmanr(
                    randomized_rankings[first_metric_name][run_index],
                    randomized_rankings[second_metric_name][run_index]
                )
                first_second_metric_spear.append(spear_correlation)
            metric_correlations[(first_metric_name, second_metric_name, KENDALL)] = first_second_metric_kendall
            metric_correlations[(first_metric_name, second_metric_name, SPEAR)] = first_second_metric_spear

        metric_index += 1
    return metric_correlations


def aggregate_correlations(correlation_results):
    """ Calculates an average and standard deviation for each group of correlations calculated for each generated
        ranking

        Args:
            correlation_results (dict): the correlation lists by each metric and correlation statistic

        Returns:
            dict: the dictionary of average and standard deviation of each metric by the correlation statistic
    """
    aggregated_correlations = {}
    for metric_tuple in correlation_results.keys():
        if f'{(metric_tuple[0], metric_tuple[1])}' not in aggregated_correlations.keys():
            aggregated_correlations[f'{(metric_tuple[0], metric_tuple[1])}'] = {}
        aggregated_correlations[f'{(metric_tuple[0], metric_tuple[1])}'] = {
            **aggregated_correlations[f'{(metric_tuple[0], metric_tuple[1])}'],
            f'average_{metric_tuple[2]}': round(
                sum(correlation_results[metric_tuple]) / len(correlation_results[metric_tuple]),
                DECIMAL_DIGITS
            ),
            f'{metric_tuple[2]}_std_dev': round(sem(correlation_results[metric_tuple]), DECIMAL_DIGITS)
        }
    return aggregated_correlations


def calculate_correlation(rankings, random_reruns=10):
    """ Orchestrates the calculation of the average correlation between each metric and stores the results in a json
        file

        Args:
            rankings (dict): a dict of dicts containing the metric rankings and ties
            random_reruns (int): (optional) the number of randomized rerankings to make ties fair
    """
    randomized_rankings = {}
    for ranking_name in rankings.keys():
        randomized_rankings[ranking_name] = generate_randomized_rankings(
            rankings[ranking_name],
            random_reruns
        )

    correlation_results = correlate_rankings(randomized_rankings)
    aggregated_metrics = aggregate_correlations(correlation_results)

    json_file = open(f'{RESULTS_FILE}', 'w')
    json.dump(aggregated_metrics, json_file)
    json_file.close()


calculate_correlation(metric_rankings, TIE_RERUNS)
