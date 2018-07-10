import matplotlib as mpl
mpl.use('Agg')

import re
import json
from optparse import OptionParser

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn import random_projection

from representations.embedding import Embedding


def main():
    usage = "%prog sgns.words sgns.words.vocab"
    parser = OptionParser(usage=usage)
    #parser.add_option('-n', dest='n', default=10,
    #                  help='Most similar: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    vec_file = args[0]
    vocab_file = args[1]

    #n = int(options.n)

    emb = Embedding(vec_file)
    subset = {}

    with open(vocab_file, 'r') as f:
        vocab = f.readlines()
    vocab = [v.strip() for v in vocab]
    vocab = [v for v in vocab if v.startswith('msa-')]

    for word in vocab:
        subset[word] = emb.represent(word)

    keys = list(subset.keys())
    n_words = len(keys)
    emb_size = len(subset[keys[0]])
    for word in keys:
        print(word)

    print("Doing dimensionality reduction")
    vectors = np.zeros([n_words, emb_size])
    for word_i, word in enumerate(keys):
        vectors[word_i, :] = subset[word]

    tsne = TSNE(n_components=2)
    proj = tsne.fit_transform(vectors)

    #pca = PCA(n_components=2)
    #proj = pca.fit_transform(vectors)

    #transformer = np.random.randn(emb_size, 2)
    #proj = np.dot(vectors, transformer)

    print("plotting")
    fig, ax = plt.subplots(figsize=(8, 6))

    for i, word in enumerate(keys):
        ax.scatter([proj[i, 0]], [proj[i, 1]], color='k', alpha=0.6, s=1, edgecolors=None)
        if word == 'msa-orlando-nightclub-massacre':
            ax.text(proj[i, 0], proj[i, 1], 'Orlando', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'msa-san-bernardino,-california':
            ax.text(proj[i, 0], proj[i, 1], 'San Bernadino', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'msa-amnicola-training-center,-chattanooga':
            ax.text(proj[i, 0], proj[i, 1], 'Chattanooga', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'msa-columbine-high-school':
            ax.text(proj[i, 0], proj[i, 1], 'Columbine', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'msa-westside-middle-school':
            ax.text(proj[i, 0], proj[i, 1], 'Westside Middle School', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'msa-heritage-high-school':
            ax.text(proj[i, 0], proj[i, 1], 'Heritage High School', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'msa-virginia-tech--campus':
            ax.text(proj[i, 0], proj[i, 1], 'Virginia Tech', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'msa-tucson,-arizona':
            ax.text(proj[i, 0], proj[i, 1], 'Tuscon, Arizona', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'msa-movie-theater-in-aurora':
            ax.text(proj[i, 0], proj[i, 1], 'Aurora', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'msa-mother-emanuel-ame-church':
            ax.text(proj[i, 0], proj[i, 1], 'Mother Emanuel', fontsize=8, alpha=0.6, ha='center', va='baseline')
        if word == 'Umpqua Community College':
            ax.text(proj[i, 0], proj[i, 1], 'Umpqua Community College', fontsize=8, alpha=0.6, ha='center', va='baseline')


        #if word in target_words:
        #    ax.scatter([proj[i, 0]], [proj[i, 1]], color='k', alpha=0.6, s=1, edgecolors=None)
        #    ax.text(proj[i, 0], proj[i, 1], word, fontsize=8, alpha=0.6, ha='center', va='baseline', color='red')
        #else:
        #    ax.scatter([proj[i, 0]], [proj[i, 1]], color='k', alpha=0.6, s=1, edgecolors=None)
        #    ax.text(proj[i, 0], proj[i, 1], word, fontsize=8, alpha=0.6, ha='center', va='baseline')

    previous_x = None
    previous_y = None

    """
    for i, year in enumerate(years):
        target_word = base_word + '_' + str(year)
        index = keys.index(target_word)
        x = proj[index, 0]
        y = proj[index, 1]
        if previous_x is not None:
            plt.plot([previous_x, x], [previous_y, y], c='b', linewidth=1, alpha=(0.8 * i/len(years) + 0.1))
        ax.scatter([x], [y], color='red', alpha=0.5, s=2, edgecolors=None)
        previous_x = x
        previous_y = y
    """

    plt.savefig('shooters.pdf', bbox_inches='tight')


if __name__ == '__main__':
    main()
