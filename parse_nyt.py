import os
import json
from glob import glob
from optparse import OptionParser

import tqdm
import spacy

# Use Spacy to tokenize text
# This can handle one or more fields in the input (each of which will become an output field)
# It converts the text to a list of lists
# By default this is a list of sentences, each of which is a list of tokens


def main():
    usage = "%prog jsonlist_dir outdir"
    parser = OptionParser(usage=usage)
    parser.add_option('--infield', type=str, default='text',
                      help='Name of field with text (comma-separated): default=%default')
    parser.add_option('--outfield', type=str, default='tokens',
                      help='Name of corresponding output fields (comma-separated): default=%default')
    #parser.add_option('--total', type=int, default=None,
    #                  help='Manually provide the number of lines to tqdm: default=%default')
    parser.add_option('--max-lines', type=int, default=None,
                      help='Only process this many lines: default=%default')
    parser.add_option('--convert-parens', action="store_true", default=False,
                      help='Convert "-lrb-" to "(", etc. : default=%default')
    parser.add_option('--quiet', action="store_true", default=False,
                      help='Suppress output: default=%default')
    parser.add_option('--high-memory', action="store_true", default=False,
                      help='Load all the data at once: default=%default')

    (options, args) = parser.parse_args()

    indir = args[0]
    outdir = args[1]

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    files = sorted(glob(os.path.join(indir, '*.jsonlist')))

    for infile in files:
        print(infile)
        basename = os.path.basename(infile)
        outfile = os.path.join(outdir, basename)
        infield = options.infield
        outfield = options.outfield
        total = None
        max_lines = options.max_lines
        convert_parens = options.convert_parens
        quiet = options.quiet
        high_memory = options.high_memory

        tokenize(infile, outfile, infield, outfield, total, max_lines, quiet, high_memory, convert_parens)


def tokenize(infile, outfile, infield, outfield, total, max_lines, quiet, high_memory, convert_parens=False):

    if ',' in infield:
        infields = infield.split(',')
        outfields = outfield.split(',')
    else:
        infields = [infield]
        outfields = [outfield]
    try:
        assert len(infields) == len(outfields)
    except Exception as e:
        print("Number of infield must match number of outfields (comma-separted)")
        raise e

    if not quiet:
        print("Loading spacy")
    nlp = spacy.load("en_core_web_sm")

    if high_memory:
        if not quiet:
            print("Reading data")
        lines = []
        with open(infile) as f:
            for line in f:
                lines.append(json.loads(line))
        if max_lines is None:
            max_lines = len(lines)

        total = max_lines

        if quiet:
            enumerator = enumerate(lines[:max_lines])
        else:
            enumerator = tqdm.tqdm(enumerate(lines[:max_lines]), total=total)

        if not quiet:
            print("Processing data")

        count = 0
        for i, line in enumerator:
            for f_i, field in enumerate(infields):
                text = nlp(line[field])
                count += 1
                tokens = []
                for sent in text.sents:
                    sent_tokens = [token.text for token in sent]
                    if convert_parens:
                        sent_tokens = ['(' if t.lower() == '-lrb-' else t for t in sent_tokens]
                        sent_tokens = [')' if t.lower() == '-rrb-' else t for t in sent_tokens]
                        sent_tokens = ['[' if t.lower() == '-lsb-' else t for t in sent_tokens]
                        sent_tokens = [']' if t.lower() == '-rsb-' else t for t in sent_tokens]
                    tokens.append(sent_tokens)
                line[outfields[f_i]] = tokens

        if not quiet:
            print("Processed {:d} lines".format(count))

        if not quiet:
            print("Saving data")

        with open(outfile, 'w') as f:
            for line in lines:
                f.write(json.dumps(line) + '\n')

    else:
        if not quiet:
            print("Processing documents")

        count = 0
        with open(infile) as f:
            with open(outfile, 'w') as w:
                if quiet:
                    enumerator = enumerate(f)
                else:
                    enumerator = tqdm.tqdm(enumerate(f), total=total)

                for i, line in enumerator:
                    line = json.loads(line)
                    for f_i, field in enumerate(infields):
                        text = nlp(line[field])
                        count += 1
                        tokens = []
                        for sent in text.sents:
                            sent_tokens = [token.text for token in sent]
                            if convert_parens:
                                sent_tokens = ['(' if t.lower() == '-lrb-' else t for t in sent_tokens]
                                sent_tokens = [')' if t.lower() == '-rrb-' else t for t in sent_tokens]
                                sent_tokens = ['[' if t.lower() == '-lsb-' else t for t in sent_tokens]
                                sent_tokens = [']' if t.lower() == '-rsb-' else t for t in sent_tokens]
                            tokens.append(sent_tokens)
                        line[outfields[f_i]] = tokens
                        if max_lines is not None and count > max_lines:
                            break
                    w.write(json.dumps(line) + '\n')

            if not quiet:
                print("Processed {:d} lines".format(count))


if __name__ == '__main__':
    main()
