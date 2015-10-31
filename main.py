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
import sqlalchemy
import logging
from bs4 import BeautifulSoup# http://www.crummy.com/software/BeautifulSoup/bs4/doc/
import re

from utils import * # General utility functions
import config # Settings and configuration






def detect_if_logged_in(html):
    """Detect if we were logged in in this page"""
    is_logged_in = True# If no test fails, assume we're logged in
    if """<h3 id="header-guest">""" in html:
        # <h3 id="header-guest"> is used to show the login prompt
        is_logged_in = False
    return is_logged_in

# Submission specific
def detect_if_submission_exists(html):
    """Detect if this is a page for a noxexistant submission"""
    submission_exists = True# If no test fails, assume we're logged in
    if """<div id="error_content" class="content">""" in html:
        if """This submission doesn't seem to be in our database.""" in html:
            submission_exists = False
    return submission_exists


def save_submission(output_path,submission_number):
    """Download a submission from weasyl
    save to <username>/submission/<submission_number>_<submission_filename.ext>
    Return True if successful"""
    # Load the submission page
    submission_page_url = "https://www.weasyl.com/submission/"+str(submission_number)
    logging.debug("submission_page_url: "+repr(submission_page_url))
    submission_page_html = get_url(submission_page_url)
    if submission_page_html is None:# Handle failure to load page
        logging.error("Could not load submission page!")
        return False
    # Ensure we are logged in
    if detect_if_logged_in(submission_page_html) is False:
        logging.error("Not logged in, not saving page.")
        return False
    # Detect if sumbission is noexistant
    if detect_if_submission_exists(submission_page_html) is False:
        logging.error("Submission does not exist.")
        return False

    # Example download link: <a href="https://cdn.weasyl.com/~tsaiwolf/submissions/1136308/7c1d7ecc303bd165c5198f188617449ff0c4d5a078dbe977edc06078d9c6444c/tsaiwolf-bedtimes-for-fenfen-erect.jpg?download"><span class="icon icon-20 icon-arrowDown"></span> Download</a>
    # Find download link
    download_link_search = re.search("""href="([^"]+weasyl.com/~(\w+)/submissions/[^"]+?download)">""", submission_page_html, re.IGNORECASE)
    submission_media_link = download_link_search.group(1)# 'https://cdn.weasyl.com/~bunny/submissions/9000/1aeeaa6032d590e2f3692cba05ad95ac9090b61098cc720833f88c5abd03ea27/bunny-ashes-badge.png?'
    username = download_link_search.group(2) # tsaiwolf
    logging.debug("submission_media_link: "+repr(submission_media_link))
    logging.debug("username: "+repr(username))
    submission_media = get_url(submission_media_link)
    if submission_media is None:
        logging.error("Could not load submission media!")
        return False
    # Find the fileename to save the media as
    media_filename_search = re.search("""/([^"/?]+)\?download$""", submission_media_link, re.IGNORECASE)
    media_filename = media_filename_search.group(1)
    local_media_filename = str(submission_number)+"_"+media_filename
    submission_media_path = os.path.join(output_path, username, "submission", local_media_filename)
    logging.debug("submission_media_path: "+repr(submission_media_path))
    # Save the submission media before page
    save_file(
        file_path = submission_media_path,
        data = submission_media,
        force_save = True,
        allow_fail = False
        )

    # Save the submission page last
    submission_page_path = os.path.join(output_path, username, "submission", str(submission_number)+".html")
    save_file(
        file_path = submission_page_path,
        data = submission_page_html,
        force_save = True,
        allow_fail = False
        )
    logging.debug("Finished saving submission_number: "+repr(submission_number))
    return True


def save_submission_range(output_path,start_number,stop_number):
    logging.info("Saving range of submissions:"+repr(start_number)+" to "+repr(stop_number))
    for submission_number in xrange(start_number,stop_number):
        save_submission(output_path,submission_number)
        submission_number += 1
    logging.info("Finished saving range of submissions:"+repr(start_number)+" to "+repr(stop_number))
# /Submission specific


# Journal specific
def detect_if_journal_exists(html):
    """Detect if this is a page for a noxexistant submission"""
    journal_exists = True# If no test fails, assume true
    if """<div id="error_content" class="content">""" in html:
        if """This journal doesn't seem to be in our database. """ in html:
            journal_exists = False
    return journal_exists


def save_journal(output_path, journal_number):
    """foo"""
    # Load the journal page
    journal_page_url = "https://www.weasyl.com/journal/"+str(journal_number)
    logging.debug("journal_page_url: "+repr(journal_page_url))
    journal_page_html = get_url(journal_page_url)
    if journal_page_html is None:# Handle failure to load page
        logging.error("Could not load journal page!")
        return False
    # Ensure we are logged in
    if detect_if_logged_in(journal_page_html) is False:
        logging.error("Not logged in, not saving page.")
        return False
    # Ensure the journal exists
    if detect_if_journal_exists(journal_page_html) is False:
        logging.error("Journal does not exist: "+repr(journal_number))
        return False

    # Find the username
    # <a class="username" href="/~dyyor">Dyyor</a>
    username_search = re.search("""<a\sclass="username"\shref="/~([^"<>/]+)">[^"<>/]+</a>""", journal_page_html, re.IGNORECASE)
    username = username_search.group(1)
    # Save the journal page
    journal_page_path = os.path.join(output_path, username, "journal", str(journal_number)+".html")
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



# Character specific
def detect_if_character_exists(html):
    """Detect if this is a page for a noxexistant submission"""
    journal_exists = True# If no test fails, assume true
    if """<div id="error_content" class="content">""" in html:
        if """This character doesn't seem to be in our database.""" in html:
            journal_exists = False
    return journal_exists


def save_character(output_path, character_number):
    """foo"""
    # Load the journal page
    character_page_url = "https://www.weasyl.com/character/"+str(character_number)
    logging.debug("character_page_url: "+repr(character_page_url))
    character_page_html = get_url(character_page_url)
    if character_page_html is None:# Handle failure to load page
        logging.error("Could not load journal page!")
        return False
    # Ensure we are logged in
    if detect_if_logged_in(character_page_html) is False:
        logging.error("Not logged in, not saving page")
        return False
    # Ensure the journal exists
    if detect_if_character_exists(character_page_html) is False:
        logging.error("Journal does not exist: "+repr(character_number))
        return False

    # Find the username
    # <a class="username" href="/~dyyor">Dyyor</a>
    username_search = re.search("""<a\sclass="username"\shref="/~([^"<>/]+)">[^"<>/]+</a>""", character_page_html, re.IGNORECASE)
    username = username_search.group(1)

    # Example download link: <a href="https://cdn.weasyl.com/static/character/5e/b8/d1/bc/43/dc/kaysimagination-58267.submit.112489.png"><span class="icon icon-20 icon-arrowDown"></span> Download</a>
    # Find download link
    download_link_search = re.search("""<a\shref="([^"]+.weasyl.com/static/character/[^"]+)">""", character_page_html, re.IGNORECASE)
    character_media_link = download_link_search.group(1)# 'https://cdn.weasyl.com/~bunny/submissions/9000/1aeeaa6032d590e2f3692cba05ad95ac9090b61098cc720833f88c5abd03ea27/bunny-ashes-badge.png?'
    logging.debug("character_media_link: "+repr(character_media_link))
    character_media = get_url(character_media_link)
    if character_media is None:
        logging.error("Could not load character media!")
        return False
    # Find the fileename to save the media as
    media_filename_search = re.search("""/([^"/?]+)$""", character_media_link, re.IGNORECASE)
    media_filename = media_filename_search.group(1)
    local_media_filename = str(character_number)+"_"+media_filename
    character_media_path = os.path.join(output_path, username, "character", local_media_filename)
    logging.debug("character_media_path: "+repr(character_media_path))
    # Save the character media before page
    save_file(
        file_path = character_media_path,
        data = character_media,
        force_save = True,
        allow_fail = False
        )

    # Save the character page
    character_page_path = os.path.join(output_path, username, "character", str(character_number)+".html")
    logging.debug("character_page_path: "+repr(character_page_path))
    save_file(
        file_path = character_page_path,
        data = character_page_html,
        force_save = True,
        allow_fail = False
        )
    logging.debug("Finished saving character_number: "+repr(character_number))
    return True


def save_character_range(output_path,start_number,stop_number):
    logging.info("Saving range of characters:"+repr(start_number)+" to "+repr(stop_number))
    for character_number in xrange(start_number,stop_number):
        save_character(output_path,character_number)
        character_number += 1
    logging.info("Finished saving range of characters:"+repr(start_number)+" to "+repr(stop_number))
# /Character specific


# Debug
def explore_json():
    """Debug"""
    json_data = read_file(os.path.join("notes","6404920.json"))
    json_obj = json.loads(json_data)
    logging.debug("json_obj: "+repr(json_obj))
    return


def debug():
    """where stuff is called to debug and test"""
    output_path="output"
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
    # Save a range of characters
    save_character_range(
        output_path,
        start_number=(58267-100),
        stop_number=58267
        )
    return
# /Debug


def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","pysagi-log.txt"))
        #run()
        debug()
    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()
