## What We Watch
Data analysis scripts for What We Watch
http://whatwewatch.mediameter.org

## Dependencies
To use this code you must install the following dependencies:
* sqlalchemy
* numpy
* scipy
* matplotlib
* http://github.com/elplatt/lda-gibbs-em (as lda/)

## Contents

This package contains scripts to analyze country-coded video trending data
available at http://www.youtube.com/trendsmap .  It contains the following
files:

* app.config.sample - Sample configuration for the database, data set, etc.
* tests/ - Unit tests
* data/ - Data sets.
* cleandata.py - Load data from a sql database, remove unwanted data, and write to a CSV in the
data/ directory.
* findlikelihood.py - Track the likelihood of LDA clusters over all training iterations.
* findparams.py - Find clusters for different parameter settings and record the likelihood of each.
* fundclusters.py - Find all clusters in the data and output to a csv.
* db.py - Database schema for sqlalchemy, used by cleandata.py.
