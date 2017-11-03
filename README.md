This is very much a work in progress. Features **will** change over time.

[![Build Status](https://travis-ci.org/gbasood/vgstation-statistics-viewer.svg?branch=master)](https://travis-ci.org/gbasood/vgstation-statistics-viewer)
[![codecov](https://codecov.io/gh/gbasood/vgstation-statistics-viewer/branch/master/graph/badge.svg)](https://codecov.io/gh/gbasood/vgstation-statistics-viewer)

# Statistics viewer for /vg/station
This is a statistics viewer which parses the statfiles exported from /vg/station rounds and writes them to db, then displays them in such a way that people can actually UNDERSTAND THEM WOW

Anyone who wants to help out or call my code shit is more than welcome. I'd like to catch any issuse with this before they become real issues. This is the first project of this nature I have undertaken (in Python at least) and I am completely amateur.

# Prereqs
 - Python 3.6.1
 - For package dependencies:
`pip install -r requirements.txt`

# Setup
 - See requirements.

 - You will need to set this environment variable, either in your shell or as part of a batch script:
   - `FLASK_APP=run.py`
   - It may be necessary to set this to an absolute path if it doesn't work the first time.
   - Additionally, if you want a debug environment, `FLASK_DEBUG=1` must be set.
 - Modify config.py as needed.
 - Run `flask db init`
 - Finally, `flask run` will run the server in a development environment.

# Additional notes
To perform a migration based on existing migration files: `flask db upgrade`
