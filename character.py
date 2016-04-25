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




def detect_if_character_exists(html):
    """Detect if this is a page for a noxexistant submission"""
    return not (
        ("""<div id="error_content" class="content">""" in html) and
        ("""This character doesn't seem to be in our database.""" in html)
    )



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
        sucess = save_character(output_path,character_number)
        if success:
            appendlist(
                lines = repr(submission_number),
                list_file_path=os.path.join("debug", "character_success.txt"),
                initial_text="# List of successfully grabbed character IDs.\r\n"
                )
        else:
            appendlist(
                lines = repr(submission_number),
                list_file_path=os.path.join("debug", "character_fail.txt"),
                initial_text="# List of failed character IDs.\r\n"
                )
        character_number += 1
        continue
    logging.info("Finished saving range of characters:"+repr(start_number)+" to "+repr(stop_number))



def cli():
    """Accept command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('start_num', help='low end of the range to work over',
                    type=int)
    parser.add_argument('end_num', help='high end of the range to work over',
                    type=int)
    args = parser.parse_args()
    save_character_range(
        output_path = config.root_path,
        start_number = args.start_num,
        stop_number = args.end_num
        )
    return

def test():
    """Run various test cases"""
    save_character_range(
        output_path = config.root_path,
        start_number = 10000,
        stop_number = 10009
        )
    return


def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","weasyl_siterip_character_log.txt"))
        cli()
    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()
