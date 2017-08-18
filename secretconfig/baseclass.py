"""
The base classes for ``secretconfig``.
"""
from __future__ import print_function, absolute_import, unicode_literals

from collections import Iterable, namedtuple
from abc import ABCMeta
from os import path

#: Base exception for ``secretconfig`` errors.
class Error(Exception): pass

#: The exception raised when attempting to parse an invalid configuration file.
class ParsingError(Error, IOError): pass

#: The exception raised when trying to access keys or values from a section that does not exist.
class UnknownSectionError(Error, KeyError): pass

#: The exception raised when trying to access keys that do not exist
class UnknownKeyError(Error, KeyError): pass

#: The structured tuple for ``GLOBAL`` key/value pairs
GlobalKV = namedtuple('GlobalKV', ['key', 'value'])

#: The structured tuple for section-specific key/value pairs
SectionKV = namedtuple('SectionKV', ['section', 'key', 'value'])

class BaseConfig(object):
    """ The base configuration object. """
    # __metaclass__ = ABCMeta

    SHORT_NAME = 'Base'

    def __init__(self, defaults=None, *args, **kwargs):
        """
        Construct a configuration instance.
        :param defaults: (Default=None). A list of tuples to set as defaults for the configuration instance. Tuples \
        can either be 2-tuples (key,value) for ``GLOBAL`` key/value pairs or 3-tuples (section,key,value) for \
        section-specific configurations.
        """
        self.__defaults = []
        if defaults is not None: self.set_defaults(defaults)

        self._config = []

    def set_defaults(self, defaults):
        self.__defaults = []
        try:
            assert(isinstance(defaults, Iterable))
            for indx, default in enumerate(defaults):
                parsedDefault = self.parse_default(default)
                self.__defaults.append(parsedDefault)
        except AssertionError:
            raise Error('Invalid defaults list given (%s). Must be a list of parsable defaults.' % defaults)

    @staticmethod
    def parse_default(default):
        """
        Parses one of the elements in a defaults list. Returns either a ``GlobalKV`` or a ``SectionKV``.
        
        Accepts either a 2-tuple (for ``GlobalKV`` defaults) or a 3-tuple (for ``SectionKV`` defaults). 2-tuples are 
        parsed as (key,value) and 3-tuples are parsed as (section,key,value).
        """
        if not (isinstance(default, Iterable) and len(default) in [2, 3]):
            raise Error('Invalid default value given (%s). Must be a 2-tuple or 3-tuple.' % default)
        elif len(default) == 2:
            # print('parsing2:', default)
            return GlobalKV(*default)
        elif len(default) == 3:
            # print('parsing3:', default)
            return SectionKV(*default)

    def defaults(self):
        """ Returns a list of tuples containing the defaults for this configuration instance. """
        return self.__defaults

    def config(self):
        """
        Returns a list of tuples containing the current values (default or otherwise) for this configuration instance.
        """
        out = [tup for tup in self._config] # makes a copy of the list
        for defTup in self.defaults():
            matchingTups = [tup for tup in out if tup.key == defTup.key]
            if isinstance(defTup, GlobalKV) and len(matchingTups)==0:
                # it was a global and there isn't an entry with that key
                out.append(defTup)
            elif isinstance(defTup, SectionKV):
                matchingTups = [
                    tup for tup in matchingTups if (
                        isinstance(tup,SectionKV) and
                        tup.section==defTup.section
                    )]
                if len(matchingTups) == 0:
                    out.append(defTup)
        return out

    def sections(self):
        """ Returns a set of available sections. """
        sections = set()
        for tup in self._config + self.defaults():
            try: sections.add(tup.section)
            except AttributeError: pass
        return sections

    def has_section(self, section):
        """ Returns TF whether a SectionKV with the named ``section`` exists in this configuration instance. """
        try:
            next(tup for tup in self._config if tup.section==section)
        except StopIteration:
            return False # no tuple in the config matched that section
        else:
            return True # at least one tuple in the config did match

    def keys(self, *args):
        """
        Returns the keys available in the given ``section``. If ``section is None`` then returns the ``GLOBAL`` keys.
        :raises UnknownSectionError: If ``section`` is not in the list of available sections.
        """
        if len(args) == 0 or args[0] is None:
            return [tup.key for tup in self.config()
                    if isinstance(tup, GlobalKV)]
        elif args[0] not in self.sections():
            raise UnknownSectionError('Section (%s) is not available.' %
                                      args[0])
        else:
            keys = [tup.key for tup in self.config()
                    if (isinstance(tup, SectionKV) and tup.section==args[0])]
            return keys

    def has_key(self, section, key):
        """
        Returns TF if the ``key`` is available in the given ``section``. Returns False if either the ``section`` or \
        ``key`` does not exist.
        """
        try: return key in self.keys(section)
        except UnknownSectionError: return False

    def get(self, *args):
        """
        Returns the value for the given option. Can either be called ``get(key)`` for global key/value pairs or \
        ``get(section, key)`` for section-specific key/value pairs.
        :raises UnknownSectionError: If the ``section`` (if given) is not available.
        :raises UnknownKeyError: If the given ``key`` is not available in the ``section`` (if given) or globally (if \
        not).
        """
        if len(args) == 1:
            section = None
            key = args[0]
        elif len(args) == 2:
            section = args[0]
            key = args[1]
        else:
            raise SyntaxError('Can either be called ``get(key)`` or ``get(section, key)``.')

        if key not in self.keys(section):
            if section is None:
                raise UnknownKeyError('Global key (%s) is not available.' % key)
            else:
                raise UnknownKeyError('Section/key (%s/%s) is not available.' % (section, key))

        matches = [tup for tup in self.config() if tup.key == key]
        if section is not None:
            matches = [tup for tup in matches if (isinstance(tup, SectionKV) and tup.section == section)]

        try:
            assert (len(matches) == 1)
        except AssertionError:
            pass # this is a problem
        else:
            return matches[0].value

    def set(self, *args):
        """
        Sets the value for the given option. Can either be called ``set(key, value)`` for global key/value pairs or \
        ``set(section, key, value)`` for section-specific key/value pairs. Overwrites any existing values.
        """
        if len(args) == 2:
            section = None
            key = args[0]
            value = args[1]
        elif len(args) == 3:
            section = args[0]
            key = args[1]
            value = args[2]
        else:
            raise SyntaxError('Can either be called ``set(key, value)`` or ``set(section, key, value)``. ')

        if section is None:
            tup = GlobalKV(key, value)
        else:
            tup = SectionKV(section, key, value)

        # remove the old tuple's value, if it's there
        for oldTup in self._config:
            if (oldTup.key == tup.key) and ( # keys match
                # and, if they're section-specific, their sections match too
                isinstance(oldTup, SectionKV) and isinstance(tup, SectionKV) and oldTup.section == tup.section
            ):
                self._config.remove(oldTup)
                break

        # and add in the new tuple's value
        self._config.append(tup)

    def getint(self, *args):
        """
        Helper function that coerces the value to be an integer.
        :raises ValueError: If the option cannot be coerced into an integer.
        """
        return int(self.get(*args))

    def getbool(self, *args):
        """
        Helper function that coerces the value to be a boolean.
        :raises ValueError: If the option cannot be coerced into a boolean.
        """
        return bool(self.get(*args))

    def items(self, section):
        """ Returns a list of tuples in the given section. If ``section is None`` returns the global tuples. """
        if section is None:
            return [tup for tup in self.config() if isinstance(tup, GlobalKV)]
        else:
            return [tup for tup in self.config() if (isinstance(tup, SectionKV) and tup.section == section)]

    @classmethod
    def load(cls, filenames, *args, **kwargs):
        """
        Loads the given filename(s) as a configuration

        Attempts to read a list of potential filenames, ignoring filenames \
        that cannot be accessed.

        :param filenames: A filename or a list of potential filenames to try.
        :param defaults: (Default=[]) A list of tuples to act as default \
        parameters. Two-tuples map to global key/value pairs and three-tuples \
        map to section/key/value triplets.
        :raises OSError: If none of the filenames can be accessed.
        :raises ParsingError: If an accessible filename is incorrectly formatted (not parsable).
        """
        if isinstance(filenames, str):
            filenames = [filenames]

        for fName in filenames:
            if path.exists(fName):
                try:
                    with open(fName, 'r') as fIn:
                        return cls.loads(fIn, **kwargs)
                except IOError:
                    pass  # non-accessible
                except ValueError:
                    raise ParsingError('Unable to parse file. %s' % fName)
        raise ValueError('No given filenames can be loaded. [%s]' % filenames)

    def dump(self, filename, overwrite=False, *args, **kwargs):
        """
        Writes the configuration out to the given filename.

        :param filename: The target file to write the configuration to.
        :param overwrite: (Default=False). If False and the target \
        ``filename`` already exists, fails.
        :raises OSError: If ``overwrite==False`` and ``filename`` already \
        exists.
        """
        if path.exists(filename) and (not overwrite):
            raise OSError('File already exists. %s' % filename)

        with open(filename, 'w') as fOut:
            return fOut.write(self.dumps(**kwargs))

    @classmethod
    def loads(cls, stream, **kwargs):
        """ Loads a configuration from the given stream. """
        raise NotImplementedError('``loads`` is not implemented in the base '
                                  'class.')

    @classmethod
    def dumps(cls, **kwargs):
        """ Serialized the configuration instance into the stream. """
        raise NotImplementedError('``dumps`` is not implemented in the base '
                                  'class.')

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def __str__(self):
        return self.dumps()