import os
import re
import glob
from optparse import OptionParser

import pandas as pd

import file_handling as fh


def main():
    usage = "%prog msa_db.csv articles.csv parsed_dir output_file.csv"
    parser = OptionParser(usage=usage)
    parser.add_option('--prefix', dest='parse_prefix', default='all',
                      help='Prefix of parsed files: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    msa_csv = args[0]
    articles_csv = args[1]
    parsed_dir = args[2]
    outfile = args[3]
    parse_prefix = options.parse_prefix

    if os.path.exists(outfile):
        raise FileExistsError("outfile already exists!")

    msa_df = pd.read_csv(msa_csv, header=0)
    print(msa_df.shape)

    df = pd.read_csv(articles_csv, header=0, index_col=0)
    n_rows, n_columns = df.shape
    print(df.shape)

    files = glob.glob(os.path.join(parsed_dir, '*.json'))
    n_files = len(files)

    assert n_files == n_rows

    msa_df['n_total_articles'] = 0
    msa_df['n_valid_articles'] = 0
    msa_df['n_terrorism_mentions'] = 0
    msa_df['n_unnegated_terrorism_mentions'] = 0
    msa_df['n_mental_mentions'] = 0

    for i in msa_df.index:
        date = pd.to_datetime(msa_df.loc[i, 'Date'])
        msa_df.loc[i, 'date'] = date
        msa_df.loc[i, 'year'] = date.year

    #msa_df = msa_df[msa_df.year >= 1990]

    for i in range(n_files):
        if i % 100 == 0 and i > 0:
            print(i)

        msa_id = df.loc[i, 'df_index']
        caseid = df.loc[i, 'caseid']
        name = str(df.loc[i, 'shooter_names'])
        # fix an important name error
        name = re.sub('Marteen', 'Mateen', name)
        names = name.split()
        age = str(df.loc[i, 'age'])
        age_string = str(age) + '-year-old'
        city = str(df.loc[i, 'city'])
        title = df.loc[i, 'title']

        if msa_id == 272:
            # Kalamzoo duplicate
            print("Skipping", i, title)
        elif msa_id == 276:
            # Belfair duplicate
            print("Skipping", i, title)
        elif msa_id == 293:
            # Sherman, Texas duplicate
            print("Skipping", i, title)
        elif msa_id == 280:
            # Chelsea, MA duplicate
            print("Skipping", i, title)
        elif msa_id == 283:
            # Kansas City duplicate
            print("Skipping", i, title)
        elif msa_id == 331:
            # Cape Coral
            print("Skipping", i, title)
        else:
            age_found = False
            name_found = False
            city_found = False

            filename = os.path.join(parsed_dir, parse_prefix + '_' + str(i) + '.json')
            parse = fh.read_json(filename)

            sentences = parse['sentences']
            for sentence in sentences:
                tokens = [token['word'] for token in sentence['tokens']]
                lower_tokens = [token.lower() for token in tokens]
                sentence_text = ' '.join(tokens)
                if age_string in lower_tokens:
                    age_found = True
                if city in sentence_text:
                    city_found = True
                for name in names:
                    if name in tokens:
                        name_found = True

            msa_df.loc[msa_id, 'n_total_articles'] += 1
            if age_found or city_found or name_found:
                msa_df.loc[msa_id, 'n_valid_articles'] += 1

                terrorism_mention = False
                unnegated_terrorism_mention = False
                mental_mention = False
                for sentence in sentences:
                    tokens = [token['word'].lower() for token in sentence['tokens']]
                    sentence_text = ' '.join(tokens)
                    if 'terrorism' in tokens or 'terrorist' in tokens:
                        terrorism_mention = True
                        if 'not' in tokens or re.match('no\s*\S* evidence', sentence_text):
                            print(sentence_text)
                        else:
                            unnegated_terrorism_mention = True
                    if 'mental' in tokens:
                        mental_mention = True

                if terrorism_mention:
                    msa_df.loc[msa_id, 'n_terrorism_mentions'] += 1
                if unnegated_terrorism_mention:
                    msa_df.loc[msa_id, 'n_unnegated_terrorism_mentions'] += 1
                if mental_mention:
                    msa_df.loc[msa_id, 'n_mental_mentions'] = 1

    msa_df.to_csv(outfile)
    print(msa_df.n_valid_articles.sum())


if __name__ == '__main__':
    main()
