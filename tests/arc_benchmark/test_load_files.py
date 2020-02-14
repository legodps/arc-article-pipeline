from unittest import TestCase
from arc_benchmark.load_files import process_article_line, process_article, read_jsonl_articles, retrieve_questions, \
    read_json_questions


class TestLoadFiles(TestCase):
    def test_process_article_line(self):
        test_line = '{"squid": "lol:asdf", "title": "boop", "paragraphs": [{"para_body": [{"text": "fake"},' \
                    '{"not": "used", "text": " line"}] }] }'
        self.assertEqual(
            {'title': 'bongo_cat-boop', 'text': 'fake line', 'id': 'asdf'},
            process_article_line(test_line, 'bongo_cat'),
            'It should extract the text entries from the JSON formatted data'
        )

    def test_process_article(self):
        expected_articles = [
            {
                'title': 'test_file_1-test-title',
                'text': 'this is a test of the software that I made for processing articles',
                'id': 'efgh'
            },
            {
                'title': 'test_file_1-full-metal-coding',
                'text': 'There are many code bases like this but this one is mine',
                'id': 'mnop'
            }
        ]
        test_file = 'tests/data-files/test_file_1'
        self.assertEqual(
            expected_articles,
            process_article(test_file),
            'It should extract articles from a given JSONL file without a .jsonl extension'
        )
        self.assertEqual(
            expected_articles,
            process_article(f'{test_file}.jsonl'),
            'It should extract articles from a given JSONL file with the .jsonl extension specified'
        )

    def test_read_jsonl_articles(self):
        expected_articles_partial = [
            {
                'title': 'test_file_2-pluto-remorse',
                'text': 'Poor Pluto, once a planet now relegated to a lesser status',
                'id': 'uvwx'
            },
            {
                'title': 'test_file_2-meditation',
                'text': 'Ask not for whom the bell tolls, it tolls for thee',
                'id': 'cdef'
            }
        ]
        expected_articles_full = [
            {
                'title': 'test_file_1-test-title',
                'text': 'this is a test of the software that I made for processing articles',
                'id': 'efgh'
            },
            {
                'title': 'test_file_1-full-metal-coding',
                'text': 'There are many code bases like this but this one is mine',
                'id': 'mnop'
            },
            {
                'title': 'test_file_2-pluto-remorse',
                'text': 'Poor Pluto, once a planet now relegated to a lesser status',
                'id': 'uvwx'
            },
            {
                'title': 'test_file_2-meditation',
                'text': 'Ask not for whom the bell tolls, it tolls for thee',
                'id': 'cdef'
            }
        ]
        self.assertEqual(
            expected_articles_partial,
            read_jsonl_articles('tests/data-files/test_file_2.jsonl'),
            'It should load in a singular file given a singular file filepath'
        )
        self.assertEqual(
            expected_articles_full,
            read_jsonl_articles('tests/data-files'),
            'It should load in a directory of files given a directory filepath'
        )
