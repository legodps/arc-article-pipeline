import os
from unittest import TestCase
from arc_benchmark.benchmark_set_creator import create_or_clean_directory, create_test_sets


class TestQuestionSetCreator(TestCase):
    def test_create_or_clean_directory(self):
        if os.path.isdir('fake_directory_dont_use'):
            self.assertTrue(False, 'directory of fake_directory_dont_use is already in use, dont use it >:(')
        else:
            create_or_clean_directory({'benchmark_set_directory': 'fake_directory_dont_use'})
            self.assertTrue(os.path.isdir('fake_directory_dont_use'), 'it should create a directory')

            open('fake_directory_dont_use/empty_file.txt', 'a').close()
            create_or_clean_directory({'benchmark_set_directory': 'fake_directory_dont_use'})
            self.assertFalse(
                os.path.isfile('fake_directory_dont_use/empty_file.txt'),
                'it should clean out any files in the configured test set directory'
            )
            self.assertTrue(os.path.isdir('fake_directory_dont_use'))
            os.rmdir('fake_directory_dont_use')