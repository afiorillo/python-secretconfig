.. secretconfig documentation master file, created by
   sphinx-quickstart on Mon Sep 18 14:44:58 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===================================================
secretconfig - Configuration files for the paranoid
===================================================

API Documentation
=================

Base Classes
------------

.. autoclass:: secretconfig.baseclass.GlobalKV

   A key/value pair used for "global" configuration values.

.. autoclass:: secretconfig.baseclass.SectionKV

   A section/key/value tuple used for "sectioned" configuration values.

.. autoclass:: secretconfig.baseclass.BaseConfig
   :members:


Plaintext Parsers
-----------------

.. autoclass:: secretconfig.JSONConfig
   :members:

.. autoclass:: secretconfig.IniConfig
   :members:

Encryption Mix-Ins
------------------

.. autoclass:: secretconfig.security.Symmetric
   :members:

.. autoclass:: secretconfig.security.PasswordSymmetric
   :members:

.. autoclass:: secretconfig.security.AssymmetricRSA
   :members:

..  Indices and tables
    ==================
    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
