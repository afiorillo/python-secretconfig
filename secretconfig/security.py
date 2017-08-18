"""
Security
========
Functions that handle encryption/decryption.


"""
import os
import base64
import abc

try:
    import cryptography
except ImportError:
    raise ImportError("""\
Unable to import security.py without having ``cryptography`` package
installed. Try installing again as ``pip install secretconfig[encryption]``.
""")

try:
    import Crypto
except ImportError:
    raise ImportError("""\
Unable to import security.py without having ``pycrypto`` package installed.
Try installing again as ``pip install secretconfig[encryption]``.
""")


########################
# Symmetric Encryption #
########################
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Encryption(object):

    __metaclass__ = abc.ABCMeta

    SHORT_NAME = 'Base'

    #: Hash algorithm from ``cryptography.hazmat.primitives.hashes``
    HASH_ALGORITHM = hashes.SHA512

    #: The maximum length of an stream in bytes
    MAX_STREAM_SIZE = 1 * (2 ** 30) # 1 GB

    @classmethod
    def _check_stream(cls, stream):
        """ Makes streams uniform and enforces limits """
        try: stream = stream.read()
        except AttributeError: pass # then treat it like a string
        if len(stream) > cls.MAX_STREAM_SIZE:
            raise IOError('Unable to process stream of size (%s). Max '
                          'stream size is (%s).' %
                          (len(stream), cls.MAX_STREAM_SIZE))
        return stream

class Symmetric(Encryption):
    """ Simple symmetric encryption with Fernet. """

    SHORT_NAME = 'Symmetric'

    @staticmethod
    def generate_key(**kwargs):
        """ returns a stream for an encryption key """
        return Fernet.generate_key()

    @classmethod
    def encrypt(cls, key, stream, **kwargs):
        """ returns an encrypted stream """
        f = Fernet(key)
        stream = cls._check_stream(stream)
        return f.encrypt(stream)

    @classmethod
    def decrypt(cls, key, encrypted_stream, **kwargs):
        f = Fernet(key)
        encrypted_stream = cls._check_stream(encrypted_stream)
        return f.decrypt(encrypted_stream)

class PasswordSymmetric(Symmetric):
    """ Password-based symmetric encryption with Fernet. """

    SHORT_NAME = 'Password'

    #: Number of iterations to use on the password
    HASH_ITERATIONS = 100000

    @staticmethod
    def generate_key(**kwargs):
        raise NotImplemented('No keys needed, just call '
                             '``encrypt(password, stream)`` and '
                             '``decrypt(password, encrypted_stream)``.')

    @classmethod
    def encrypt(cls, password, stream, salt=None, **kwargs):
        """ uses the password given to encrypt the stream """
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=cls.HASH_ALGORITHM(),
            length=32,
            salt=salt,
            iterations=cls.HASH_ITERATIONS,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f = Fernet(key)
        stream = cls._check_stream(stream)
        return f.encrypt(stream), salt

    @classmethod
    def decrypt(cls, password, encrypted_stream, salt=None, **kwargs):
        """ uses the password and salt given to decrypt the stream """
        if salt is None:
            raise SyntaxError('Cannot decrypt without salt used to encrypt.')
        kdf = PBKDF2HMAC(
            algorithm=cls.HASH_ALGORITHM(),
            length=32,
            salt=salt,
            iterations=cls.HASH_ITERATIONS,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f = Fernet(key)
        encrypted_stream = cls._check_stream(encrypted_stream)
        return f.decrypt(encrypted_stream)


##########################
# Assymmetric Encryption #
##########################
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

class AssymmetricRSA(Encryption):
    """ Assymetric encryption with RSA. """

    SHORT_NAME = 'RSA'

    #: Key size in bits
    KEY_SIZE = 4096

    @classmethod
    def generate_keys(cls, **kwargs):
        """returns a tuple (public, private) keys"""
        private = rsa.generate_private_key(
            public_exponent=65537, # should be fine
            key_size=kwargs.get('key_size', cls.KEY_SIZE),
            backend=default_backend(),
        )
        return (private.public_key(), private)

    @classmethod
    def dumps_private_key(cls, private_key, password=None, **kwargs):
        """ Serializes and encodes the private key into PEM format """
        alg = serialization.NoEncryption()
        if password is not None:
            alg = serialization.BestAvailableEncryption(password)

        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=alg
        )

    @classmethod
    def loads_private_key(cls, pem_string, password=None, **kwargs):
        """ Loads a PEM formatted private key """
        return serialization.load_pem_private_key(
            pem_string, password=password, backend=default_backend()
        )

    @classmethod
    def dumps_public_key(cls, public_key, **kwargs):
        """ Serializes and encodes the public key into PEM format """
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @classmethod
    def loads_public_key(cls, pem_string, **kwargs):
        """ Loads a PEM formatted public key """
        return serialization.load_pem_public_key(
            pem_string, backend=default_backend()
        )

    @classmethod
    def encrypt(cls, public_key, stream, sign_with_private_key=None, **kwargs):
        """ Encrypts the stream with the public key """
        return public_key.encrypt(
            cls._check_stream(stream),
            padding.OAEP(mgf=padding.MGF1(algorithm=cls.HASH_ALGORITHM),
                         algorithm=cls.HASH_ALGORITHM,
                         label=None)
        )

    @classmethod
    def decrypt(cls, private_key, encrypted_stream, **kwargs):
        """ Decrypts the stream with the private key """
        return private_key.decrypt(
            cls._check_stream(encrypted_stream),
            padding.OAEP(mgf=padding.MGF1(algorithm=cls.HASH_ALGORITHM),
                         algorithm=cls.HASH_ALGORITHM, label=None)
        )