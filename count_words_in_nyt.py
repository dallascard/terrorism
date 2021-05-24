import os
import re
import string
import datetime
from optparse import OptionParser
from collections import Counter, defaultdict

import file_handling as fh

# compile a regex of all puncutation except hyphens
punct_chars = list(set(string.punctuation) - set("-"))
punct_chars.sort()
punctuation = ''.join(punct_chars)
replace = re.compile('[%s]' % re.escape(punctuation))


def main():
    usage = "%prog infiles.jsonlist[.gz]"
    parser = OptionParser(usage=usage)
    parser.add_option('-o', dest='output_dir', default='output',
                      help='Output_dir: default=%default')
    parser.add_option('-w', dest='target_word', default='mass shooting',
                      help='Target word: default=%default')

    (options, args) = parser.parse_args()
    infiles = args
    output_dir = options.output_dir
    target_word = options.target_word

    if not os.path.exists(output_dir):
        fh.makedirs(output_dir)

    n_articles_per_day = defaultdict(int)
    target_count_per_day = defaultdict(int)
    for f in infiles:
        print(f)
        articles = fh.read_jsonlist(f)
        print(len(articles))
        for i, article in enumerate(articles):
            if i % 10000 == 0 and i > 0:
                print(i)
            year = int(article['year'])
            month = int(article['month'])
            day = int(article['day'])
            date = datetime.date(year=year, month=month, day=day)
            ordinal_date = date.toordinal()
            n_articles_per_day[ordinal_date] += 1
            text = ''
            if 'headline' in article:
                text += article['headline'] + '\n'
            if 'body' in article:
                text += article['body']
            if 'text' in article:
                text += article['text']

            text = ' ' + clean_text(text, lower=True) + ' '
            # if we are searching for a phrase, look for it
            if ' ' in target_word:
                if target_word in text:
                    target_count_per_day[ordinal_date] += 1

            # otherwise, assume we want the exact token, so first split the text into tokens
            else:
                words = set(text.split())
                if target_word in words and 'film' not in words and 'game' not in words:
                    target_count_per_day[ordinal_date] += 1

    fh.write_to_json(n_articles_per_day, os.path.join(output_dir, 'articles_per_day.json'))
    fh.write_to_json(target_count_per_day, os.path.join(output_dir, 'target_counts_per_day.json'))


def clean_text(text, lower=True):
    # lower case
    if lower:
        text = text.lower()
    # replace all punctuation hyphens with spaces
    text = replace.sub(' ', text)
    # replace all whitespace with a single space
    text = re.sub(r'\s', ' ', text)
    # strip off spaces on either end
    text = text.strip()
    return text


if __name__ == '__main__':
    main()
