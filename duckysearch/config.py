import ConfigParser


class Config:

    _config = None

    def __init__(self, file='config.ini'):
        config = ConfigParser.SafeConfigParser()
        config.read(file)
        self._config = self.parse(config)

    def parse(self, config):
        return config

    def get(self, section, option):
        return self._config.get(section, option)
