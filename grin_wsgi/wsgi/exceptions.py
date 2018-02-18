class ConfigFileDoesNotExist(Exception):
    """ Wrong config file path was passed """


class WrongConfigSectionName(Exception):
    """ Wrong section is declared in a config file """
