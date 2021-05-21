import os
import re
import sys
import glob
import codecs
import tarfile
from optparse import OptionParser
import xml.etree.ElementTree as et

import file_handling as fh


def main():
    usage = "%prog data_dir output_dir output_prefix"
    parser = OptionParser(usage=usage)
    #parser.add_option('--year', dest='year', default=1987,
    #                  help='Year: default=%default')
    parser.add_option('--gzip', action="store_true", dest="gzip", default=False,
                      help='gzip output: default=%default')
    #parser.add_option('--word2vec', action="store_true", dest="word2vec", default=False,
    #                  help='Output data processed for word2vec: default=%default')
    parser.add_option('--lower', action="store_true", dest="lower", default=False,
                      help='Lower-case words: default=%default')
    parser.add_option('--replace_digits', action="store_true", dest="replace_digits", default=False,
                      help='Replace digits with #: default=%default')
    parser.add_option('--fix_punct', action="store_true", dest="fix_punct", default=False,
                      help='Fix some punctuation: default=%default')
    #parser.add_option('--timestamp', dest='timestamp', default=None,
    #                  help='List of words to timestamp (comma-separated): default=%default')

    (options, args) = parser.parse_args()
    base_dir = args[0]
    outdir = args[1]
    output_prefix = args[2]

    years = [str(year) for year in range(1987, 2008)]
    do_gzip = options.gzip
    word2vec = False
    lower = options.lower
    replace_digits = options.replace_digits
    fix_punct = options.fix_punct
    #words_to_timestamp = options.timestamp
    #if words_to_timestamp is not None:
    #    words_to_timestamp = words_to_timestamp.split(',')

    outfile = None
    if word2vec:
        outfile = os.path.join(outdir, output_prefix + '.txt')
        if os.path.exists(outfile):
            sys.exit("Error: output file already exists.")

        with codecs.open(outfile, 'w') as f:
            f.write('')

    n_words = 0
    outlines = []
    for year in years:
        data_dir = os.path.join(base_dir, year)
        files = glob.glob(os.path.join(data_dir, '*.tgz'))
        files.sort()
        for tgz in files:
            print(tgz)
            tar = tarfile.open(tgz, "r:gz")
            for member in tar.getmembers():
                #print(tgz, member.name)
                f = tar.extractfile(member)
                if f is not None:
                    name = member.name
                    parts = name.split('/')
                    month = int(parts[0])
                    day = int(parts[1])
                    #print(tgz, member, f)
                    xml_string = f.read()
                    root = et.fromstring(xml_string)
                    headlines = []
                    paragraphs = []
                    for body in root.findall('body'):
                        #print(body)
                        for head in body.findall('body.head'):
                            #print(content)
                            for headline in head.findall('hedline'):
                                for child in headline:
                                    if child.text is not None:
                                        if 'class' not in child.attrib:
                                            headlines.append(child.text)

                        for content in body.findall('body.content'):
                            #print(content)
                            for block in content.findall('block'):
                                #print(block)
                                if block.attrib['class'] == 'full_text':
                                    for child in block:
                                        if child.text is not None:
                                            if child.text[:5] != 'LEAD:':
                                                paragraphs.append(child.text)
                    if len(paragraphs) > 0:
                        try:
                            if word2vec:
                                if len(headlines) > 0:
                                    for headline in headlines:
                                        lines = headline.split('\n')
                                        for line in lines:
                                            n_words += len(line.split())
                                            outlines.append(line)
                                for paragraph in paragraphs:
                                    lines = paragraph.split('\n')
                                    for line in lines:
                                        n_words += len(line.split())
                                        outlines.append(line)
                            else:
                                headline = '\n\n'.join(headlines)
                                body = '\n\n'.join(paragraphs)

                                headline = fix_line(headline, lower, replace_digits, fix_punct)
                                body = fix_line(body, lower, replace_digits, fix_punct)

                                outlines.append({'body': body, 'headline': headline, 'year': year, 'month': month, 'day': day})
                        except:
                            print(tgz, member.name)
                            print(headlines)
                            print(paragraphs)
                            print(year)
                            print(month)
                            print(day)
                            sys.exit()
        if word2vec:
            output_line = ''
            for line in outlines:
                output_line += line + '\n'
            output_line = fix_line(output_line, lower, replace_digits, fix_punct)
            #if words_to_timestamp is not None:
            #    for word in words_to_timestamp:
            #        output_line = re.sub(word, word + '_' + str(year), output_line)
            with codecs.open(outfile, 'a') as f:
                f.write(output_line)
        else:
            outfile = os.path.join(outdir, output_prefix + '_' + year + '.jsonlist')
            if do_gzip:
                outfile += '.gz'
            fh.write_jsonlist(outlines, outfile, sort_keys=False, do_gzip=do_gzip)

    print("Total tokens = %d" % n_words)


def fix_line(line, lower=False, replace_digits=False, fix_punct=False):
    if lower:
        line = line.lower()
    if replace_digits:
        line = re.sub(r'\d', '#', line)
    if fix_punct:
        # drop stars
        line = re.sub(r'\*', ' ', line)
        # split off opening quotes
        line = re.sub(r'^\'\'', '\'\' ', line)
        line = re.sub(r'^``', '`` ', line)
        line = re.sub(r'^"', '" ', line)
        line = re.sub(r'\s\'\'', ' \'\' ', line)
        line = re.sub(r'\s``', ' `` ', line)
        line = re.sub(r'\s"', ' " ', line)
    return line


if __name__ == '__main__':
    main()
