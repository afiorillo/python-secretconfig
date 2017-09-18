import json
from collections import OrderedDict as od

import baseclass

class JSONConfig(baseclass.BaseConfig):
    """
    A config parser for JSON-formatted files.

    Usage:

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

    SHORT_NAME = 'JSON'

    @classmethod
    def loads(cls, stream, **kwargs):
        """ Loads a JSON-formatted stream. """
        cfg = cls(defaults=kwargs.get('defaults', None))

        try: obj = json.loads(stream.read())
        except AttributeError: obj = json.loads(stream)

        for section, inner in obj.items():
            if isinstance(inner, dict):
                for key, value in inner.items():
                    cfg._config.append(
                        baseclass.SectionKV(section, key, value)
                    )
            else:
                cfg._config.append(baseclass.GlobalKV(section, inner))
        return cfg

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

class IniConfig(baseclass.BaseConfig):
    """
    A config parser for INI-formatted files.

    Usage:

    >>> cfg = IniConfig(defaults=[('hello', 'world'), ('foo', 'bar', 'baz')])
    >>> cfg.get('hello')
    'world'
    >>> cfg.get('foo', 'bar')
    'baz'
    >>> cfg.set('foo', 'bar', 'bas')
    >>> cfg.dump("test_cfg.ini", overwrite=True)
    >>> cfg2 = IniConfig.load("test_cfg.ini")
    >>> cfg.sections()
    set(['foo'])
    >>> cfg.get('foo', 'bar')
    'bas'

    """

    SHORT_NAME = 'Ini'

    @classmethod
    def loads(cls, stream, **kwargs):
        """ Loads an INI-formatted steam. """

        cfg = cls(defaults=kwargs.get('defaults', None))

        try:
            lines = stream.readlines()
        except AttributeError:
            lines = [l.strip() for l in stream.split('\n') if l.strip()!='']

        section = None
        for lIdx, l in enumerate(lines):
            l = l.strip() # take out whitespace

            # skip comment lines
            if l[0] in ['#', ';']:
                continue

            if l[0] == '[':
                section = l.lstrip('[').rstrip(']')
                continue

            parts = l.split('=')
            try:
                key = parts[0].strip().strip('"')
                value = parts[1].strip().strip('"')
            except IndexError:
                raise ValueError('Line %d has invalid key/value pair' % lIdx+1)

            if section is None:
                cfg._config.append(baseclass.GlobalKV(key, value))
            else:
                cfg._config.append(baseclass.SectionKV(section, key, value))

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