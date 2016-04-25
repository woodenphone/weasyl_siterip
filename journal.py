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
from utils import * # General utility functions
from weasyl_common import *
import config # Settings and configuration


# Journal specific
def detect_if_journal_exists(html):
    """Detect if this is a page for a noxexistant submission"""
    journal_exists = True# If no test fails, assume true
    if """<div id="error_content" class="content">""" in html:
        if """This journal doesn't seem to be in our database. """ in html:
            journal_exists = False
    return journal_exists


def save_journal(output_path, journal_number):
    """Download a journal from weasyl
    save to <username>/journal/<journal_number>.html
    Return True if successful"""
    # Load the journal page
    journal_page_url = "https://www.weasyl.com/journal/"+str(journal_number)
    logging.debug("journal_page_url: "+repr(journal_page_url))
    journal_page_html = get_url(journal_page_url)
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
        save_journal(output_path,journal_number)
        journal_number += 1
    logging.info("Finished saving range of journals:"+repr(start_number)+" to "+repr(stop_number))
# /Journal specific




def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","weasyl_siterip_journal_log.txt"))
        save_journal_range(
            output_path = config.root_path,
            start_number = 10000,
            stop_number = 10009
            )
    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()
