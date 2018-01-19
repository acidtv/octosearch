import os
import pkg_resources


def get(type, plugin):
    dist, name = plugin.split(':')

    try:
        return pkg_resources.load_entry_point(dist=dist, group='duckysearch.' + type, name=name)
    except Exception as e:
        # FIXME
        raise e


def list(type):
    return pkg_resources.iter_entry_points(group='duckysearch.' + type)


class Plugins:
	def load(self, plugin):
		'''Return a reference to requested class, not an instance'''

		module_name = self._get_module(plugin)
		class_name = self._get_class(plugin)

		mod = __import__(module_name, globals(), locals(), [class_name])
		obj = getattr(mod, class_name)()

		return obj

	def list_plugins(self):
		'''Return a list of plugins for current type'''

                my_path = os.path.dirname(os.path.realpath(__file__))

		for file in os.listdir(my_path + '/' + self._type + '/'):
			if file[-3:] != '.py' or file[:1] == '_':
				continue

			plugin = file[:-3].capitalize()
			yield plugin

	def _get_module(self, plugin):
		'''Generate module name from plugin name'''
		return self._type.lower() + '.' + plugin.lower()

	def _get_class(self, plugin):
		'''Generate class name from plugin name'''
		return self._type.capitalize() + plugin.capitalize()


