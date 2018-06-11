import os
from collections import Counter
from optparse import OptionParser

import numpy as np

import file_handling as fh


def main():
    usage = "%prog contexts.jsonlist output_dir"
    parser = OptionParser(usage=usage)
    parser.add_option('-v', dest='vocab_size', default=1000,
                      help='Vocab size: default=%default')
    parser.add_option('-k', dest='k', default=5,
                      help='k: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    infile = args[0]
    output_dir = args[1]
    vocab_size = int(options.vocab_size)
    k = int(options.k)

    lines = fh.read_jsonlist(infile)

    stopwords = fh.read_text('stopwords.txt')
    stopwords = {s.strip() for s in stopwords}

    full_vocab = Counter()
    for line in lines:
        text = line['text']
        full_vocab.update(text.split())

    most_common = full_vocab.most_common(n=vocab_size)
    vocab, counts = zip(*most_common)
    vocab = list(vocab)
    vocab = [word for word in vocab if word not in stopwords]
    vocab.sort()
    vocab_size = len(vocab)
    print("Vocab size after filtering = {:d}".format(vocab_size))
    vocab_index = dict(zip(vocab, range(vocab_size)))

    filtered_lines = []
    for line in lines:
        text = line['text']
        words = [word for word in text.split() if word in vocab_index]
        if len(words) > 0:
            filtered_lines.append(words)

    counts = np.zeros((len(filtered_lines), vocab_size), dtype=float)

    for line_i, line in enumerate(filtered_lines):
        for word in line:
            counts[line_i, vocab_index[word]] += 1.0

    base_dist = np.sum(counts, axis=0)
    print(np.min(base_dist), np.mean(base_dist), np.max(base_dist))
    base_dist = np.power(base_dist, 1.0)
    base_dist_sum = base_dist.sum()

    row_sums = counts.sum(axis=1)
    col_sums = counts.sum(axis=0)
    col_sums = np.power(base_dist, 0.75)
    col_sums_sum = col_sums.sum()

    #w_c_sum = counts.sum()
    print(np.min(counts), np.mean(counts), np.max(counts))
    for i in range(len(filtered_lines)):
        for j in range(vocab_size):
            counts[i, j] = float(counts[i, j]) / row_sums[i] / col_sums[j] * col_sums_sum
            if counts[i, j] < 1.0:
                counts[i, j] = 1.0

    counts = np.log(counts)
    print(np.min(counts), np.mean(counts), np.max(counts))

    u, s, v = np.linalg.svd(counts)
    print(u.shape)
    print(s.shape)
    print(v.shape)
    #np.savez('svd.npz', u=u, s=s, v=v)

    for i in range(5):
        print(i)
        order = list(np.argsort(v[i, :]))
        order.reverse()
        print(' '.join([vocab[j] for j in order[:20]]))
        print([v[i, j] for j in order[:15]])
        order.reverse()
        print(' '.join([vocab[j] for j in order[:20]]))
        print([v[i, j] for j in order[:15]])

    doc_reps = np.dot(u[:, :k], np.diag(np.power(s[:k], 0.5)))
    np.savez('temp.npz', D=doc_reps)



if __name__ == '__main__':
    main()
