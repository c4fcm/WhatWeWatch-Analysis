import ConfigParser
import csv
import time

import numpy as np
import pylab as P

import util

# Read config
config = ConfigParser.RawConfigParser()
config.read('app.config')

exp_id = time.time()

videos = dict()

# Open data file
with open('data/%s' % config.get('data', 'filename'), 'rb') as f:
    reader = csv.reader(f)
    # Skip header
    reader.next()
    # Load rows
    for row in reader:
        date = row[0].strip()
        loc = row[1].strip()
        vid_id = row[2].strip()
        videos[vid_id] = videos.get(vid_id, dict())
        videos[vid_id][loc] = videos[vid_id].get(loc, list())
        videos[vid_id][loc].append(date)

# Calculate spread
spread = list()
for vid_id, countries in videos.iteritems():
    spread.append((vid_id, len(countries)))
util.write_results_csv('findstatistics', exp_id, 'spread', spread, ('Video ID', 'Number of Countries'))
