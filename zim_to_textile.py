'''
'''

import argparse
import pyperclip
from zim.formats import get_parser
from zim.formats.plain import Dumper as TextDumper
from zim.parsing import url_re


class Dumper(TextDumper):
    '''Inherit from wiki format Dumper class, only overload things that are different'''

    def dump_link(self, tag, attrib, strings=None):
        href = attrib['href']
        text = u''.join(strings) or href
        if href == text and url_re.match(href):
            return href
        else:
            return ['"%s":%s' % (text, href)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-T', dest='wiki_text', help='the selected text including wiki formatting')
    args = parser.parse_args()

    zim_parser = get_parser('wiki')
    tree = zim_parser.parse(args.wiki_text)
    dumper = Dumper()
    lines = dumper.dump(tree)
    textile_text = ''.join(lines).encode('utf-8')
    pyperclip.copy(textile_text)
