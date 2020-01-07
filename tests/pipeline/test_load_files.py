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