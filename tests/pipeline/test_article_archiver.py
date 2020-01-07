from unittest import TestCase
from pipeline import article_archiver

class TestArticleArchiver(TestCase):
    def test_clean_article_name(self):
        self.assertEqual(
            'fake-article-name',
            article_archiver.clean_article_name(
                r'f\a/k*e? a,r<ti>cle_nam.e'
            ),
            'It should properly clean and replace all illegal characters'
        )
        
    def test_make_documents(self):
        article_lines = [
            'this is line one',
            'this is line two'
        ]
        test_config = {'index_type': 'sentence'}
        expected_documents = [
            {
                '_op_type': 'create',
                '_index':  'article1',
                '_type': 'sentence',
                '_id': 0,
                '_source': {'text': 'this is line one'.strip()}
            },
            {
                '_op_type': 'create',
                '_index':  'article1',
                '_type': 'sentence',
                '_id': 1,
                '_source': {'text': 'this is line two'.strip()}
            }
        ]
        document_generator = article_archiver.make_documents('article1', article_lines, test_config)
        actual_documents = [article for article in document_generator]
        self.assertEqual(
            expected_documents,
            actual_documents,
            'It should generate proper documents that are valid to insert into Elasticsearch '
        )