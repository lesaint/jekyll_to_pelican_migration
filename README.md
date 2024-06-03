Migrate from Jekyll to Pelican
==============================

Tools to help migrate from static website generator Jekyll (Ruby-based) to [Pelican](https://docs.getpelican.com/en/latest/index.html) (Python-based).

Migrate .md files
-----------------

`migrate_md.py` alters the content of `.md` files to make them render correctly with Pelican.

### Usage

```shell
./migrate_md.py *.md
```

### How it works

* makes copy of `.md` files matching the provided pattern as `.md.backup` files
* process `.md` files lines by line and apply `LineProcessor` instances provided by function `_create_processors()`
* replace the current line by the second value of the tuple returned by the first `LineProcessor` having `True` as the first value


License
-------

Licensed under the [MIT License](https://opensource.org/license/mit).

Copyright 2024 Sébastien Lesaint
