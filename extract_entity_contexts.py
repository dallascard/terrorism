import os
import re
from optparse import OptionParser
from collections import Counter, defaultdict

import pandas as pd

import file_handling as fh

def main():
    usage = "%prog parsed.ids.jsonlist articles.csv output_dir"
    parser = OptionParser(usage=usage)
    #parser.add_option('-v', dest='vocab_size', default=1000,
    #                  help='Maximum number of words to keep: default=%default')
    parser.add_option('-m', dest='min_df', default=3,
                      help='Minimum occurrence count for context words: default=%default')
    parser.add_option('-d', dest='max_depth', default=2,
                      help='Max depth in parse tree: default=%default')
    parser.add_option('-p', dest='pos', default=None,
                      help='Filter by POS tag(s) (e.g. JJ): default=%default')
    #parser.add_option('--filter', action="store_true", dest="filter", default=False,
    #                  help='Filter out unknown mental: default=%default')

    (options, args) = parser.parse_args()

    infile = args[0]
    csv_file = args[1]
    output_dir = args[2]

    max_depth = int(options.max_depth)
    min_df = int(options.min_df)
    pos = options.pos
    #filter = options.filter

    lines = fh.read_jsonlist(infile)
    df = pd.read_csv(csv_file, header=0, index_col=0)

    stopwords = set()

    # go through all documents and build a vocab of relevant tuple words
    search_terms = ['mental', 'terrorism']
    word_counts, entity_contexts, words_found = process_lines(lines, stopwords, search_terms, max_depth=max_depth, pos=pos)

    print(word_counts.most_common(n=30))

    print("Size of full vocab = {:d}".format(len(word_counts)))
    vocab = [w for w, c in word_counts.items() if c >= min_df]
    vocab_size = len(vocab)
    print("Size of filtered vocab = {:d}".format(vocab_size))
    vocab.sort()

    vocab_index = dict(zip(vocab, range(len(vocab))))

    outlines = []
    for doc_id, words in entity_contexts.items():
        # filter out duplicates
        words = [word for word in words if word in vocab_index]
        
        if len(words) > 2:
            event_name = df.loc[doc_id, 'title']
            text = ' '.join(words)
            outline = {'id': doc_id, 'text': text, 'event_name': event_name}
            outline['name'] = event_name + '_' + str(doc_id)
            outline['simple_race'] = df.loc[doc_id, 'simple_race']
            outline['white'] = int(df.loc[doc_id, 'white'])
            for term in search_terms:
                if words_found[doc_id][term] > 0:
                    outline[term] = 1
                else:
                    outline[term] = 0

            #if filter:
            #    if outline['mental'] != 'Unknown':
            #        outlines.append(outline)
            #else:
            outlines.append(outline)

    """
    all_events = {}
    for doc_id, words in entity_contexts.items():
        # filter out duplicates
        words = [word for word in words if word in vocab_index]
        event_name = df.loc[doc_id, 'title']
        if event_name in all_events:
            all_events[event_name]['words'] = all_events[event_name]['words'] + words
        else:
            all_events[event_name] = {'id': doc_id, 'words': words, 'event_name': event_name, 'name': event_name + '_' + str(doc_id)}

    outlines = []
    for key, value in all_events.items():
        if len(value['words']) > 2:
            outlines.append({'id': value['id'], 'text': ' '.join(value['words']), 'event_name': key})
    """
    fh.write_jsonlist(outlines, os.path.join(output_dir, 'contexts.jsonlist'))


def process_lines(lines, stopwords, search_terms, max_depth=2, pos=None):
    """
    Call me twice! First with vocab=None to choose a vocab, and then with a learned vocab to extract entities
    """

    entity_contexts = {}

    word_counts = Counter()
    words_found = defaultdict(dict)

    n_articles_with_contexts = 0
    for line_i, line in enumerate(lines):
        if line_i % 1000 == 0 and line_i > 0:
            print(line_i)
        doc_id = line['id']
        tokens = line['sentences']
        for search_word in search_terms:
            term_found = 0
            for sent in tokens:
                if search_word in sent:
                    term_found = 1
            words_found[doc_id][search_word] = term_found

        deps = line['dependencies']
        corefs = line['coref']
        pos_tags = line['pos_tags']
        assert len(corefs) == 1
        for e_i, entity in enumerate(corefs):
            tokens_to_add = defaultdict(list)
            context_i = []
            # make note of which tokens are entity mentions to avoid including names as modifiers
            #entity = sorted(entity, key=lambda x: (x['sent'], x['start']))
            mention_tokens = defaultdict(set)
            for mention in entity:
                start = mention['start']
                end = mention['end']
                sentence = mention['sent']
                for token_index in range(start, end):
                    mention_tokens[sentence].add(token_index)
                #person_tokens[sentence].update(list(range(start, end)))
            #print("\tEntity:", entity_name)
            for mention in entity:
                start = mention['start']
                end = mention['end']
                sentence = mention['sent']
                head = mention['head']

                neighbours = get_neighbours(deps, sentence, head, max_depth=max_depth)

                #temp = []
                for index in neighbours:
                    token = tokens[sentence][index].lower()
                    if index not in mention_tokens[sentence] and re.match(r'[a-z]', token) is not None and token not in stopwords:
                        if pos is not None and pos_tags is not None:
                            if pos_tags[sentence][index] == pos:
                                tokens_to_add[sentence].append(index)
                                #context_i.append(token)
                        else:
                            tokens_to_add[sentence].append(index)
                            #context_i.append(token)

            if len(tokens_to_add) > 0:
                for sentence, token_indices in tokens_to_add.items():
                    for index in token_indices:
                        context_i.append(tokens[sentence][index])
                entity_contexts[doc_id] = context_i
                word_counts.update(context_i)
                n_articles_with_contexts += 1

    print("Articles with sufficient contexts:", n_articles_with_contexts)

    return word_counts, entity_contexts, words_found


def get_neighbours(deps, sentence, head, max_depth=2):
    visited = set()
    to_visit = [head]
    neighbours = set()

    depth = 0
    while len(to_visit) > 0:
        next_layer = []
        node = to_visit.pop()
        visited.add(node)
        arc_to_parent = deps[sentence][node]
        parent_index = arc_to_parent[1]
        if parent_index not in visited and parent_index not in to_visit:
            next_layer.append(parent_index)
            neighbours.add(parent_index)

        children = [d for d in deps[sentence] if d[1] == node]
        for child in children:
            child_index = child[0]
            if child_index not in visited and child_index not in to_visit:
                next_layer.append(child_index)
                neighbours.add(child_index)

        #print(to_visit, neighbours)
        if depth < max_depth:
            to_visit.extend(next_layer)
        depth += 1

    return list(neighbours)


if __name__ == '__main__':
    main()
