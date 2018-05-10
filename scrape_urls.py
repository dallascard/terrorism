import os
import re
import json
from optparse import OptionParser

import newspaper
import numpy as np
import pandas as pd

def main():
    usage = "%prog database.csv output_dir summary.csv"
    parser = OptionParser(usage=usage)
    #parser.add_option('-o', dest='output_file', default=None,
    #                  help='Output file: default=%default')
    #parser.add_option('-n', dest='n', default=20,
    #                  help='Number of words to print: default=%default')
    #parser.add_option('--sort_by', dest='sort_by', default=None,
    #                  help='Print the output of a column: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    
    input_file = args[0]
    base_dir = args[1]
    summary_file = args[2]

    df = pd.read_csv(input_file, header=0)
    df_out = pd.DataFrame(columns=['filename', 'event num', 'name', 'source num', 'incident date', 'article date', 'source'])

    count = 0
    #for i in range(2):
    for i in range(len(df)):
        row = df.iloc[i]
        caseid = row['CaseID']
        name = row['Shooter Name']
        name = re.sub('/', ', ', name)
        name = re.sub(r'\s', '_', name)
        incident_date = str(row['Date'])
        output_dir = os.path.join(base_dir, str(caseid) + '_' + name)
        print('\n' + output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for s in range(7):
            source = str(row['Data Source ' + str(s+1)])
            if source[:4] == 'http' and source[:23] != 'http://en.wikipedia.org' and source[:23] != 'http://books.google.com':
                article = newspaper.Article(source)
                article.download()
                try:
                    article.parse()
                    print("Parsed", source)
                    output = {'text': article.text, 'authors': article.authors, 'date': str(article.publish_date), 'metadata': article.meta_data, 'url': source}
                    filename = os.path.join(output_dir, str(caseid) + '_' + name + '-source_' + str(s+1) + '.json')
                    with open(filename, 'w') as f:
                        json.dump(output, f, indent=2)
                    text = 'Person: ' + name + '\n'
                    text += 'Date: ' + str(article.publish_date) + '\n'
                    site_name = 'n/a'
                    if 'og' in article.meta_data:
                        if 'site_name' in article.meta_data['og']:
                            site_name = article.meta_data['og']['site_name']
                    text += 'Source: ' + site_name + '\n'
                    text += 'url: ' + source + '\n\n'
                    text += article.title + '\n\n'
                    text += article.text
                    filename = os.path.join(output_dir, str(caseid) + '_' + name + '-source_' + str(s+1) + '.txt')
                    with open(filename, 'w') as f:
                        f.write(text)
                    filename = str(caseid) + '_' + name + '-source_' + str(s+1) + '.txt'
                    df_out.loc[count] = [filename, caseid, name, str(s+1), incident_date, str(article.publish_date), site_name]
                    count += 1
                except newspaper.article.ArticleException as e:
                    print("Exception; skipping", source)
            else:
                print("Skipping", source)

    df_out.to_csv(summary_file)


    if __name__ == '__main__':
        main()
