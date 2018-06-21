import re
from optparse import OptionParser

import numpy as np

import file_handling as fh

# take the output of tag_each_shooter_in_parse and output plain text for word2vec

def main():
    usage = "%prog tagged.jsonlist output_file.txt"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    infile = args[0]
    outfile = args[1]

    outlines = []
    lines = fh.read_jsonlist(infile)
    n_lines = len(lines)
    order = np.arange(n_lines)
    np.random.shuffle(order)
    print(order[:10])

    for i in order:
        line = lines[i]
        text = line['text_tagged']
        text = re.sub('_', '-', text)
        text = re.sub('\d', '#', text)
        text = text.lower()
        outlines.append(text)

    fh.write_list_to_text(outlines, outfile)


if __name__ == '__main__':
    main()
