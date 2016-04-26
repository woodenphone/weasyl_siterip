#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     22/04/2016
# Copyright:   (c) User 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import argparse

from utils import * # General utility functions
from weasyl_common import *
import config # Settings and configuration



def detect_if_journal_exists(html):
    """Detect if this is a page for a noxexistant journal"""
    return not (
        ("""<div id="error_content" class="content">""" in html) and
        ("""This journal doesn't seem to be in our database. """ in html)
    )



def save_journal(output_path, journal_number):
    """Download a journal from weasyl
    save to <username>/journal/<journal_number>.html
    Return True if successful"""
    # Load the journal page
    journal_page_url = "https://www.weasyl.com/journal/"+str(journal_number)
    logging.debug("journal_page_url: "+repr(journal_page_url))
    journal_page_html = get_url_requests(journal_page_url)
    if journal_page_html is None:# Handle failure to load page
        logging.error("Could not load journal page!")
        return False
        #raise Exception("Could not load journal page!")

    # Ensure we are logged in
    if detect_if_logged_in(journal_page_html) is False:
        logging.error("Not logged in, not saving page.")
        raise Exception("Not logged in, not saving page.")

    # Ensure the journal exists
    if detect_if_journal_exists(journal_page_html) is False:
        logging.error("Journal does not exist: "+repr(journal_number))
        return False

    # Save the journal page
    journal_page_path = generate_html_filepath(
        root_path = output_path,
        media_type = "journal",
        media_id = journal_number
        )
    logging.debug("journal_page_path: "+repr(journal_page_path))
    save_file(
        file_path = journal_page_path,
        data = journal_page_html,
        force_save = True,
        allow_fail = False
        )
    logging.debug("Finished saving journal_number: "+repr(journal_number))
    return True


def save_journal_range(output_path,start_number,stop_number):
    logging.info("Saving range of journals:"+repr(start_number)+" to "+repr(stop_number))
    for journal_number in xrange(start_number,stop_number):
        success = save_journal(output_path,journal_number)
        if success:
            appendlist(
                lines = repr(journal_number),
                list_file_path=os.path.join("debug", "journal_success.txt"),
                initial_text="# List of successfully grabbed journal IDs.\r\n"
                )
        else:
            appendlist(
                lines = repr(journal_number),
                list_file_path=os.path.join("debug", "journal_fail.txt"),
                initial_text="# List of failed journal IDs.\r\n"
                )
        journal_number += 1
        continue
    logging.info("Finished saving range of journals:"+repr(start_number)+" to "+repr(stop_number))



def cli():
    """Accept command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('start_num', help='low end of the range to work over',
                    type=int)
    parser.add_argument('end_num', help='high end of the range to work over',
                    type=int)
    args = parser.parse_args()
    save_journal_range(
        output_path = config.root_path,
        start_number = args.start_num,
        stop_number = args.end_num
        )
    return


def test():
    """Run various test cases"""
    save_journal_range(
        output_path = config.root_path,
        start_number = 10000,
        stop_number = 10009
        )
    return


def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","weasyl_siterip_journal_log.txt"))
        test()
        #cli()
    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()
