from unittest import TestCase
from unittest.mock import Mock, call
from arc_benchmark import article_archiver


class TestArticleArchiver(TestCase):
    def test_clean_article_name(self):
        self.assertEqual(
            'fake-article-name',
            article_archiver.clean_article_name(
                r'f\a/k*e? a,r<ti>cle_nam.e'
            ),
            'It should properly clean and replace all illegal characters'
        )

    def test_create_elasticsearch_index(self):
        create_mock = Mock(return_value=True)
        fake_es = Mock(indices=Mock(create=create_mock))
        article_archiver.create_elasticsearch_index('fake_index', fake_es, {'mapping': {}})
        create_mock.assert_called_once_with(index='fake_index', ignore=400, body={})
        
    def test_make_documents(self):
        article_lines = [
            'this is line one',
            'this is line two'
        ]
        test_config = {'index_type': 'sentence'}
        expected_documents = [
            {
                '_op_type': 'index',
                '_index':  'article1',
                '_id': 0,
                '_source': {'text': 'this is line one'.strip()}
            },
            {
                '_op_type': 'index',
                '_index':  'article1',
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

    def test_store_articles(self):
        create_mock = Mock(return_value=True)
        es_mock = Mock(indices=Mock(create=create_mock))
        mock_bulk = Mock(return_value=True)
        fake_articles = [
            {'text': 'this is one fake article. It will be split into two lines', 'title': 'fake_article_1'},
            {'text': 'this is another fake article, but it will only result in one line', 'title': 'fake_article_2'}
        ]
        fake_config = {
            'mapping': {},
            'host': 'bongo',
            'port': 'cat'
        }
        es_docs = [
            {
                '_op_type': 'index',
                '_index': 'fake-article-1',
                '_id': 0,
                '_source': {
                    'text': 'this is one fake article'
                }
            },
            {
                '_op_type': 'index',
                '_index': 'fake-article-1',
                '_id': 1,
                '_source': {
                    'text': 'It will be split into two lines'
                }
            },
            {
                '_op_type': 'index',
                '_index': 'fake-article-2',
                '_id': 0,
                '_source': {
                    'text': 'this is another fake article, but it will only result in one line'
                }
            }
        ]
        article_archiver.store_articles(fake_articles, fake_config, es_mock, mock_bulk)
        create_mock.mock_calls = [
            call(index_name='fake-article-1', ignore=400, body={}),
            call(index_name='fake-article-2', ignore=400, body={})
        ]
        mock_bulk.mock_calls = [
            call(es_mock, es_docs[0]),
            call(es_mock, es_docs[1]),
            call(es_mock, es_docs[2])
        ]
