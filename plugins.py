import os

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

		for file in os.listdir('./' + self._type + '/'):
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


