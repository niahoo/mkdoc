mkdoc
=====

A simple static wiki generator. Uses markdown files

Installation
------------

### Requirements

- Python 2.6 +
- Jinja2
- Python Markdown ([PyPI](http://pypi.python.org/pypi/Markdown))

To install Jinja2, please run one of the following commands as root :

    easy_install Jinja2
    pip install Jinja2

To install Markdown, please run one of the following commands as root :

    easy_install markdown
    pip install markdown

### Clone & Install

Now clone this repository

    git clone https://github.com/niahoo/mkdoc.git
    cd mkdoc

Then add in your path a symlink to mkdoc.py

    ln -s src/mkdoc.py /home/$USER/bin/mkdoc

Using
-----

mkdoc command must now be in your path.

Let say you have your makrdown formatted files in /home/wiki/md-src,
as we actually support only this name for the sources directory.

Go into /home/wiki, launch mkdoc:

    cd /home/wiki
    mkdoc

Now you should have a directory containing the generated HTML files:
/home/wiki/www


Troubleshooting
---------------

As `realpath` doesn't seem to work on MinGW, you must either provide
the default template path with the -t option or use mkdoc.py instead
of a symlink.

    mkdoc -t /path/to/mkdoc/default_tpl

    /path/to/mkdoc/src/mkdoc.py

You can also add /path/to/mkdoc/src to your PATH.
