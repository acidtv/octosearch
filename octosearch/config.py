import configparser
import os


class Config:

    _config = None

    _multi_keys = ['indexer']

    _defaults = 'config-defaults.ini'

    def __init__(self, defaults_dir, file='config.ini'):
        config = configparser.SafeConfigParser()

        defaults_file = open(os.path.join(defaults_dir, self._defaults), 'r')
        config.read_file(defaults_file)
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
                if (len(key_parts) != 2):
                    raise Exception('`%s` keys in config file must use a name in the key name, for example [indexer:foo]' % key)

                data['name'] = key_parts[1]
                parsed_config[key_parts[0]].append(data)
            else:
                parsed_config[key] = data

        return parsed_config

    def get(self, section, option=None):
        if option and (section not in self._multi_keys):
            # check if config was provided in environment var
            envname = (section + '_' + option).upper()

            if envname in os.environ:
                return os.environ[envname]

        if section not in self._config:
            return None

        if option is None:
            return self._config[section]
        else:
            return self._config[section][option]
