import os
from unittest import TestCase
from unittest.mock import Mock, call
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
        expected_documents = [
            {
                '_op_type': 'index',
                '_index':  'article1',
                '_id': 0,
                '_type': '_doc',
                '_source': {'text': 'this is line one'.strip()}
            },
            {
                '_op_type': 'index',
                '_index':  'article1',
                '_id': 1,
                '_type': '_doc',
                '_source': {'text': 'this is line two'.strip()}
            }
        ]
        document_generator = article_archiver.make_documents('article1', article_lines, {})
        actual_documents = [article for article in document_generator]
        self.assertEqual(
            expected_documents,
            actual_documents,
            'It should generate proper documents that are valid to insert into Elasticsearch '
        )

    def test_store_articles_not_exist(self):
        create_mock = Mock(return_value=True)
        es_mock = Mock(indices=Mock(create=create_mock, exists=Mock(return_value=False)))
        mock_bulk = Mock(return_value=True)
        fake_articles = [
            {
                'text': 'this is one fake article. It will be split into two lines',
                'title': 'fake_article_1',
                'id': 'manta',
                'file': 'alpha'
            },
            {
                'text': 'this is another fake article, but it will only result in one line',
                'title': 'fake_article_2',
                'id': 'ray',
                'file': 'beta'
            },
            {
                'text': 'this is a third fake article and it will be one line',
                'title': 'fake_article_3',
                'id': 'ray',
                'file': 'beta'
            }
        ]
        fake_config = {'mapping': {}}
        question_set_indices, index_files = article_archiver.store_articles(
            fake_articles,
            es_mock,
            mock_bulk,
            fake_config
        )
        self.assertEqual(
            {'manta': ['fake-article-1'], 'ray': ['fake-article-2', 'fake-article-3']},
            question_set_indices,
            'it should produce a list of article indices associated with their question set ids'
        )
        self.assertEqual(
            {'fake-article-1': 'alpha', 'fake-article-2': 'beta', 'fake-article-3': 'beta'},
            index_files,
            'it should list indices with their associated files'
        )
        create_mock.assert_has_calls([
            call(index='fake-article-1', ignore=400, body={}),
            call(index='fake-article-2', ignore=400, body={}),
            call(index='fake-article-3', ignore=400, body={})
        ])
        mock_bulk.assert_called()

    def test_store_articles_does_exist(self):
        exists_mock = Mock(return_value=True)
        create_mock = Mock(return_value=True)
        es_mock = Mock(indices=Mock(exists=exists_mock, create=create_mock))
        mock_bulk = Mock(return_value=True)
        fake_articles = [
            {
                'text': 'this is one fake article. It will be split into two lines',
                'title': 'fake_article_1',
                'id': 'manta',
                'file': 'alpha'
            },
            {
                'text': 'this is another fake article, but it will only result in one line',
                'title': 'fake_article_2',
                'id': 'ray',
                'file': 'beta'
            },
            {
                'text': 'this is a third fake article and it will be one line',
                'title': 'fake_article_3',
                'id': 'ray',
                'file': 'beta'
            }
        ]
        fake_config = {'mapping': {}}
        question_set_indices, index_files = article_archiver.store_articles(
            fake_articles,
            es_mock,
            mock_bulk,
            fake_config
        )
        self.assertEqual(
            {'manta': ['fake-article-1'], 'ray': ['fake-article-2', 'fake-article-3']},
            question_set_indices,
            'it should produce a list of article indices associated with their question set ids'
        )
        self.assertEqual(
            {'fake-article-1': 'alpha', 'fake-article-2': 'beta', 'fake-article-3': 'beta'},
            index_files,
            'it should list indices with their associated files'
        )
        mock_bulk.assert_not_called()
        create_mock.assert_not_called()

    def test_load_and_store_articles_success(self):
        create_mock = Mock(return_value=True)
        es_mock = Mock(indices=Mock(create=create_mock, exists=Mock(return_value=False)))
        mock_bulk = Mock(return_value=True)
        fake_config = {'mapping': {}}
        question_set_indices, index_files = article_archiver.load_and_store_articles(
            'tests/data-files/articles/test_articles_1.jsonl',
            es_mock,
            mock_bulk,
            fake_config
        )
        self.assertEqual(
            {'efgh': ['test-articles-1-test-title'], 'mnop': ['test-articles-1-full-metal-coding']},
            question_set_indices,
            'it should load the files from the article directory and save them to Elasticsearch'
        )
        self.assertEqual(
            {'test-articles-1-test-title': 'test_articles_1', 'test-articles-1-full-metal-coding': 'test_articles_1'},
            index_files,
            'it should associate the article indices with their file'
        )
        create_mock.assert_has_calls([
            call(index='test-articles-1-test-title', ignore=400, body={}),
            call(index='test-articles-1-full-metal-coding', ignore=400, body={})
        ])
        mock_bulk.assert_called()

    def test_combined_indices(self):
        input_question_set_indices = {
            '1': ['asdf'],
            '2': ['efgh']
        }
        input_new_question_set_indices = {
            '1': ['ijkl'],
            '2': ['mnop']
        }
        expected_output = {
            '1': ['asdf', 'ijkl'],
            '2': ['efgh', 'mnop']
        }
        self.assertEqual(
            expected_output,
            article_archiver.combine_indices(input_new_question_set_indices, input_question_set_indices),
            'it should merge two sets of question set indices together'
        )

    def test_load_and_store_tqa_articles(self):
        exists_mock = Mock(return_value=True)
        create_mock = Mock(return_value=True)
        es_mock = Mock(indices=Mock(exists=exists_mock, create=create_mock))
        mock_bulk = Mock(return_value=True)
        fake_config = {'mapping': {}, 'question_directory': f'{os.getcwd()}/tests/data-files/articles/test_tqa.json'}
        question_set_indices, index_files = article_archiver.load_and_store_tqa_articles(
            {'manta': ['fake-article-0'], 'ray': ['fake-article-2']},
            es_mock,
            mock_bulk,
            fake_config
        )
        expected_combined_indices = {
            'manta': ['fake-article-0', 'tqa-tqa-article'],
            'ray': ['fake-article-2']
        }
        expected_index_files = {
            'tqa-tqa-article': 'test_tqa.json'
        }
        self.assertEqual(
            expected_combined_indices,
            question_set_indices,
            'it should load and store text information from the tqa dataset'
        )
        self.assertEqual(expected_index_files, index_files)
