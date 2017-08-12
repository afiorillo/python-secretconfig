import json
from collections import OrderedDict as od

from baseclass import BaseConfig, GlobalKV, SectionKV

class JSONConfig(BaseConfig):
    """
    A config parser for JSON-formatted files.

    Usage
    =====
    >>> cfg = JSONConfig(defaults=[('hello', 'world'), ('foo', 'bar', 'baz')])
    >>> cfg.get('hello')
    'world'
    >>> cfg.get('foo', 'bar')
    'baz'
    >>> cfg.set('foo', 'bar', 'bas')
    >>> cfg.dump("test_cfg.json", overwrite=True)
    >>> cfg2 = JSONConfig.load("test_cfg.json")
    >>> cfg.sections()
    set(['foo'])
    >>> cfg.get('foo', 'bar')
    'bas'

    """

    @classmethod
    def loads(cls, stream, **kwargs):
        """ Loads a JSON-formatted stream. """
        cfg = cls(defaults=kwargs.get('defaults', None))

        try: obj = json.loads(stream.read())
        except AttributeError: obj = json.loads(stream)

        for section, inner in obj.items():
            if isinstance(inner, dict):
                for key, value in inner.items():
                    cfg._config.append(SectionKV(section, key, value))
            else:
                cfg._config.append(GlobalKV(section, inner))
        return obj

    def dumps(self, pretty=True, **kwargs):
        """ Dumps a JSON-formatted stream. """
        obj = od()
        for tup in self.config():
            if len(tup) == 2:
                obj[tup[0]] = tup[1]
            elif len(tup) == 3:
                obj[tup[0]] = obj.get(tup[0], {})
                obj[tup[0]][tup[1]] = tup[2]
        if pretty:
            return json.dumps(obj, indent=4, separators=(',', ': '))
        else:
            return json.dumps(obj)

class IniConfig(BaseConfig):
    """
    A config parser for INI-formatted files.

    Usage
    =====
    >>> cfg = IniConfig(defaults=[('hello', 'world'), ('foo', 'bar', 'baz')])
    >>> cfg.get('hello')
    'world'
    >>> cfg.get('foo', 'bar')
    'baz'
    >>> cfg.set('foo', 'bar', 'bas')
    >>> cfg.dump("test_cfg.ini", overwrite=True)
    >>> cfg2 = JSONConfig.load("test_cfg.ini")
    >>> cfg.sections()
    set(['foo'])
    >>> cfg.get('foo', 'bar')
    'bas'

    """

    @classmethod
    def loads(cls, stream, **kwargs):
        """ Loads an INI-formatted steam. """

        cfg = cls(defaults=kwargs.get('defaults', None))

        try:
            lines = stream.splitlines()
        except AttributeError:
            lines = [l.strip() for l in stream.split('\n') if l.strip()!='']

        section = None
        for lIdx, l in enumerate(lines):
            # skip comment lines
            if l[0] in ['#', ';']:
                continue

            if l[0] == '[':
                section = l.lstrip('[').rstrip(']')
                continue

            parts = l.split('=')
            try:
                key = parts[0]
                value = parts[1].strip('"')
            except IndexError:
                raise ValueError('Line %d has invalid key/value pair' % lIdx+1)

            if section is None:
                cfg._config.append(GlobalKV(key, value))
            else:
                cfg._config.append(SectionKV(section, key, value))

        return cfg

    def dumps(self, **kwargs):
        """ Dumps the config to an INI-formatted stream. """
        lines = []
        for key in self.keys(None):
            lines.append('%s=%s' % (key, self.get(key)))

        for section in self.sections():
            lines.append('[%s]' % section)
            for key in self.keys(section):
                lines.append('%s=%s' % (key, self.get(section, key)))

        return '\n'.join(lines)