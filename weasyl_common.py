#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     17/07/2015
# Copyright:   (c) User 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import logging
import re

from utils import * # General utility functions
import config # Settings and configuration





def generate_media_filepath(root_path, media_type, media_id, media_filename):
    """root/type/millions/thousands/id.filename"""
    padded_id_string = str(media_id).zfill(9)
    millions_section = padded_id_string[0:3]
    thousands_section = padded_id_string[3:6]
    filename = '%s.%s' % (media_id, media_filename)
    file_path = os.path.join(
        root_path, media_type, millions_section, thousands_section, filename
        )
    return file_path


def generate_html_filepath(root_path, media_type, media_id):
    """root/type/millions/thousands/id.filename"""
    padded_id_string = str(media_id).zfill(9)
    millions_section = padded_id_string[0:3]
    thousands_section = padded_id_string[3:6]
    filename = '%s.html' % (media_id)
    file_path = os.path.join(
        root_path, media_type, millions_section, thousands_section, filename
        )
    return file_path


def generate_tag_history_filepath(root_path, media_type, media_id):
    """root/type/millions/thousands/id.filename"""
    padded_id_string = str(media_id).zfill(9)
    millions_section = padded_id_string[0:3]
    thousands_section = padded_id_string[3:6]
    filename = '%s.tag_history.html' % (media_id)
    file_path = os.path.join(
        root_path, media_type, millions_section, thousands_section, filename
        )
    return file_path


def detect_if_logged_in(html):
    """Detect if we were logged in in this page"""
    is_logged_in = True# If no test fails, assume we're logged in
    if """<h3 id="header-guest">""" in html:
        # <h3 id="header-guest"> is used to show the login prompt
        is_logged_in = False
    return is_logged_in












# Debug
def debug():
    """where stuff is called to debug and test"""
    output_path=config.root_path
##    # Generic low-numbered submission
##    save_submission(
##        output_path,
##        submission_number=9000
##        )
##    # Generic age-restricted submission
##    save_submission(
##        output_path,
##        submission_number=1136308
##        )
    # Audio submission that we crashed on (bandcamp)
    save_submission(
        output_path,
        submission_number=1136234
        )
    # Video submission (youtube)
    # https://www.weasyl.com/submission/1136032/laughing-zombie
    save_submission(
        output_path,
        submission_number=1136032
        )
##    # Save a range of submissions
##    save_submission_range(
##        output_path,
##        start_number=(1136308-100),
##        stop_number=1136308
##        )
##    # Save a single journal
##    save_journal(
##        output_path,
##        journal_number=97129
##        )
##    # Save a range of journals
##    save_journal_range(
##        output_path,
##        start_number=(97129-100),
##        stop_number=97129
##        )
##    # Save a single character
##    save_character(
##        output_path,
##        character_number=58267
##        )
##    # Save a range of characters
##    save_character_range(
##        output_path,
##        start_number=(58267-100),
##        stop_number=58267
##        )
##    return
# /Debug


def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","weasyl_siterip-log.txt"))
        debug()
    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()
