#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''publish zim note to wordpress as post
'''
import os
import argparse
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
from zim_to_wordpress import Dumper
from zim.formats import get_parser, BaseLinker, TAG
from zim.parsing import link_type


class WordPressPostDumper(Dumper):
    def __init__(self, linker):
        super(WordPressPostDumper, self).__init__(linker=linker)
        self.wp_title = None
        self.wp_tags = []
        self.wp_p_count = 0
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
        if strings[0].startswith('Content-Type: text/x-zim-wiki') or strings == [u' ', u'<br>\n']:
            strings = []
        else:
            self.wp_p_count += 1

        if self.wp_p_count == 1:
            # insert read more tag after first p
            strings.append('<!--more-->')

        return strings


class WordPressLinker(BaseLinker):
    def __init__(self, source_dir, wordpress_client):
        self.source_dir = source_dir
        self.wordpress_client = wordpress_client

    def link(self, link):
        type = link_type(link)
        if type == 'mailto' and not link.startswith('mailto:'):
            return 'mailto:' + link
        elif type == 'interwiki':
            return 'interwiki:' + link
        else:
            return link

    def img(self, src):
        filename = self.resolve_source_file(src)
        ext = os.path.splitext(filename)[-1]
        data = {'name': os.path.basename(filename),
                'type': 'image/' + ext[1:]}
        with open(filename, 'rb') as img:
            data['bits'] = xmlrpc_client.Binary(img.read())
        print 'upload image', filename
        response = self.wordpress_client.call(UploadFile(data))
        return response['url']

    def resolve_source_file(self, link):
        if os.path.isabs(link):
            return link

        return os.path.normpath(os.path.join(self.source_dir, link))

    def resource(self, path):
        return path

    def page_object(self, path):
        return path.name

    def file_object(self, file):
        return file.name

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-w', dest='wordpress', help='url of wordpress site')
    parser.add_argument('-u', dest='username', help='username of wordpress site')
    parser.add_argument('-p', dest='password', help='password of wordpress site')
    parser.add_argument('-f', dest='file', help='the page source as temporary file')
    #parser.add_argument('-D', dest='source_dir', help='the document root')

    args = parser.parse_args()

    zim_parser = get_parser('wiki')
    wiki_text = open(args.file).read()
    tree = zim_parser.parse(wiki_text)

    wp = Client('http://%s/xmlrpc.php' % args.wordpress, args.username, args.password)

    source_dir = os.path.splitext(args.file)[0]
    linker = WordPressLinker(source_dir, wp)
    dumper = WordPressPostDumper(linker=linker)
    lines = dumper.dump(tree)
    wordpress_text = ''.join(lines).encode('utf-8')
    #print wordpress_text

    assert dumper.wp_title is not None

    post = WordPressPost()
    post.title = dumper.wp_title
    post.content = wordpress_text
    post.comment_status = 'open'  # allow comments
    post.terms_names = {'post_tag': dumper.wp_tags,
                        'category': []
                        }
    wp.call(NewPost(post))

