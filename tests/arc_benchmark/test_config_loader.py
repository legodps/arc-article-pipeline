from unittest import TestCase
from arc_benchmark.config_loader import load_config, override_config


class TestConfigLoader(TestCase):
    def test_load_config(self):
        config = load_config('tests/config-files/test_config.yaml')
        self.assertEqual(
            'test value',
            config['test_property'],
            'It should load in configuration file'
        )
        self.assertEqual(1, len(config.keys()))

    def test_override_config(self):
        config = {'bongo': 'cat'}
        self.assertEqual(
            'cat',
            override_config('bongo', None, config),
            'it should default to the corresponding config value if the terminal argument is Falsey'
        )

        self.assertEqual(
            'drums',
            override_config('bongo', 'drums', config),
            'it should use the terminal argument if present'
        )
