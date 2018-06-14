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
    #parser.add_option('-d', dest='max_depth', default=2,
    #                  help='Max depth in parse tree: default=%default')
    #parser.add_option('-p', dest='pos', default=None,
    #                  help='Filter by POS tag(s) (e.g. JJ): default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    infile = args[0]
    csv_file = args[1]
    output_dir = args[2]

    #max_depth = int(options.max_depth)
    min_df = int(options.min_df)
    #pos = options.pos

    lines = fh.read_jsonlist(infile)
    df = pd.read_csv(csv_file, header=0, index_col=0)

    stopwords = set()

    # go through all documents and build a vocab of relevant tuple words
    word_counts, entity_contexts = process_lines(lines, stopwords)

    print(word_counts.most_common(n=30))

    print("Size of full vocab = {:d}".format(len(word_counts)))
    vocab = [w for w, c in word_counts.items() if c >= min_df]
    vocab_size = len(vocab)
    print("Size of filtered vocab = {:d}".format(vocab_size))
    vocab.sort()

    vocab_index = dict(zip(vocab, range(len(vocab))))
    outlines = []
    for doc_id, words in entity_contexts.items():
        words = [word for word in words if word in vocab_index]
        if len(words) > 0:
            event_name = df.loc[doc_id, 'title']
            outlines.append({'id': doc_id, 'text': ' '.join(words), 'event_name': event_name, 'name': event_name + '_' + str(doc_id)})

    fh.write_jsonlist(outlines, os.path.join(output_dir, 'tuples.jsonlist'))

    #_, entity_contexts = process_lines(lines, stopwords, vocab)


def process_lines(lines, stopwords):
    """
    Call me twice! First with vocab=None to choose a vocab, and then with a learned vocab to extract entities
    """

    entity_contexts = {}

    word_counts = Counter()

    n_articles_with_contexts = 0
    for line_i, line in enumerate(lines):
        if line_i % 1000 == 0 and line_i > 0:
            print(line_i)
        doc_id = line['id']
        tokens = line['lemmas']
        deps = line['dependencies']
        corefs = line['coref']
        pos_tags = line['pos_tags']
        assert len(corefs) == 1
        for e_i, entity in enumerate(corefs):
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

                neighbours = get_neighbours(deps, sentence, head)

                #temp = []
                for index, role_type in neighbours:
                    token = tokens[sentence][index].lower()
                    if index not in mention_tokens[sentence] and re.match(r'[a-z]', token) is not None and token not in stopwords:
                        context_i.append(token + '_' + role_type)

            if len(context_i) > 2:
                entity_contexts[doc_id] = context_i
                word_counts.update(context_i)
                n_articles_with_contexts += 1

    print("Articles with sufficient contexts:", n_articles_with_contexts)

    return word_counts, entity_contexts


def get_neighbours(deps, sentence, pos_tags, head):
    visited = set()
    to_visit = [head]
    neighbours = set()

    depth = 0
    while len(to_visit) > 0:
        next_layer = []
        node = to_visit.pop()
        visited.add(node)
        arc_to_parent = deps[sentence][node]
        arc_type = arc_to_parent[2]
        parent_index = arc_to_parent[1]
        parent_pos = pos_tags[sentence][parent_index]
        if parent_index not in visited and parent_index not in to_visit:
            if parent_pos[0] == 'V' and (arc_type == 'nsubj' or arc_type == 'agent'):
                neighbours.add((parent_index, 'A'))
            elif parent_pos[0] == 'V' and (arc_type =='dobj' or arc_type == 'nsubjpass' or arc_type == 'iobj' or arc_type.startswith('nmod')):
                neighbours.add((parent_index, 'P'))
            elif (parent_pos[0] == 'J' or parent_pos[0] == 'N') and (arc_type == 'nsubj' or arc_type == 'appos'):
                neighbours.add((parent_index, 'M'))

        children = [d for d in deps[sentence] if d[1] == node]
        for child in children:
            child_index = child[0]
            child_pos = pos_tags[sentence][child_index]
            arc_type = child[2]
            if child_index not in visited and child_index not in to_visit:
                if (child_pos[0] == 'J' or child_pos[0] == 'N') and (arc_type == 'nsubj' or arc_type == 'appos' or arc_type == 'amod' or arc_type == 'compound'):
                    neighbours.add((child_index, 'M'))

    return list(neighbours)


if __name__ == '__main__':
    main()
