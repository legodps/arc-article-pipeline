import yaml


def load_config(config_path):
    """ Imports a yaml configuration file and all of its properties

        Args:
            config_path (str): the path to a config file

        Returns:
            dict: a set of properties to use
    """
    config = {}
    with open(config_path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    return config
