"""Small, dependency-free tools for shipping changes to a server you can verify.

- manifest:      md5 manifest of a directory tree
- parity:        are two copies byte-identical, file by file?
- deploylist:    which files does a change touch, measured against production?
- anchored_edit: apply a reviewed edit plan exactly once, all or nothing
"""
__version__ = "0.1.0"
