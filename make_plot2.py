import matplotlib as mpl
mpl.use('Agg')

import re
from optparse import OptionParser

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn import random_projection
from sklearn.metrics.pairwise import cosine_similarity

from representations.embedding import Embedding


def main():
    usage = "%prog sgns.words"
    parser = OptionParser(usage=usage)
    #parser.add_option('-n', dest='n', default=10,
    #                  help='Most similar: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    vec_file = args[0]

    #n = int(options.n)

    emb = Embedding(vec_file)
    subset = {}

    target_words = []
    target_vectors = []
    words = []

    years = list(range(1987, 2008))

    print("Collecting vectors")
    target_word = 'terrorism_pre911'
    target_words.append(target_word)
    subset[target_word] = emb.represent(target_word)
    target_vectors.append(emb.represent(target_word))

    target_word = 'terrorism_post911'
    target_words.append(target_word)
    subset[target_word] = emb.represent(target_word)
    target_vectors.append(emb.represent(target_word))

    mean_vector = np.mean(target_vectors, axis=0)

    closest = emb.closest_to_vec(mean_vector, n=50)
    words = [pair[1] for pair in closest]
    words = [word for word in words if word != 'terrorism']
    words = [word for word in words if not re.search(r'\d', word)]
    for word in words:
        subset[word] = emb.represent(word)

    keys = list(subset.keys())
    n_words = len(keys)
    emb_size = len(subset[keys[0]])
    for word in keys:
        print(word)

    print("Doing dimensionality reduction")
    vectors = np.zeros([n_words, emb_size])
    dist1 = np.zeros(n_words)
    dist2 = np.zeros(n_words)
    for word_i, word in enumerate(keys):
        vectors[word_i, :] = subset[word]
        dist1[word_i] = np.abs(cosine_similarity(subset[word].reshape(-1, 1), subset['terrorism_pre911'].reshape(-1, 1))[0][0])
        dist2[word_i] = np.abs(cosine_similarity(subset[word].reshape(-1, 1), subset['terrorism_post911'].reshape(-1, 1))[0][0])

    tsne = TSNE(n_components=2)
    proj = tsne.fit_transform(vectors)

    #pca = PCA(n_components=2)
    #proj = pca.fit_transform(vectors)

    #transformer = np.random.randn(emb_size, 2)
    #proj = np.dot(vectors, transformer)

    print("plotting")
    fig, ax = plt.subplots(figsize=(8, 6))

    for i, word in enumerate(keys):
        if word in target_words:
            ax.scatter([proj[i, 0]], [proj[i, 1]], color='k', alpha=0.6, s=1, edgecolors=None)
            ax.text(proj[i, 0], proj[i, 1], word, fontsize=8, alpha=0.6, ha='center', va='baseline', color='red')
        else:
            ax.scatter([proj[i, 0]], [proj[i, 1]], color='k', alpha=0.6, s=1, edgecolors=None)
            ax.text(proj[i, 0], proj[i, 1], word, fontsize=8, alpha=0.6, ha='center', va='baseline')

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

    plt.savefig('test.pdf', bbox_inches='tight')


    fig, ax = plt.subplots(figsize=(8, 6))
    for i, word in enumerate(keys):
        if word not in target_words:
            ax.scatter(dist1[i], dist2[i], color='k', alpha=0.6, s=1, edgecolors=None)
            ax.text(dist1[i], dist2[i], word, fontsize=8, alpha=0.6, ha='center', va='baseline')

    plt.savefig('test2.pdf', bbox_inches='tight')



if __name__ == '__main__':
    main()
