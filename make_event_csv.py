import os
from optparse import OptionParser

import numpy as np
import pandas as pd

import file_handling as fh


def main():
    usage = "%prog contexts.jsonlist output_file.csv"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    infile = args[0]
    outfile = args[1]

    lines = fh.read_jsonlist(infile)
    n_lines = len(lines)

    events = set()
    for line in lines:
        event = line['event_name']
        events.add(event)

    events = list(events)
    events.sort()
    n_events = len(events)
    event_index = dict(zip(events, range(n_events)))
    print("Found %d events" % n_events)

    event_array = np.zeros([n_lines, n_events])
    for line_i, line in enumerate(lines):
        event = line['event_name']
        event_array[line_i, event_index[event]] += 1

    df = pd.DataFrame(event_array, columns=events)
    df.to_csv(outfile)


if __name__ == '__main__':
    main()
