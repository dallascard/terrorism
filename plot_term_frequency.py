import matplotlib as mpl
mpl.use('Agg')

import os
import datetime
from optparse import OptionParser
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sbn

import file_handling as fh

# Uses the output of count_word_in_nyt.py


def main():
    usage = "%prog input_dir"
    parser = OptionParser(usage=usage)
    #parser.add_option('-t', dest='target_word', default='terrorism',
    #                  help='Word to put in title: default=%default')
    parser.add_option('-s', type=int, dest='smoothing', default=30,
                      help='Size of smoothing window: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()

    input_dir = args[0]
    word = options.target_word

    articles = fh.read_json(os.path.join(input_dir, 'articles_per_day.json'))
    targets = fh.read_json(os.path.join(input_dir, 'target_counts_per_day.json'))

    keys = [int(k) for k in articles.keys()]
    keys.sort()

    ordinal_dates = range(keys[0], keys[-1]+1)
    dates = [datetime.datetime.fromordinal(d) for d in ordinal_dates]
    #week_list = [d.isocalendar()[1] for d in dates]

    #weeks = list(set(week_list))
    #weeks.sort()
    #week_index = dict(zip(weeks, range(len(weeks))))

    article_counts = np.zeros(len(dates))
    target_counts = np.zeros(len(dates))

    for d_i, d in enumerate(ordinal_dates):
        #week = week_list[d_i]
        if str(d) in articles:
            article_counts[d_i] = articles[str(d)]
        if str(d) in targets:
            target_counts[d_i] = targets[str(d)]

    sbn.set_style('white')
    #fig, axes = plt.subplots(2, sharex=True)
    fig, ax = plt.subplots(figsize=(8, 4))

    """
    ax1.set_title('NYT articles mentioning "' + word + '"')
    ax1.plot_date(dates, target_counts, linestyle='solid', marker='None', alpha=0.5, label='Daily')
    target_counts_smoothed = moving_average(target_counts, radius=15, extend_ends=True)
    ax1.plot_date(dates, target_counts_smoothed, linestyle='solid', marker='None', label='Smoothed')
    ax1.set_ylabel('Count')
    ax1.legend()
    """

    target_freq = target_counts / (article_counts + 1)
    ax.plot_date(dates, target_freq, linestyle='solid', marker='None', alpha=0.4, label='Daily')
    #ax.scatter(dates, target_freq, s=1, alpha=0.3, label='Daily')
    target_freq_smoothed = moving_average(target_freq, radius=options.smoothing, extend_ends=True)
    ax.plot_date(dates, target_freq_smoothed, c='k', linewidth=1, linestyle='solid', marker='None', alpha=1.0, label='Smoothed')
    ax.set_ylabel('Proportion of articles')
    ax.set_xlabel('Date')
    ax.legend()

    plt.savefig(word + '.pdf', bbox_inches='tight')



def moving_average(x, radius=2, extend_ends=False, halve_ends=False):
    """
    Apply a moving-average filter (used for trend estimation)
    :param x: time series to be smoothed
    :param radius: radius of filter (i.e size = 2 * radius + 1); default = 2
    :param extend_ends: if True, compute end points of smoothed time series by repeating ends; default=False
    :param halve_ends: divide the weights of the two end points by 2 (used for seasonal decomposition)
    :return: a smoothed time series
    """
    n = len(x)
    if extend_ends:
        x_plus = np.zeros(n + 2 * radius)
        x_plus[:radius] = x[0]
        x_plus[radius:n+radius] = x
        x_plus[n+radius:] = x[-1]
        x = x_plus
        n = len(x)

    weights = np.ones(radius * 2 + 1)
    if halve_ends:
        weights[0] /= 2.0
        weights[-1] /= 2.0
        weights /= (2.0 * radius)
    else:
        weights /= (2.0 * radius + 1.0)
    smoothed = np.zeros(n - 2 * radius)
    for t in range(n - 2 * radius):
        smoothed[t] = np.dot(weights, x[t:t+radius*2+1]) / np.sum(weights)
    return smoothed


if __name__ == '__main__':
    main()
