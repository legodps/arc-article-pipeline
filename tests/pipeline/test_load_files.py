from unittest import TestCase
from pipeline import load_files


class TestLoadFiles(TestCase):
    def test_load_config(self):
        config = load_files.load_config('tests/config-files/test_config.yaml')
        self.assertEqual(
            'test value',
            config['test_property'],
            'It should load in configuration file'
        )
        self.assertEqual(1, len(config.keys()))

    def test_process_article_line(self):
        test_line = '{"paragraphs": [{"para_body": [{"text": "fake"}, {"not": "used", "text": " line"}] }], ' \
                    '"title": "boop"}'
        self.assertEqual(
            {'title': 'boop', 'text': 'fake line'},
            load_files.process_article_line(test_line),
            'It should extract the text entries from the JSON formatted data'
        )

    def test_process_article(self):
        expected_articles = [
            {'title': 'test-title', 'text': 'this is a test of the software that I made for processing articles'},
            {'title': 'full-metal-coding', 'text': 'There are many code bases like this but this one is mine'}
        ]
        test_file = 'tests/data-files/test_file_1'
        self.assertEqual(
            expected_articles,
            load_files.process_article(test_file),
            'It should extract articles from a given JSONL file without a .jsonl extension'
        )
        self.assertEqual(
            expected_articles,
            load_files.process_article(f'{test_file}.jsonl'),
            'It should extract articles from a given JSONL file with the .jsonl extension specified'
        )

    def test_read_jsonl_articles(self):
        expected_articles_partial = [
            {'title': 'pluto-remorse', 'text': 'Poor Pluto, once a planet now relegated to a lesser status'},
            {'title': 'meditation', 'text': 'Ask not for whom the bell tolls, it tolls for thee'}
        ]
        expected_articles_full = [
            {'title': 'test-title', 'text': 'this is a test of the software that I made for processing articles'},
            {'title': 'full-metal-coding', 'text': 'There are many code bases like this but this one is mine'},
            {'title': 'pluto-remorse', 'text': 'Poor Pluto, once a planet now relegated to a lesser status'},
            {'title': 'meditation', 'text': 'Ask not for whom the bell tolls, it tolls for thee'}
        ]
        self.assertEqual(
            expected_articles_partial,
            load_files.read_jsonl_articles('tests/data-files/test_file_2.jsonl'),
            'It should load in a singular file given a singular file filepath'
        )
        self.assertEqual(
            expected_articles_full,
            load_files.read_jsonl_articles('tests/data-files'),
            'It should load in a directory of files given a directory filepath'
        )
