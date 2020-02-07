

def store_question_sets(question_sets):
    """

    """
    for question_set_key in question_sets.keys():
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
            print(f'written {filename}')
