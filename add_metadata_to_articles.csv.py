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
    mental = []

    outlines = []
    for line_i, line in enumerate(articles):
        if line_i % 1000 == 0:
            print(line_i)
        caseid = int(line['caseid'])
        name = line['name']
        if caseid == 156 or caseid == 168:
            # differentiate on name for two ids that have duplicates
            row = df[(df['CaseID'] == caseid) & (df['name'] == name)]
        else:
            # otherwise, just use the id
            row = df[df['CaseID'] == caseid]
        line['state'] = str(row['state'].values[0])
        line['white'] = int(row['ekg_white'])
        line['black'] = int(row['ekg_white'])
        white.append(int(row['ekg_white']))
        black.append(int(row['ekg_black']))
        line['mental'] = int(row['mental'])
        mental.append(int([row['mental']]))
        line['fate'] = str(row['fate_at_scene'].values[0])
        line['fatalities'] = int(row['ekg_white'])
        line['victims'] = int(row['ekg_white'])
        victim_counts.append(int(row['victims']))
        fatality_counts.append(int(row['fatalities']))
        outlines.append(line)

    fh.write_jsonlist(outlines, os.path.join(output_dir, 'articles.metadata.jsonlist'), sort_keys=False)

    ids = list(range(len(victim_counts)))
    victims_df = pd.DataFrame(victim_counts, index=ids, columns=['victims'])
    victims_df.to_csv(os.path.join(output_dir, 'train.victims.csv'))

    fatalities_df = pd.DataFrame(fatality_counts, index=ids, columns=['fatalities'])
    fatalities_df.to_csv(os.path.join(output_dir, 'train.fatalities.csv'))

    white_df = pd.DataFrame(white, index=ids, columns=['white'])
    white_df.to_csv(os.path.join(output_dir, 'train.white.csv'))

    black_df = pd.DataFrame(black, index=ids, columns=['black'])
    black_df.to_csv(os.path.join(output_dir, 'train.black.csv'))

    mental_df = pd.DataFrame(mental, index=ids, columns=['black'])
    mental_df.to_csv(os.path.join(output_dir, 'train.mental.csv'))


if __name__ == '__main__':
    main()
