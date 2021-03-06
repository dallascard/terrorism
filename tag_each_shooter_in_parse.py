import os
import re
import copy
import glob
from optparse import OptionParser
from collections import defaultdict

import numpy as np
import pandas as pd

import file_handling as fh

# RUN this after running parse_text_keep_all.py to pull out certain types of entities


def main():
    usage = "%prog article_db.csv parsed_dir output_dir output_prefix"
    parser = OptionParser(usage=usage)
    parser.add_option('--prefix', dest='parse_prefix', default='all',
                      help='Prefix of parsed files: default=%default')
    #parser.add_option('--all', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    csv_file = args[0]
    parsed_dir = args[1]
    output_dir = args[2]
    output_prefix = args[3]
    parse_prefix = options.parse_prefix

    preprocess_data(csv_file, parsed_dir, output_dir, output_prefix, parse_prefix)


def preprocess_data(csv_file, parsed_dir, output_dir, output_prefix, parse_prefix):

    df = pd.read_csv(csv_file, header=0, index_col=0)
    n_rows, n_columns = df.shape
    print(df.shape)

    files = glob.glob(os.path.join(parsed_dir, '*.json'))
    n_files = len(files)

    #assert n_files == n_rows

    coref_input = []

    pos_tags_all = set()
    print("Parsing %d documents" % n_files)
    #for i in range(n_files):
    for i in range(n_files):
        if i % 1000 == 0 and i > 0:
            print(i)

        valid = df.loc[i, 'matching']
        name = str(df.loc[i, 'shooter_names'])
        # fix an important name error
        name = re.sub('Marteen', 'Mateen', name)
        names = name.split()
        age = str(df.loc[i, 'age'])
        event_name = 'msa-' + re.sub('\s', '-', df.loc[i, 'title'])

        msa_index = int(df.loc[i, 'df_index'])

        if msa_index == 272:
            # Kalamzoo duplicate
            print("Skipping", i, event_name)
        elif msa_index == 276:
            # Belfair duplicate
            print("Skipping", i, event_name)
        elif msa_index == 293:
            # Sherman, Texas duplicate
            print("Skipping", i, event_name)
        elif msa_index == 280:
            # Chelsea, MA duplicate
            print("Skipping", i, event_name)
        elif msa_index == 283:
            # Kansas City duplicate
            print("Skipping", i, event_name)
        elif msa_index == 331:
            # Cape Coral
            print("Skipping", i, event_name)

        elif valid:
            filename = os.path.join(parsed_dir, parse_prefix + '_' + str(i) + '.json')
            parse = fh.read_json(filename)

            # get the text and convert to tokens
            sentences, sentences_tagged, target_mentions, pos_tags, dependencies = process_parse(parse, names, age, event_name)

            sentences_pruned = []
            for sent in sentences_tagged:
                tokens = [token for token in sent if token != '__DROP__']
                sentences_pruned.append(' '.join(tokens))
            text_pruned = ' '.join(sentences_pruned)

            # write output for e2e-coref
            coref_input.append({"id": i,
                                "clusters": [],
                                "doc_key": "nw",
                                "sentences": sentences,
                                "text_tagged": text_pruned,
                                "pos_tags": pos_tags,
                                "dependencies": dependencies,
                                "coref": [target_mentions]
                                })

            print(i, names, age, len(target_mentions))

        fh.write_jsonlist(coref_input, os.path.join(output_dir, output_prefix + '.parsed.jsonlist'))


def process_parse(parse, names, age, event_name):

    sentences = []
    lemmas = []
    pos_tags = []
    dependencies = []
    ner_mentions = {}

    age_mention = str(age) + '-year-old'

    target_mentions = {}
    target_mentions_flat = []

    sentences_tagged = []

    # gather the tokens in each sentence and extract certain token patterns
    for sent_i, sent in enumerate(parse['sentences']):
        # note: using lemmas instead of words!
        sentences.append([token['word'] for token in sent['tokens']])
        sentences_tagged.append([token['word'] for token in sent['tokens']])
        lemmas.append([token['lemma'] for token in sent['tokens']])
        pos_tags.append([token['pos'] for token in sent['tokens']])
        deps = [(arc['dependent']-1, arc['governor']-1, arc['dep']) for arc in sent['enhancedPlusPlusDependencies']]
        deps.sort()
        dependencies.append(deps)
        target_mentions[sent_i] = defaultdict(list)

        for mention in sent['entitymentions']:
            # make note of which entities have a PERSON mention (or other NER types)
            if mention['ner'] == 'PERSON':
                start = mention['tokenBegin']
                end = mention['tokenEnd']
                ner_mentions[(sent_i, start, end)] = 0

    # now process the coref, looking for the person of interest
    corefs = parse['corefs']
    keys = list(corefs.keys())
    keys.sort()
    for key in keys:
        include_this_entity = False
        mentions = corefs[key]
        # take all corefering entities that mention the target
        for mention in mentions:
            sent_i = mention['sentNum'] - 1
            start = mention['startIndex'] - 1
            end = mention['endIndex'] - 1
            head_index = mention['headIndex'] - 1
            words = sentences[sent_i][start:end]
            if np.all([word in names for word in words]):
                include_this_entity = True
                if (sent_i, start, end) in ner_mentions:
                    ner_mentions[(sent_i, start, end)] = 1

        if include_this_entity:
            for mention in mentions:
                sent_i = mention['sentNum'] - 1
                start = mention['startIndex'] - 1
                end = mention['endIndex'] - 1
                head = mention['headIndex'] - 1
                if end - start < 4:
                    sentences_tagged[sent_i][start] = event_name
                    if end > start+1:
                        for i in range(start+1, end):
                            sentences_tagged[sent_i][i] = '__DROP__'

                    target_mentions[sent_i][head].append({'sent': sent_i, 'start': start, 'end': end, 'text': mention['text'], 'head': mention['headIndex']-1, 'isRepresentative': mention['isRepresentativeMention']})
                    target_mentions_flat.append({'sent': sent_i, 'start': start, 'end': end, 'text': mention['text'], 'head': mention['headIndex']-1, 'isRepresentative': mention['isRepresentativeMention']})

    # add persons with matching names that haven't already been added
    for mention, value in ner_mentions.items():
        if value == 0:
            sent_i, start, end = mention
            words = [sentences[sent_i][t_i] for t_i in range(start, end)]
            for word in words:
                if word in names:
                    # assume the last token is the head, since this is a person
                    if end-1 not in target_mentions[sent_i]:
                        if end - start < 4:
                            target_mentions[sent_i][end-1].append({'sent': sent_i, 'start': start, 'end': end, 'text': ' '.join(words), 'head': end-1, 'isRepresentative': False})
                            target_mentions_flat.append({'sent': sent_i, 'start': start, 'end': end, 'text': ' '.join(words), 'head': end-1, 'isRepresentative': False})
                            sentences_tagged[sent_i][start] = event_name
                            if end > start+1:
                                for j in range(start+1, end):
                                    sentences_tagged[sent_i][j] = '__DROP__'


    # also look for certain patterns
    age_pos_tags = set()
    for sent_i, sent in enumerate(parse['sentences']):
        for t_i, token in enumerate(sent['tokens']):
            lemma = token['lemma'].lower()
            word = token['word'].lower()
            pos = token['pos']
            if lemma == 'gunman' or lemma == 'shooter':
                if t_i not in target_mentions[sent_i]:
                    target_mentions[sent_i][t_i].append({'sent': sent_i, 'start': t_i, 'end': t_i+1, 'text': word, 'head': t_i, 'isRepresentative': False})
                    target_mentions_flat.append({'sent': sent_i, 'start': t_i, 'end': t_i+1, 'text': word, 'head': t_i, 'isRepresentative': False})
                    sentences_tagged[sent_i][t_i] = event_name

            if word == age_mention:
                # use the governor if this is a JJ/amod XX-year-old, otherwise, treat it as a noun phrase
                governors = [(arc['governor']-1, arc['dep']) for arc in sent['enhancedPlusPlusDependencies'] if arc['dependent']-1 == t_i]
                if len(governors) > 0:
                    governor = governors[0]
                    if pos == 'JJ' and governor[1] == 'amod':
                        governor_id = governor[0]
                        if governor_id not in target_mentions[sent_i]:
                            target_mentions[sent_i][governor_id].append({'sent': sent_i, 'head': governor_id, 'start': governor_id, 'end': governor_id+1, 'text': word, 'isRepresentative': False})
                            target_mentions_flat.append({'sent': sent_i, 'head': governor_id, 'start': governor_id, 'end': governor_id+1, 'text': word, 'isRepresentative': False})
                            sentences_tagged[sent_i][governor_id] = event_name

                    else:
                        if t_i not in target_mentions[sent_i]:
                            target_mentions[sent_i][t_i].append({'sent': sent_i, 'head': t_i, 'start': t_i, 'end': t_i+1, 'text': word, 'isRepresentative': False})
                            target_mentions_flat.append({'sent': sent_i, 'head': t_i, 'start': t_i, 'end': t_i+1, 'text': word, 'isRepresentative': False})
                            sentences_tagged[sent_i][t_i] = event_name


    return sentences, sentences_tagged, target_mentions_flat, pos_tags, dependencies


if __name__ == '__main__':
    main()

