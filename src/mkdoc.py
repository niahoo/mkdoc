#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright © 2013 Ludovic Demblans

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# The Software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and
# noninfringement. In no event shall the authors or copyright holders
# be liable for any claim, damages or other liability, whether in an
# action of contract, tort or otherwise, arising from, out of or in
# connection with the software or the use or other dealings in the
# Software.


import sys, os, re, datetime, distutils.dir_util, codecs, markdown
from os.path import realpath, isdir, basename, isfile, dirname
from HTMLParser import HTMLParser
from jinja2 import Template
from getopt import getopt
from operator import  attrgetter




## -------------------------------------------------------------------
## Lib
## -------------------------------------------------------------------

class Mkdoc:

    mkdoc_dir = dirname(dirname(realpath(sys.argv[0])))
## -------------------------------------------------------------------
    def __init__(self, src_dir, tpl_dir, out_dir):
        self.src_dir = realpath(src_dir)
        self.tpl_dir = realpath(tpl_dir)
        self.out_dir = realpath(out_dir)
        self._exts = ['.*']
        self.recomp()
        print "Mkdoc root dir : %s" % Mkdoc.mkdoc_dir
## -------------------------------------------------------------------
    def set_exts(self, exts):
        self._exts = exts
        self.recomp()
## -------------------------------------------------------------------
    def recomp(self):
        regexp = ".+\.(%s)$" % '|'.join(self._exts)
        self.p = re.compile(regexp, re.IGNORECASE)
## -------------------------------------------------------------------
    def create_static(self):

        # fichiers md -> pages

        if not isdir(self.src_dir):
            print "not a directory : %s" % self.src_dir
            return

        md_files = self.get_md_files(self.src_dir)

        # pages -> collection

        pages = []

        for mdf in md_files:
            # print "loading file %s" % mdf.filename
            pages.append(mdf.get_page())

        # Écriture des fichiers

        print "Generating pages"

        menu_file = os.path.join(self.tpl_dir,'menu.html')
        if not isfile(menu_file):
            print "    missing menu template (%s), skipping" % menu_file
            menu_tpl = MockTpl()
        else:
             menu_tpl = Tpl(menu_file)

        tpl_file = os.path.join(self.tpl_dir,'default.html')
        print "    Using template %s" % tpl_file
        tpl = Tpl(tpl_file)

        pages = sorted(pages, key=lambda x:x['path'])

        pub_infos = self.pub_infos()
        id = 0
        for page in pages:
            page['id'] = id
            id += 1
            menu_html = menu_tpl.render({'cur_page':page,
                                         'pages':pages,
                                         'out_dir':self.out_dir})

            page_html = tpl.render({'page':page,
                                    'menu':menu_html,
                                    'pub_infos':pub_infos,
                                    'out_dir':self.out_dir})

            # la flemme d'utiliser os.path.join sur windows donc on concatene
            target_path = self.out_dir + os.sep + page['rel_url'].strip('/')
            if not isdir(dirname(target_path)):
                os.makedirs(dirname(target_path))
            tgf = codecs.open(target_path, "w", "utf-8")
            tgf.write(page_html)
            tgf.close()
            print "    CREATE %s" % page['rel_url']
            # print page_html

        print 'done'

        # Copie des static

        print "Copying static files"
        static_dir = os.path.join(self.tpl_dir, 'static')
        static_www = os.path.join(self.out_dir, 'static')
        if not isdir(static_dir):
            print "no dir %s" % static_dir
        else:
            if not isdir(static_www):
                os.makedirs(static_www)
            distutils.dir_util.copy_tree(static_dir, static_www)
            print 'done'


## -------------------------------------------------------------------
    def get_md_files(self, dirname, level=0):
        # print "Fetching md files from %s" % dirname
        md_files = []
        for f in os.listdir(dirname):
            it = os.path.join(dirname,f)
            if False == isdir(it) and self.accepts(it):
                md_files.append(MDFile(it, self.src_dir, level))
            elif isdir(it):
                md_files.extend(self.get_md_files(it, level+1))
        if level == 0: print 'All sources collected'
        return md_files
## -------------------------------------------------------------------
    def accepts(self, filename):
        m = self.p.match(filename)
        if m:
            return True
        else:
            print "SKIP file %s" % basename(filename)
            return False
        pass

    def pub_infos(self):
        return {
            'date': datetime.date.today().isoformat()
        }

class MDFile:

    def __init__(self,filename,root,level):
        ## level == deepness
        self.filename = filename
        self.html = ''
        self.root = root
        self.level = level

    def get_page(self):
        html = unicode(self.to_html().strip())
        parser = MkParser()
        parser.feed(html)
        title = unicode(parser.get_page_title().strip())
        rel_url = self.switch_ext(self.filename.replace(self.root, '').replace('\\', '/'))
        path = dirname(self.filename.replace(self.root, ''))
        return {
            'content': html,
            'title':   title,
            'path':   path.replace('/',' > ').replace('\\',' > ').strip(' > '),
            'rel_url': rel_url.strip('/'),
            'to_root': self.to_root()
        }


    def to_html(self):
        input_file = codecs.open(self.filename, mode="r", encoding="utf-8")
        text = input_file.read()
        html = markdown.markdown(text)
        return html

    def switch_ext(self, filename):
        """remplace l'extension d'un nom de fichier par .html"""
        regexp = "(.+)\.([^\.]+)$"
        p = re.sub(regexp, r'\1.html',filename)
        return p

    def to_root(self):
        return self.level and '../' * self.level or './'

class MkParser(HTMLParser):

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self)
        self.recording = False
        self.fragments = []

    def handle_starttag(self, tag, attrs):
        ltag = tag.lower()
        if 'h1' == ltag:
            self.recording = True
        elif self.recording:
            self.fragments.append('<%s>' % ltag)

    def handle_endtag(self, tag):
        ltag = tag.lower()
        if 'h1' == ltag:
            self.recording = False
        elif self.recording:
            self.fragments.append('</%s>' % ltag)

    def handle_data(self, data):
        if self.recording:
            self.fragments.append(data)

    def get_page_title(self):
        page_title = ''.join(self.fragments)
        if '' == page_title:
            return 'No Title'
        else:
            return page_title


# instantiate the parser and fed it some HTML


class Tpl:

    def __init__(self, tpl_file):
        if isfile(tpl_file):
            self.tpl_file = tpl_file
        else:
            raise Exception('template file not found : %s' % tpl_file)
        self.tpl = Template(self.read_file())

    def read_file(self):
        fp = codecs.open(self.tpl_file, "r", "utf-8")
        content = fp.read()
        fp.close()
        return unicode(content)

    def render(self, props):
        return self.tpl.render(props)

class MockTpl:

    def __init__(self,*args):
        pass

    def render(self, *args):
        return ''


## -------------------------------------------------------------------
## Start Script
## -------------------------------------------------------------------

if __name__ == '__main__':

    ## Get Opts

    cur_dir = os.path.dirname(os.getcwd())

    opts, args = getopt(sys.argv[1:], 't:')
    def opt_val(ak,default=None):
        for k, v in opts:
            if k == ak:
                return v
        return default


    def get_src_dir():
        return 'md-src'
    def get_tpl_dir():
        tpl_dir = opt_val('-t', os.path.join(Mkdoc.mkdoc_dir, 'default_tpl'))
        return tpl_dir
    def get_out_dir():
        return "www"
    def get_exts():
        return 'm,md,markdown'.split(',')

    # Launch

    mkdoc = Mkdoc(get_src_dir(),get_tpl_dir(),get_out_dir())
    mkdoc.set_exts(get_exts())
    mkdoc.create_static()
