#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''publish zim note to wordpress as post
'''
import argparse
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from zim_to_wordpress import Dumper, get_parser, StubLinker


class WordPressPostDumper(Dumper):
    def __init__(self, linker):
        super(WordPressPostDumper, self).__init__(linker=linker)
        self.wp_title = None

    def dump_h(self, tag, attrib, strings):
        # get title for wordpress post
        if self.wp_title is None and attrib['level'] == 1:
            self.wp_title = strings[0]
        super(WordPressPostDumper, self).dump_h(tag, attrib, strings)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-w', dest='wordpress', help='url of wordpress site')
    parser.add_argument('-u', dest='username', help='username of wordpress site')
    parser.add_argument('-p', dest='password', help='password of wordpress site')
    parser.add_argument('-f', dest='file', help='the page source as temporary file')
    parser.add_argument('-D', dest='source_dir', help='the document root')

    args = parser.parse_args()

    zim_parser = get_parser('wiki')
    wiki_text = open(args.file).read()
    tree = zim_parser.parse(wiki_text)
    linker = StubLinker(source_dir=args.source_dir)
    dumper = WordPressPostDumper(linker=linker)
    lines = dumper.dump(tree)
    lines = lines[6:]  # skip zim-wiki header
    wordpress_text = ''.join(lines).encode('utf-8')

    assert dumper.wp_title is not None

    wp = Client('http://%s/xmlrpc.php' % args.wordpress, args.username, args.password)

    post = WordPressPost()
    post.title = dumper.wp_title
    post.content = wordpress_text
    post.terms_names = {'post_tag': ['test'],
                        'category': []
                        }
    #wp.call(NewPost(post))


    
