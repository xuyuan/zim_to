'''

* textile format: http://www.redmine.org/projects/redmine/wiki/RedmineTextFormattingTextile#External-links
'''

import argparse
import pyperclip
from zim.formats import get_parser
from zim.formats import UNCHECKED_BOX, XCHECKED_BOX, CHECKED_BOX, BULLET, BULLETLIST, NUMBEREDLIST
from zim.formats import EMPHASIS, STRONG, MARK, STRIKE, VERBATIM, TAG, SUBSCRIPT, SUPERSCRIPT
from zim.formats.plain import Dumper as TextDumper
from zim.parsing import url_re


class Dumper(TextDumper):
    '''Inherit from wiki format Dumper class, only overload things that are different'''
    BULLETS = {UNCHECKED_BOX:	u'\u2610',
               XCHECKED_BOX:	u'\u2612',
               CHECKED_BOX:	u'\u2611',
               BULLET:          u'*',
               }

    TAGS = {EMPHASIS:    ('_', '_'),
            STRONG:      ('*', '*'),
            MARK:        ('+', '+'),
            STRIKE:      ('-', '-'),
            VERBATIM:    ("<pre>", "</pre>"),
            TAG:         ('@', '@'),
            SUBSCRIPT:   ('~', '~'),
            SUPERSCRIPT: ('^', '^'),
            }

    def dump_link(self, tag, attrib, strings=None):
        href = attrib['href']
        text = u''.join(strings) or href
        if href == text and url_re.match(href):
            return href
        else:
            return ['"%s":%s' % (text, href)]

    def dump_h(self, tag, attrib, strings):
        level = int(attrib['level'])
        heading = u''.join(strings)
        return ['h%d. ' % level, heading, '\n']

    def dump_ul(self, tag, attrib, strings):
        return strings

    def dump_ol(self, tag, attrib, strings):
        return strings

    def dump_li(self, tag, attrib, strings):
        level = self._count_list_level()
        if self.context[-1].tag == NUMBEREDLIST:
            bullet = u'#' * level
        else:
            bullet = self.BULLETS[BULLET] * level
            if 'bullet' in attrib and attrib['bullet'] != BULLET and attrib['bullet'] in self.BULLETS:
                bullet += (' ' + self.BULLETS[attrib['bullet']])

        return (bullet, ' ') + tuple(strings) + ('\n',)

    def _count_list_level(self):
        level = 0
        for i in range(-1, -len(self.context) - 1, -1):
            if self.context[i].tag in (BULLETLIST, NUMBEREDLIST):
                level += 1
            else:
                break
        return level

    def dump_img(self, tag, attrib, strings=None):
        src = attrib['src']
        if src.startswith('./'):
            src = src[2:]
        text = attrib.get('alt', '')
        if text:
            return ['!%s(%s)!\n' % (src, text)]
        else:
            return ['!%s!\n' % src]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-T', dest='wiki_text', help='the selected text including wiki formatting')
    args = parser.parse_args()

    zim_parser = get_parser('wiki')
    tree = zim_parser.parse(args.wiki_text)
    try:
        dumper = Dumper()
        lines = dumper.dump(tree)
        textile_text = ''.join(lines).encode('utf-8')
        pyperclip.copy(textile_text)
    except Exception as e:
        pyperclip.copy(e.message)
