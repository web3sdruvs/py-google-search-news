import configparser

class Config:
    '''
    A class for managing configuration settings and blockchain addresses. It also provides methods to retrieve
    specific configuration values.

    Attributes:
    - config_file (str): The path to the configuration file.

    Methods:
    - get_search(): Retrieve the search configuration.
    - get_exclude(): Retrieve the exclusion configuration.
    - get_black_list(): Retrieve the blacklist configuration.
    '''
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get_search(self):
        return self.config['SEARCH']['search']
    
    def get_exclude(self):
        return self.config['EXCLUDE']['exclude']
    
    def get_black_list(self):
        return self.config['BLACK_LIST']['black_list']
    
    def get_period(self):
        return self.config['PERIOD']['period']