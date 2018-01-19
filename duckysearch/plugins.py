import pkg_resources


def get(type, plugin):
    dist, name = plugin.split(':')
    return pkg_resources.load_entry_point(dist=dist, group='duckysearch.' + type, name=name)


def list(type):
    return pkg_resources.iter_entry_points(group='duckysearch.' + type)
