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

### Revisions
  - [ ] `BaseConfig` ought to constrain value types and handle sequences too

## Contributing
Make a pull request!
Currently, the style guide is: write code that would make your mom proud.

## License: BSD 3-Clause

Copyright 2017 Andrew Fiorillo

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

