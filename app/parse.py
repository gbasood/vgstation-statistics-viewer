"""This file handles code for parsing statfiles into the database."""
from __future__ import unicode_literals

import os
import shutil
import sys, traceback
import re
from typing import Text

from flask import current_app
from werkzeug.local import LocalProxy

from app.parsers import csvparser, jsonparser

logger = LocalProxy(lambda: current_app.logger)


def batch_parse():
    """Parse all statfiles in configured directory."""
    errored = 0

    if not os.path.exists(current_app.config['STATS_DIR']):
        logger.debug('!! ERROR: Statfile dir path is invalid. Path used: ' + current_app.config['STATS_DIR'])
        return -1
    files = [f for f in os.listdir(current_app.config['STATS_DIR']) if re.match(r'statistics(-|_)(.*).(txt|json)', f)]
    total_files = len(files)

    print("{0} files to parse, starting...".format(total_files))
    count = 0
    for file in files:
        count += 1
        if count % 250 is 0:  # Let's let the command line know every once in awhile that we're still parsing
            print("Parsing file {0} of {1}".format(count, total_files))
        try:
            parse_file(os.path.join(current_app.config['STATS_DIR'], file))
            shutil.move(os.path.join(current_app.config['STATS_DIR'], file),
                        os.path.join(current_app.config['PROCESSED_DIR'], file))
        except Exception as e:
            if current_app.debug:
                raise e
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.error('!! ERROR: File could not be parsed. Details: \n${0}'
                             .format('\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback))))
                errored += 1
                shutil.move(os.path.join(current_app.config['STATS_DIR'], file),
                            os.path.join(current_app.config['UNPARSABLE_DIR'], file))

    logger.debug('# DEBUG: Batch parsed %r files with %r exceptions.', count, errored)


def parse_file(path: Text):
    """Parse the contents of a CSV statfile."""
    if not os.path.exists(path):
        logger.error('!! ERROR: Tried to parse non-existant path %r', str(path))
        return False
    filename, extension = os.path.splitext(path)
    if extension.lower() == ".json": # noqa
        return jsonparser.parse(path, filename)
    elif extension.lower() == ".txt":
        with open(path) as f:
            contents = f.read()
        return csvparser.parse(contents, os.path.basename(path))
    else:
        raise ValueError('Invalid file type.')
