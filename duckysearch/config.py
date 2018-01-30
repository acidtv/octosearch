import ConfigParser


class Config:

    _config = None

    _multi_keys = ['indexer']

    def __init__(self, file='config.ini'):
        config = ConfigParser.SafeConfigParser()
        config.read(file)
        self._config = self.parse(config)

    def parse(self, raw_config):
        parsed_config = {}

        for key in self._multi_keys:
            parsed_config[key] = []

        for key in raw_config.sections():
            key_parts = key.split(':')
            data = dict(raw_config.items(key))

            if key_parts[0] in self._multi_keys:
                data['name'] = key_parts[1]
                parsed_config[key_parts[0]].append(data)
            else:
                parsed_config[key] = data

        return parsed_config

    def get(self, section, option=None):
        if option is None:
            return self._config[section]
        else:
            return self._config[section][option]
