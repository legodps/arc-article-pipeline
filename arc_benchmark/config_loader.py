import yaml


def load_config(config_path):
    """ Imports a yaml configuration file and all of its properties

        Args:
            config_path (str): the path to the yaml configuration file

        Returns:
            dict: a set of properties to use in the benchmark
    """
    with open(config_path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config


def override_config(prop, args_value, config):
    """ Returns the terminal argument if present, otherwise returns the corresponding config property

        Args:
            prop (str): the key of the config property to use in absence of terminal argument
            args_value (various): the terminal argument being examined
            config (dict): the config to supplement from given missing terminal arguments

        Returns:
            various: either the terminal argument if present or the appropriate config value if not
    """
    if not args_value and prop in config.keys():
        return config[prop]

    return args_value
