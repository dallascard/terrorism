from optparse import OptionParser

import numpy as np
import pandas as pd

import file_handling as fh


def main():
    usage = "%prog articles.jsonlist metadata.csv outputfile.jsonlist"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    infile = args[0]
    meta_file = args[1]
    outfile = args[2]

    articles = fh.read_jsonlist(infile)
    df = pd.read_csv(meta_file, header=0, index_col=0)
    df.index = [str(i) for i in df.index]
    print(df.head())

    n_not_found = 0
    for line in articles:
        caseid = str(line['caseid'])
        name = line['name']
        if caseid in df.index:
            row = df.loc[caseid]
            df_name = row['Shooter Name']
            white = row['EKG white']
            line['white'] = str(white)
        else:
            print("CaseID {:s} not found in csv".format(caseid))

    fh.write_jsonlist(articles, outfile)




if __name__ == '__main__':
    main()
