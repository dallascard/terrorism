from optparse import OptionParser

import numpy as np

import file_handling as fh


def main():
    usage = "%prog sgns.words sgns.words.vocab"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    vecs_file = args[0]
    vocab_file = args[1]


if __name__ == '__main__':
    main()
