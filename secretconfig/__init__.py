"""
secretconfig


"""

# plaintext parsers
from parsers import JSONConfig, IniConfig

# encrypted parser magic
import sys
from secureparsers import secureparsers as __sps
for SPName, SPCls in __sps.items():
    setattr(sys.modules[__name__], SPName, SPCls)