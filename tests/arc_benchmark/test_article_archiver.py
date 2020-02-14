from unittest import TestCase
from unittest.mock import Mock, call
from elasticsearch import ElasticsearchException
from arc_benchmark import article_archiver


class TestArticleArchiver(TestCase):
    def test_clean_article_name(self):
        self.assertEqual(
            'fake-article-name',
            article_archiver.clean_article_name(
                r'f\a/k*e? a,r<ti>cle_na\'m.e'
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
            {
                'text': 'this is one fake article. It will be split into two lines',
                'title': 'fake_article_1',
                'id': 'manta'
            },
            {
                'text': 'this is another fake article, but it will only result in one line',
                'title': 'fake_article_2',
                'id': 'ray'
            },
            {
                'text': 'this is a third fake article and it will be one line',
                'title': 'fake_article_3',
                'id': 'ray'
            }
        ]
        fake_config = {'mapping': {}}
        question_set_indices = article_archiver.store_articles(fake_articles, es_mock, mock_bulk, fake_config)
        self.assertEqual(
            {'manta': ['fake-article-1'], 'ray': ['fake-article-2', 'fake-article-3']},
            question_set_indices,
            'it should product a list of article indices associated with their question set ids'
        )
        create_mock.assert_has_calls([
            call(index='fake-article-1', ignore=400, body={}),
            call(index='fake-article-2', ignore=400, body={}),
            call(index='fake-article-3', ignore=400, body={})
        ])
        mock_bulk.assert_called()

    def test_load_and_store_articles_success(self):
        create_mock = Mock(return_value=True)
        es_mock = Mock(indices=Mock(create=create_mock))
        mock_bulk = Mock(return_value=True)
        fake_config = {'mapping': {}}
        question_set_indices = article_archiver.load_and_store_articles(
            'tests/data-files/test_file_1.jsonl',
            es_mock,
            mock_bulk,
            fake_config
        )
        self.assertEqual(
            {'efgh': ['test-file-1-test-title'], 'mnop': ['test-file-1-full-metal-coding']},
            question_set_indices,
            'it should load the files from the article directory and save them to Elasticsearch'
        )
        create_mock.assert_has_calls([
            call(index='test-file-1-test-title', ignore=400, body={}),
            call(index='test-file-1-full-metal-coding', ignore=400, body={})
        ])
        mock_bulk.assert_called()

    def test_load_and_store_articles_failure(self):
        create_mock = Mock(side_effect=ElasticsearchException('death walks among you'))
        es_mock = Mock(indices=Mock(create=create_mock))
        mock_bulk = Mock(return_value=True)
        fake_config = {'mapping': {}}
        self.assertRaises(
            ElasticsearchException,
            article_archiver.load_and_store_articles(
                'tests/data-files/test_file_1.jsonl',
                es_mock,
                mock_bulk,
                fake_config
            )
        )
