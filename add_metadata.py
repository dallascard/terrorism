from optparse import OptionParser

import pandas as pd

import file_handling as fh


# Note: this assumes that the "id" field in all.jsonlist is the index into articles.csv
# This must be edited if it refers to the index of metadata.csv

def main():
    usage = "%prog all.jsonlist articles.csv metadata.csv outfile.jsonlist"
    parser = OptionParser(usage=usage)
    parser.add_option('--fields', dest='field_names', default='metadata',
                      help='metadata fields to add (comma-separated): default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    infile = args[0]
    articles_csv = args[1]
    metadata_csv = args[2]
    outfile = args[3]

    field_names = options.field_names.split(',')

    lines = fh.read_jsonlist(infile)
    articles_df = pd.read_csv(articles_csv, header=0, index_col=0)
    metadata_df = pd.read_csv(metadata_csv, header=0, index_col=0)

    for name in field_names:
        if name not in metadata_df.columns:
            raise ValueError("Field {:s} not found in metadata file".format(name))

    outlines = []

    for line in lines:
        doc_id = int(line['id'])
        msa_id = articles_df.loc[doc_id, 'df_index']
        for field in field_names:
            if field in line:
                raise ValueError("Field {:s} already in json object!".format(field))
            line[field] = metadata_df.loc[msa_id, field]
        outlines.append(line)

    fh.write_jsonlist(outlines, outfile, sort_keys=False)


if __name__ == '__main__':
    main()
