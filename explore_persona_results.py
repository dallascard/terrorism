from collections import defaultdict
from optparse import OptionParser

import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm


import file_handling as fh


def main():
    usage = "%prog contexts.jsonlist personas.npz"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    contexts_file = args[0]
    personas_file = args[1]

    contexts = fh.read_jsonlist(contexts_file)
    theta = np.load(personas_file)['theta']
    print(theta.shape)
    print(len(contexts))
    n_items, n_topics = theta.shape
    mean_freq = theta.mean(0)
    print(theta.mean(0))
    bincount = np.bincount(np.argmax(theta, 1), minlength=n_topics)
    print(bincount)
    print(bincount / float(bincount.sum()))

    race = np.zeros(n_items)
    indices = defaultdict(list)
    for i, context in enumerate(contexts):
        event_name = context['event_name']
        indices[event_name].append(i)
        race[i] = context['race']

    for k in range(n_topics):
        order = list(np.argsort(theta[:, k]))
        order.reverse()
        print(k)
        for j in range(6):
            context = contexts[order[j]]
            print(context['event_name'], context['id'])

    for event in indices.keys():
        personas = np.argmax(theta[indices[event], :], axis=1)
        print(event, np.bincount(personas, minlength=n_topics))

    """
    articles = indices['Fort Hood']
    subset = theta[articles, :]
    print(subset.mean(0))
    subset = subset / mean_freq
    print(subset.mean(0))
    fig, ax = plt.subplots(1, 3, figsize=(8, 8))
    ax[0].imshow(subset)
    print(np.bincount(np.argmax(subset, 1), minlength=n_topics))

    articles = indices['Fort Hood Army Base']
    subset = theta[articles, :]
    print(subset.mean(0))
    subset = subset / mean_freq
    print(subset.mean(0))
    ax[1].imshow(subset)
    print(np.bincount(np.argmax(subset, 1), minlength=n_topics))

    articles = indices['Washington Navy Yard']
    subset = theta[articles, :]
    print(subset.mean(0))
    subset = subset / mean_freq
    print(subset.mean(0))
    ax[2].imshow(subset)
    print(np.bincount(np.argmax(subset, 1), minlength=n_topics))
    plt.show()
    """

    #model = sm.OLS(race, theta).fit()
    #print(model.summary())

    #for j in range(n_topics):
    #    print(np.corrcoef(race, theta[:, j])[0])
    model = LogisticRegression(C=1.0, penalty='l1')
    model.fit(X=theta, y=race)
    print(model.coef_)


if __name__ == '__main__':
    main()
