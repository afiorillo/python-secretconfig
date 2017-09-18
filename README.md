secretconfig
---
A configuration parsing library for the paranoid.


## Installation
Clone and use `pip`
```bash
git clone https://github.com/andrewmfiorillo/python-secretconfig.git
pushd python-secretconfig
pip install .
```

## Usage
Basic usage of a plaintext parser looks like
```python
from secretconfig import JSONConfig, IniConfig

# create a configuration
cfg = JSONConfig()
cfg.set('host', '127.0.0.1')
cfg.set('auth', 'username', 'gaping_security_hole')
cfg.set('auth', 'password', 'plaintext_password')
cfg.dump('configuration.json')
# ... and later, load it again
newCfg = JSONConfig.load('configuration.json')
assert(newCfg.get('host') == '127.0.0.1')
assert(newCfg.get('password') == 'plaintext_password'
```

Storing a plaintext password is **BAD**<sup>[citation needed]</sup>.
Encrypting the password is less bad but
  sometimes a necessary evil.
If you must do evil, you owe it to yourself to do it well.
`secretconfig` exposes a few different encryption schemes that are better
suited to different situations.

### Password-based Encryption
Password-based encryption requires a `password` to encrypt the
configuration. Decrypting the configuration requires that same `password` as
 well as a `salt` produced when encryption occurred.

For example, let's say you have an application with many users, each of whom
 have their own configuration.
You could store the salt and the configurations, and each user could decrypt
 only their configuration with their password.

To use password-based configurations
```python
import secretconfig as sc

# create a configuration
cfg = sc.PasswordJSONConfig()
cfg.set('account_number', '1234567890')
salt = cfg.dump('config.json.pw.enc', 'password')
# ... and later, load it again
cfg = sc.PasswordJSONConfig.load('config.json.pw.enc', 'password', salt=salt)
```
Note: the `salt` changes every time the configuration is encrypted again,
but it can be decrypted any number of times with the same `salt`/`password`
combination.

### Symmetric Key Configuration
Symmetric key encryption uses a single key to both encrypt and decrypt
the configuration.

An example use case could be a group of developers working on the same
server. As long as they can share a key securely then they can share the
encrypted configuration file over public channels.

To use symmetric key encryption
```python
import secretconfig as sc

# create the key
key = sc.SymmetricJSONConfig.generate_key()
with open('super_secret.key', 'wb') as fOut:
    fOut.write(key)

# create the config
cfg = sc.SymmetricJSONConfig()
cfg.set('server', 'username', 'admin')
cfg.set('server', 'password', 'password')
cfg.dump('config.json.sym.enc', key)
# ... and later, load it
with open('super_secret.key', 'rb') as fIn:
    key = fIn.read()
cfg = sc.SymmetricJSONConfig.load('config.json.sym.enc', key)
```

### Asymmetric (RSA) Encryption
Asymmetric encryption uses two keys: a public key (used to encrypt and only
encrypt) and a private key (used to decrypt and only decrypt).
In this implementation, the private key can be password secured for
additional protection.

To use asymmetric encryption
```python
import secretconfig as sc

# generate the key pair
public_key, private_key = sc.RSAJSONConfig.generate_keys()
with open('private_key.pem', 'wb') as fOut:
    fOut.write(sc.RSAJSONConfig.dumps_private_key(private_key))
with open('public_key.pem', 'wb') as fOut:
    fOut.write(sc.RSAJSONConfig.dumps_public_key(public_key))

# create the config
cfg = sc.RSAJSONConfig()
cfg.set('server', 'username', 'admin')
cfg.set('server', 'password', 'password')
cfg.dump('config.json.rsa.enc', public_key)
# ... and later, load it
with open('private_key.pem', 'rb') as fIn:
    private_key = sc.RSAJSONConfig.loads_private_key(fIn)
cfg = sc.SymmetricJSONConfig.load('config.json.sym.enc', private_key)
```



## TODO
### New Development
  - [x] Base class
  - [x] INI-style subclass
  - [x] JSON-style subclass
  - [x] YAML-style subclass
  - [x] Symmetric encryption mix-in
  - [x] Asymmetric encryption mix-in

### Questions
  - [ ] Pure Python/Cython way to wrap around OpenSSL? Should it use OpenSSL at all?
  - [ ] Should `BaseConfig` enforce sections like a stdlib `ConfigParser` or should it just use them as extended keys?

### Etc
  - [ ] `BaseConfig` ought to constrain value types and handle sequences too
  - [ ] More secure strings (like `secureconfig`?)
  - [ ] Unit tests. Aim for 100% coverage.
  - [ ] Sphinx docs

## Contributing
Make a pull request!
Currently, the style guide is: write code that would make your mom proud.

## License: BSD 3-Clause

Copyright 2017 Andrew Fiorillo

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

