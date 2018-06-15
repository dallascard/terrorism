import os
import glob
from optparse import OptionParser

import pandas as pd

import file_handling as fh


def main():
    usage = "%prog msa_db.csv data_dir output_file.jsonlist"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    msa_db = args[0]
    data_dir = args[1]
    output_filename = args[2]

    articles = []

    df = pd.read_csv(msa_db, header=0)
    index = df.index
    for i in index:
        row = df.loc[i]
        caseid = row['CaseID']
        title = row['Title']
        names = row['Shooter Name'].split()
        #subdirs = glob.glob(os.path.join(data_dir, '*_*'))
        subdir = os.path.join(data_dir, str(caseid) + '_' + '_'.join(names))
        if not os.path.exists(subdir):
            files = glob.glob(os.path.join(data_dir, str(caseid) + '_*', '*.json'))
        else:
            files = glob.glob(os.path.join(subdir, '*.json'))
        print(subdir, len(files))
        for f in files:
            data = fh.read_json(f)
            text = data['text']
            if len(text) > 200:
                articles.append({'id': str(i), 'caseid': str(caseid), 'event_name': title, 'text': text})

    fh.write_jsonlist(articles, output_filename, sort_keys=False)


if __name__ == '__main__':
    main()
