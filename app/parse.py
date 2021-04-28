"""This file handles code for parsing statfiles into the database."""
from __future__ import unicode_literals

import os
import re
import shutil
import sys
import traceback
from typing import Text

from flask import current_app
from werkzeug.local import LocalProxy

from app.parsers import jsonparser

logger = LocalProxy(lambda: current_app.logger)


def batch_parse(app=None):
    """Parse all statfiles in configured directory."""
    errored = 0

    with app.app_context():
        if not os.path.exists(app.config['STATS_DIR']):
            logger.debug('!! ERROR: Statfile dir path is invalid. Path used: ' + app.config['STATS_DIR'])
            return -1
        files = [f for f in os.listdir(app.config['STATS_DIR']) if re.match(r'statistics(-|_)(.*).(txt|json)', f)]
        total_files = len(files)

        logger.debug("{0} files to parse, starting...".format(total_files))
        count = 0
        for file in files:
            count += 1
            if count % 250 is 0:  # Let's let the command line know every once in awhile that we're still parsing
                logger.debug("Parsing file {0} of {1}".format(count, total_files))
            try:
                parse_file(os.path.join(app.config['STATS_DIR'], file))
                shutil.move(os.path.join(app.config['STATS_DIR'], file),
                            os.path.join(app.config['PROCESSED_DIR'], file))
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logger.error('!! ERROR: File could not be parsed. Details: \n${0}'
                            .format('\n'.join(traceback.format_exception(exc_type, exc_value, exc_traceback))))
                errored += 1
                shutil.move(os.path.join(app.config['STATS_DIR'], file),
                            os.path.join(app.config['UNPARSABLE_DIR'], file))
                
                if app.debug:
                    raise e

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
