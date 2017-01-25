'''

command for zim custom tool: python path/to/zim_to_wordpress.py -T %T -f %f -D %D

'''

import argparse
import pyperclip
from zim.formats import get_parser, StubLinker
from zim.formats.html import Dumper as TextDumper

# Not all the languages are supported in wordpress plugin
# Or the names are different
# see http://alexgorbatchev.com/SyntaxHighlighter/manual/brushes/
LANG_MAP = {'sh': 'bash',
            'ini': 'text'}


class Dumper(TextDumper):
    '''Inherit from html format Dumper class, only overload things that are different'''
    def dump_object(self, tag, attrib, strings=None):
        if 'type' in attrib:
            t = attrib['type']
            if t == 'code':
                c = attrib.get('lang', "")
                c = LANG_MAP.get(c, c)
                return ['[%s]\n' % c] + strings + ['[/%s]\n' % c]
        return super(Dumper, self).dump_object(tag, attrib, strings)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-T', dest='wiki_text', help='the selected text including wiki formatting')
    parser.add_argument('-f', dest='file', help='the page source as temporary file')
    parser.add_argument('-D', dest='source_dir', help='the document root')
    args = parser.parse_args()

    zim_parser = get_parser('wiki')
    if args.wiki_text:
        wiki_text = args.wiki_text
    else:
        wiki_text = open(args.file).read()
    tree = zim_parser.parse(wiki_text)
    try:
        linker = StubLinker(source_dir=args.source_dir)
        dumper = Dumper(linker=linker)
        lines = dumper.dump(tree)
        wordpress_text = ''.join(lines).encode('utf-8')
        pyperclip.copy(wordpress_text)
    except Exception as e:
        pyperclip.copy(e.message)
