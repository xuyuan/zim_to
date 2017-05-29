'''

extract code blocks from zim-wiki to script file

command for zim custom tool: python path/to/zim_to_script.py -T %T -f %f -D %D

'''

import argparse
from zim.formats import get_parser, StubLinker, DumperClass
import json
import tempfile
import os
import subprocess


class Dumper(DumperClass):
    '''Inherit from html format Dumper class, only overload things that are different'''
    def dump_object(self, tag, attrib, strings=None):
        if 'type' in attrib:
            t = attrib['type']
            if t == 'code':
                block = {'tag': tag, 'attrib': attrib, 'strings': strings}
                return [json.dumps(block)]
        return super(Dumper, self).dump_object(tag, attrib, strings)

    def dump_ignore(self, tag, attrib, strings, _extra=None):
        '''dump nothing'''
        return None

    dump_p = dump_ignore
    dump_h = dump_ignore
    dump_link = dump_ignore
    dump_li = dump_ignore
    dump_ul = dump_ignore
    dump_div = dump_ignore
    dump_img = dump_ignore
    dump_code = dump_ignore
    dump_ol = dump_ignore
    dump_pre = dump_ignore
    dump_strong = dump_ignore


def dump_shenbang(lang):
    if lang in ['sh', 'python']:
        return '#!/usr/bin/env %s\n' % lang


def dump_script(json_data):
    lang = json_data['attrib']['lang']
    shebang = dump_shenbang(lang)
    if shebang:
        lines = [shebang] + json_data['strings']
        return ''.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-T', dest='wiki_text', help='the selected text including wiki formatting')
    parser.add_argument('-f', dest='file', help='the page source as temporary file')
    parser.add_argument('-D', dest='source_dir', help='the document root')
    parser.add_argument('--print', action='store_true', help='print output to stdout instead of to tmpfile and executing')
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
        dumper.dump(tree)
        lines = dumper._text
        lines = [l for l in lines if l and l.startswith('{') and l.endswith('}')]  # remove empty lines
        script_lines = [dump_script(json.loads(l)) for l in lines]
        script_lines = [l for l in script_lines if l]
    except Exception as e:
        print e
        assert False

    for l in script_lines:
        print(l)
        if not vars(args)['print']:
            tf = tempfile.NamedTemporaryFile(prefix='zim_to_script-')
            with tf.file as f:
                f.write(l)
            os.chmod(tf.name, 0777)
            tf.file.close()
            subprocess.check_call(tf.name)



