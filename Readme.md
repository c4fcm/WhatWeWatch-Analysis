
=What We Watch
Data analysis scripts

This package contains scripts to analyze country-coded video trending data
available at http://www.youtube.com/trendsmap .  It contains the following
files:

* app.config.sample - Sample configuration for the database, data set, etc.
* tests/ - Unit tests
* data/ - Data sets.
* cleandata.py - Load data from a sql database, remove unwanted data, and write to a CSV in the
data/ directory.
* db.py - Database schema for sqlalchemy, used by cleandata.py.
