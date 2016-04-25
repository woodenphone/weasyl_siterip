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



# Character specific
def detect_if_character_exists(html):
    """Detect if this is a page for a noxexistant submission"""
    journal_exists = True# If no test fails, assume true
    if """<div id="error_content" class="content">""" in html:
        if """This character doesn't seem to be in our database.""" in html:
            journal_exists = False
    return journal_exists


def save_character(output_path, character_number):
    """Download a character from weasyl
    save to <username>/character/<character_number>_<character_filename.ext>
    and <username>/character/<character_number>.html
    Return True if successful"""
    # Load the character page
    character_page_url = "https://www.weasyl.com/character/"+str(character_number)
    logging.debug("character_page_url: "+repr(character_page_url))
    character_page_html = get_url(character_page_url)
    if character_page_html is None:# Handle failure to load page
        logging.error("Could not load character page!")
        return False

    # Ensure we are logged in
    if detect_if_logged_in(character_page_html) is False:
        logging.error("Not logged in, not saving page")
        raise Exception("Not logged in, not saving page")

    # Ensure the character exists
    if detect_if_character_exists(character_page_html) is False:
        logging.error("character does not exist: "+repr(character_number))
        return False

    # Example download link: <a href="https://cdn.weasyl.com/static/character/5e/b8/d1/bc/43/dc/kaysimagination-58267.submit.112489.png"><span class="icon icon-20 icon-arrowDown"></span> Download</a>
    # Find download link
    download_link_search = re.search("""<a\shref="([^"]+.weasyl.com/static/character/[^"]+)">""", character_page_html, re.IGNORECASE)
    character_media_link = download_link_search.group(1)
    logging.debug("character_media_link: "+repr(character_media_link))
    # Open the download link
    character_media = get_url(character_media_link)
    if character_media is None:
        logging.error("Could not load character media!")
        raise Exception("Could not load character media!")
        #return False
    # Find the fileename to save the media as
    media_filename_search = re.search("""/([^"/?]+)$""", character_media_link, re.IGNORECASE)
    media_filename = media_filename_search.group(1)

    character_media_path = generate_media_filepath(
        root_path = output_path,
        media_type = "character",
        media_id = submission_number,
        media_filename = media_filename
        )

    logging.debug("character_media_path: "+repr(character_media_path))
    # Save the character media before page
    save_file(
        file_path = character_media_path,
        data = character_media,
        force_save = True,
        allow_fail = False
        )

    # Save the character page
    character_page_path = generate_html_filepath(
        root_path = output_path,
        media_type = "character",
        media_id = character_number
        )
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


def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","weasyl_siterip_character_log.txt"))
        save_character_range(
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
