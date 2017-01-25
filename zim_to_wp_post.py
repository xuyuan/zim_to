#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''publish zim note to wordpress as post
'''
import argparse
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from zim_to_wordpress import Dumper
from zim.formats import get_parser, StubLinker, TAG


class WordPressPostDumper(Dumper):
    def __init__(self, linker):
        super(WordPressPostDumper, self).__init__(linker=linker)
        self.wp_title = None
        self.wp_tags = []
        del self.TAGS[TAG]  # --> dump_tag

    def dump_h(self, tag, attrib, strings):
        # get title for wordpress post
        if self.wp_title is None and attrib['level'] == 1:
            self.wp_title = strings[0]
            return []
        return super(WordPressPostDumper, self).dump_h(tag, attrib, strings)

    def dump_tag(self, tag, attrib, strings):
        self.wp_tags.append(attrib['name'])

    def dump_p(self, tag, attrib, strings):
        #print tag, attrib, strings
        if strings[0].startswith('Content-Type: text/x-zim-wiki'):
            strings = []
        return strings
        #assert False

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
    wordpress_text = ''.join(lines).encode('utf-8')
    print wordpress_text

    assert dumper.wp_title is not None

    wp = Client('http://%s/xmlrpc.php' % args.wordpress, args.username, args.password)

    post = WordPressPost()
    post.title = dumper.wp_title
    post.content = wordpress_text
    post.terms_names = {'post_tag': dumper.wp_tags,
                        'category': []
                        }
    #wp.call(NewPost(post))


    
