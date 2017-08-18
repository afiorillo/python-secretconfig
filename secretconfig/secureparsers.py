"""
Configuration parsers that support encryption.
"""
import inspect
from inspect import isclass, getmembers
from collections import OrderedDict as od

import security
import parsers
from baseclass import BaseConfig

#: The map of secured parsers
secureparsers = od()


for ParserName, ParserCls in getmembers(parsers):
    if isclass(ParserCls) and issubclass(ParserCls, BaseConfig):

        for EncName, EncCls in getmembers(security):
            if isclass(EncCls) and issubclass(EncCls, security.Encryption):

                class Magic(ParserCls, EncCls):
                    PARSER_CLASS = ParserCls
                    ENCRYPTION_CLASS = EncCls

                    def dumps(self, key, *args, **kwargs):
                        obj = self.PARSER_CLASS(self.config())
                        plaintext_stream = obj.dumps(
                            **kwargs
                        )

                        enc_stream = self.ENCRYPTION_CLASS.encrypt(
                            key, plaintext_stream, **kwargs
                        )
                        return enc_stream

                    @classmethod
                    def loads(cls, encrypted_stream, key, **kwargs):
                        plaintext_stream = cls.ENCRYPTION_CLASS.decrypt(
                            key, encrypted_stream, **kwargs
                        )
                        plain_obj = cls.PARSER_CLASS.loads(
                            plaintext_stream, **kwargs
                        )
                        obj = cls(plain_obj.config())
                        return obj

                name = '{enc}{parser}Config'.format(
                    enc=EncCls.SHORT_NAME, parser=ParserCls.SHORT_NAME
                )
                Magic.__name__ = name
                secureparsers[name] = Magic