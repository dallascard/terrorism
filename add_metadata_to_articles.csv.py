import os
from optparse import OptionParser

import pandas as pd

import file_handling as fh


def main():
    usage = "%prog articles.jsonlist metadata.csv output_dir"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    infile = args[0]
    meta_file = args[1]
    output_dir = args[2]

    articles = fh.read_jsonlist(infile)
    df = pd.read_csv(meta_file, header=0, index_col=0)
    df.index = [str(i) for i in df.index]
    print(df.head())

    victim_counts = []
    fatality_counts = []
    white = []
    black = []

    outlines = []
    for line in articles:
        caseid = str(line['caseid'])
        name = line['name']
        if caseid == '156' or caseid == '168':
            # differentiate on name for two ids that have duplicates
            row = df[(df['CaseID'] == caseid) & (df['name'] == name)]
        else:
            # otherwise, just use the id
            row = df[df['CaseID'] == caseid]
        df_name = row['Shooter Name']
        line['state'] = row['state']
        line['white'] = row['ekg_white']
        white.append(row['ekg_white'])
        black.append(row['ekg_black'])
        line['black'] = row['ekg_white']
        line['mental'] = row['mental']
        line['fate'] = row['fate_at_scene']
        line['fatalities'] = row['ekg_white']
        line['victims'] = row['ekg_white']
        victim_counts.append(row['victims'])
        fatality_counts.append(row['fatalities'])
        outlines.append(line)

    fh.write_jsonlist(outlines, os.path.join(output_dir, 'articles.metadata.jsonlist'))

    victims_df = pd.DataFrame(victim_counts, index=articles.index, columns=['victims'])
    victims_df.to_csv(os.path.join(output_dir, 'victims.csv'))

    fatalities_df = pd.DataFrame(fatality_counts, index=articles.index, columns=['fatalities'])
    fatalities_df.to_csv(os.path.join(output_dir, 'fatalities.csv'))

    white_df = pd.DataFrame(white, index=articles.index, columns=['white'])
    white_df.to_csv(os.path.join(output_dir, 'white.csv'))

    black_df = pd.DataFrame(black, index=articles.index, columns=['black'])
    black_df.to_csv(os.path.join(output_dir, 'black.csv'))


if __name__ == '__main__':
    main()
