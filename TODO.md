TODO
---

# New Development
  - [x] Base class
  - [ ] INI-style subclass
  - [ ] JSON-style subclass
  - [ ] YAML-style subclass
  - [ ] Symmetric encryption mix-in
  - [ ] Asymmetric encryption mix-in
  
# Questions
  - [ ] Pure Python/Cython way to wrap around OpenSSL? Should it use OpenSSL at all?
  - [ ] Should `BaseConfig` enforce sections like a stdlib `ConfigParser` or should it just use them as extended keys?
  
# Revisions
  - [ ] `BaseConfig` ought to constrain value types and handle sequences too
