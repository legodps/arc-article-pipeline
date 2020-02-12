def store_question_sets(question_sets, question_set_ids):
    """ Stores the sets of questions into different files, named based on the question set ID. Not all question sets
        should be saved into files as only a subset will have associated articles to be evaluated on.

        Args:
            question_sets (dict): all questions grouped into different sets based on ID
            question_set_ids (list): the list of question ids the articles should be benchmarked on

        Returns:
            list: all filepaths of the question set files
    """
    question_set_filepaths = []
    for question_set_key in question_sets.keys():
        if question_set_key not in question_set_ids:
            continue

        filename = f'{question_set_key}-ARC-Challenge-Test.jsonl'
        question_set = question_sets[question_set_key]
        jsonl_questions = []

        for question in question_set:
            jsonl_string = '{"id": "' + str(question['id']) + '", "question": {"stem": "' \
                           + question['question']['stem'] + '", "choices": ['
            for choice_index in range(len(question['question']['choices'])):
                if choice_index > 0:
                    jsonl_string += ', '
                jsonl_string += '{"text": "' + question['question']['choices'][choice_index]['text'] \
                    + ', "label": "' + question['question']['choices'][choice_index]['label'] + '"}'
            jsonl_string += ']}, "answerKey": "' + question['answerKey'] + '"}'
            jsonl_questions.append(jsonl_string)

        with open(f'arc-questions/{filename}', 'w') as jsonl_file:
            for question in jsonl_questions:
                jsonl_file.write(f'{question}\n')
            # print(f'written {filename}')

        question_set_filepaths.append(f'arc-questions/{filename}')

    return question_set_filepaths
