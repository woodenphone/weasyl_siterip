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



def detect_if_submission_exists(html):
    """Detect if this is a page for a noxexistant submission"""
    submission_exists = True# If no test fails, assume we're logged in
    if """<div id="error_content" class="content">""" in html:
        if """This submission doesn't seem to be in our database.""" in html:
            submission_exists = False
    return submission_exists


def detect_if_friends_only(html):
    """Detect if a submission page is restricted to friends of the uploader"""
    return(
        ('This page contains content that you cannot view because the page owner has allowed only friends to access it.' in html) and
        ('?download">' not in html)# Submission download link
        )


def detect_submission_category(html):
    """Figure out the category of the submission.
    Possible types:
        'multimedia' - Audio/video/swf
        'literary' - .txt/.md/.pdf/google drive (Can also have a header image)
        'visual' - Pictures
    """
    if '<dt>Category:</dt> <dd>Multimedia' in html:
        return 'multimedia'
    elif '<dt>Category:</dt> <dd>Literary' in html:
        return 'literary'
    elif '<dt>Category:</dt> <dd>Visual' in html:
        return 'visual'
    else:
        raise Exception('Cannot determine submission category!')


def save_submission_tag_history(output_path, submission_number):
    """Save the tag history page sor a given submissionID"""
    logging.debug("Saving tag history page...")
    # Load the tag history page
    # https://www.weasyl.com/submission/tag-history/1245327
    tag_history_page_url = "https://www.weasyl.com/submission/tag-history/"+str(submission_number)
    tag_history_page_html = get_url_requests(tag_history_page_url)
    if tag_history_page_html is None:
        # Handle failure to load page. Since we grab tag history last, we expect this page to exist.
        logging.error("Could not load tag history page!")
        raise Exception("Could not load tag history page!")

    # Ensure we are logged in
    if detect_if_logged_in(tag_history_page_html) is False:
        logging.error("Not logged in, not saving page.")
        raise Exception("Not logged in, not saving page.")

    # Save the HTML
    tag_history_filepath = generate_tag_history_filepath(
        root_path = output_path,
        media_type = "submission",
        media_id = submission_number
        )
    save_file(
        file_path = tag_history_filepath,
        data = tag_history_page_html,
        force_save = True,
        allow_fail = False
        )
    logging.debug("Saved tag history page to: %s" % (tag_history_filepath))
    return True


def save_story_header_image(output_path, submission_number, submission_page_html):
    """Try to save the story header image if it exists. Return True for success, False for failed."""
    # Save story header image if it exists
    story_header_search = re.search('<div\sid="detail-art">\s+<img\ssrc="([^"]+)"\salt=', submission_page_html, re.IGNORECASE)
    if story_header_search:
        story_header_link = story_header_search.group(1)
        logging.debug("story_header_link: "+repr(story_header_link))
        # Get the filename + filepath
        story_header_filename_search = re.search("""/([^"/?]+)$""", story_header_link, re.IGNORECASE)
        story_header_filename = story_header_filename_search.group(1)
        story_header_path = generate_media_filepath(
            root_path = output_path,
            media_type = "submission",
            media_id = submission_number,
            media_filename = story_header_filename
            )
        # Save the image
        story_header_data = get_url_requests(story_header_link)
        if not story_header_data:
            # Handle specific case where a image is broken.
            if int(submission_number) in [
                41511,# 'https://cdn.weasyl.com/static/submission/23/82/b5/f4/9b/fe/41511.cover.png'
                ]:
                logging.error('Permitting failure to save image for known error case: %s' % (submission_number))
                return False
            else:
                raise Exception("Failed to load story header image!")
        save_file(
            file_path = story_header_path,
            data = story_header_data,
            force_save = True,
            allow_fail = False
            )
        logging.debug("Saved story header image.")
        return True
    return False


def save_download_link(output_path, submission_number, submission_page_html):
    """Try to save the submission download link if it exists. Return True for success, False for failed."""
    # Attempt to save download link if it exists
    # Example download link: <a href="https://cdn.weasyl.com/~tsaiwolf/submissions/1136308/7c1d7ecc303bd165c5198f188617449ff0c4d5a078dbe977edc06078d9c6444c/tsaiwolf-bedtimes-for-fenfen-erect.jpg?download"><span class="icon icon-20 icon-arrowDown"></span> Download</a>
    # Find download link
    download_link_search = re.search("""href="([^"]+weasyl.com/~(\w+)/submissions/[^"]+?download)">""", submission_page_html, re.IGNORECASE)
    if download_link_search:
        submission_media_link = download_link_search.group(1)# 'https://cdn.weasyl.com/~bunny/submissions/9000/1aeeaa6032d590e2f3692cba05ad95ac9090b61098cc720833f88c5abd03ea27/bunny-ashes-badge.png?'

        submission_media = get_url_requests(submission_media_link)
        if submission_media is None:
            logging.error("Could not load submission media!")
            raise Exception("Could not load submission media!")

        # Find the fileename to save the media as
        media_filename_search = re.search("""/([^"/?]+)\?download$""", submission_media_link, re.IGNORECASE)
        media_filename = media_filename_search.group(1)

        # Generate local media filepath
        submission_media_path = generate_media_filepath(
            root_path = output_path,
            media_type = "submission",
            media_id = submission_number,
            media_filename = media_filename
            )
        logging.debug("submission_media_path: "+repr(submission_media_path))

        # Save the submission media before page
        save_file(
            file_path = submission_media_path,
            data = submission_media,
            force_save = True,
            allow_fail = False
            )
        return True
    return False


def save_submission(output_path, submission_number):
    """Download a submission from weasyl
    save to <username>/submission/<submission_number>_<submission_filename.ext>
    and <username>/submission/<submission_number>.html
    Return True if successful"""
    # Load the submission page
    submission_page_url = "https://www.weasyl.com/submission/"+str(submission_number)
    logging.debug("submission_page_url: "+repr(submission_page_url))
    submission_page_html = get_url_requests(submission_page_url)
    if submission_page_html is None:# Handle failure to load page
        logging.error("Could not load submission page!")
        return False# Some submissionIDs are invalid and return a 404
        #raise Exception("Could not load submission page!")

    # Ensure we are logged in
    if detect_if_logged_in(submission_page_html) is False:
        # We should ALWAYS be logged in
        logging.error("Not logged in, not saving page.")
        raise Exception("Not logged in, not saving page.")

    # Detect if sumbission is noexistant
    if detect_if_submission_exists(submission_page_html) is False:
        logging.error("Submission does not exist.")
        return False# Some submissionIDs are invalid and return a 404

    # Detect if restricted to friends only
    if detect_if_friends_only(submission_page_html):
        logging.error("Submission is restricted to friends of the uploader")
        return False

    # Initialise variables used to record if we saved various things that could be on the page
    saved_story_header_image = False
    saved_download_link = False

    # Try downloading each kind of thing we want to save
    saved_story_header_image = save_story_header_image(output_path, submission_number, submission_page_html)
    saved_download_link = save_download_link(output_path, submission_number, submission_page_html)

    # Check that expected response for the page type occured
    submission_category = detect_submission_category(submission_page_html)
    if submission_category == 'visual':
        assert(saved_download_link)# We should always get a download link with visual submissions
    elif submission_category == 'literary':
        # Literary submissions can be offsite and have not download link, and story header images are optional
        pass
    elif submission_category == 'multimedia':
        # Multimedia submissions can be offsite, and the accompianing picture is optional
        pass

    # Save the tags
    save_submission_tag_history(output_path, submission_number)

    # Save the submission page last
    # Generate local html filepath
    submission_page_path = generate_html_filepath(
        root_path = output_path,
        media_type = "submission",
        media_id = submission_number
        )
    # Save the submission page HTML
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
        logging.info("Saving submissionID %s" % (submission_number))
        success = save_submission(output_path,submission_number)
        appendlist(
                lines = 't: %s, id: %s, r: %s' % (repr(time.time()), repr(submission_number), repr(success)),#  str(datetime.datetime.now()),
                list_file_path=os.path.join("debug", "submission_stats.txt"),
                initial_text="# time: UNIXTIME, id: ITEM_NUMBER, r: SUCCESS IDs.\r\n"
                )
        submission_number += 1
        continue
    logging.info("Finished saving range of submissions:"+repr(start_number)+" to "+repr(stop_number))


def cli():
    """Accept command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('start_num', help='low end of the range to work over',
                    type=int)
    parser.add_argument('end_num', help='high end of the range to work over',
                    type=int)
    args = parser.parse_args()
    save_submission_range(
        output_path = config.root_path,
        start_number = args.start_num,
        stop_number = args.end_num
        )
    return


def test():
    """Run various test cases.
    HINT: Wipe the download folder so you get clean results."""
    logging.info('running test cases')
    save_submission(output_path=config.root_path,submission_number=11931)# Crashed?
    save_submission(output_path=config.root_path,submission_number=1220462)# text download AND image
    save_submission(output_path=config.root_path,submission_number=1169192)# text download AND image
    save_submission(output_path=config.root_path,submission_number=1199683)# text download AND image
    save_submission(output_path=config.root_path,submission_number=1221326)# googledocs, no download link
    save_submission(output_path=config.root_path,submission_number=1241596)# youtube, no download link
    save_submission(output_path=config.root_path,submission_number=10118)# bandcamp, no embed
    save_submission(output_path=config.root_path,submission_number=10280)# Friends only
    save_submission(output_path=config.root_path,submission_number=1241567)# regular image submission
##    save_submission_range(
##        output_path = config.root_path,
##        start_number = 10000,
##        stop_number = 10099
##        )
    logging.info('finished test cases')
    return


def main():
    try:
        setup_logging(log_file_path=os.path.join("debug","weasyl_siterip_submission_log.txt"))
        #test()
        cli()
    except Exception, e:# Log fatal exceptions
        logging.critical("Unhandled exception!")
        logging.exception(e)
    return


if __name__ == '__main__':
    main()
