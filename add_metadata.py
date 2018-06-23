from optparse import OptionParser

import pandas as pd

import file_handling as fh


def main():
    usage = "%prog all.jsonlist articles.csv metadata.csv field_name outfile.jsonlist"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    infile = args[0]
    articles_csv = args[1]
    metadata_csv = args[2]
    field_name = args[3]
    outfile = args[4]

    lines = fh.read_jsonlist(infile)
    articles_df = pd.read_csv(articles_csv, header=0, index_col=0)
    metadata_df = pd.read_csv(metadata_csv, header=0, index_col=0)

    outlines = []

    for line in lines:
        doc_id = int(line['id'])
        msa_id = articles_df.loc[doc_id, 'df_index']
        line[field_name] = metadata_df.loc[msa_id, field_name]
        outlines.append(line)

    fh.write_jsonlist(outlines, outfile, sort_keys=False)


if __name__ == '__main__':
    main()
