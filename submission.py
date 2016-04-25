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


def detect_if_bandcamp_submission(html):
    """Return True if submission html is a bandcamp embed submission"""
    return ("""src="https://bandcamp.com/EmbeddedPlayer/""" in html)


def detect_if_youtube_submission(html):
    """Return True if submission html is a youtube embed submission"""
    return ("""src="https://www.youtube.com/embed/""" in html)


def detect_if_googledocs_submission(html):
    """Return True if submission html is a google documents embed submission"""
    #src="https://docs.google.com/document/d/188lEgSsvNCOUQTVGQ465x8gLboOpadegeXEEjqAxDIo/pub?embedded=true" class="content gdoc"
    return ( ("""src="https://docs.google.com/document/""" in html) and ("""class="content gdoc""" in html) )


def save_bandcamp_submission(output_path,submission_number,submission_page_html):
    """
    Download a bandcamp submission
    save to <username>/submission/<submission_number>_<submission_filename.ext>
    and <username>/submission/<submission_number>.html
    """
    logging.debug("Saving bandcamp submission: "+repr(submission_number))
    assert(detect_if_bandcamp_submission(submission_page_html))
    # Find username
    #<h1 id="detail-title" class="pad-left pad-right">... <i>by</i> <a class="username" href="/~silentcicada">Silent Cicada</a>   ... </h1>
    # <i>by</i>\s+<a\s+class="username"\s+href="/~(\w+)">
    """<i>by</i>\s+<a\s+class="username"\s+href="/~(\w+)">"""
    username_search = re.search("""<i>by</i>\s+<a\s+class="username"\s+href="/~(\w+)">""", submission_page_html, re.IGNORECASE)
    username = username_search.group(1)
    # Find submission image
    # <div id="detail-art">
    #    <img src="https://cdn.weasyl.com/static/media/54/69/65/54696582851bc2c17969cd364e555fbe6db792a1d19c6dcb1f715eff89429aeb.png" alt="" style="margin-bottom: 3em">
    #  </div>
    # <div\s+id="detail-art">\s+<img\s+src="([^"'<>\n]+)"
    # https://cdn.weasyl.com/static/media/54/69/65/54696582851bc2c17969cd364e555fbe6db792a1d19c6dcb1f715eff89429aeb.png
    submission_image_link_search = re.search('''<div\s+id="detail-art">\s+<img\s+src="([^"'<>\n]+)"''', submission_page_html, re.IGNORECASE)
    submission_image_link = submission_image_link_search.group(1)
    submission_image = get_url(submission_image_link)
    submission_image_filename = os.path.basename(submission_image_link)
    # Generate local media filepath
    submission_media_path = generate_media_filepath(
        root_path = output_path,
        media_type = "submission",
        media_id = submission_number,
        media_filename = submission_image_filename
        )
    save_file(
        file_path = submission_image_path,
        data = submission_image,
        force_save = True,
        allow_fail = False
        )
    submission_page_path = generate_html_filepath(
        root_path = output_path,
        media_type = "submission",
        media_id = submission_number
        )
    save_file(
        file_path = submission_page_path,
        data = submission_page_html,
        force_save = True,
        allow_fail = False
        )
    return True


def save_submission_google_docs(output_path,submission_number,submission_page_html):
    """
    Save google docs submissions
    """
    assert(detect_if_googledocs_submission(submission_page_html))
    # Generate local html filepath
    submission_page_path = generate_html_filepath(
        root_path = output_path,
        media_type = "submission",
        media_id = submission_number
        )
    save_file(
        file_path = submission_page_path,
        data = submission_page_html,
        force_save = True,
        allow_fail = False
        )
    return True


def save_submission_youtube(output_path,submission_number,submission_page_html):
    """Save youtube embed submissions"""
    assert(detect_if_youtube_submission(submission_page_html))
    # Generate local html filepath
    submission_page_path = generate_html_filepath(
        root_path = output_path,
        media_type = "submission",
        media_id = submission_number
        )
    save_file(
        file_path = submission_page_path,
        data = submission_page_html,
        force_save = True,
        allow_fail = False
        )
    return True


def check_if_dl_skip_is_permitted(submission_number,submission_page_html):
    """Decide if, after failing to find a download link, to keep going as normal"""
    return (
        ('<dt>Category:</dt> <dd>Multimedia' in submission_page_html) and# Media (audio/video) catgory
        ('<dt>Category:</dt> <dd>Visual' not in submission_page_html) and# Visual (Pictures) category
        ('<!-- VISUAL -->' not in submission_page_html) and# submission picture box
        ('<div id="detail-art">' not in submission_page_html) and# Submission media view box
        ('<!-- /detail-art -->' not in submission_page_html) and# Submission media view box
        ('?download">' not in submission_page_html)# Submission download link
        )


def save_submission_tag_history(output_path, submission_number):
    """Save the tag history page sor a given submissionID"""
    logging.debug("Saving tag history page...")
    # Load the tag history page
    # https://www.weasyl.com/submission/tag-history/1245327
    tag_history_page_url = "https://www.weasyl.com/submission/tag-history/"+str(submission_number)
    tag_history_page_html = get_url(tag_history_page_url)
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


def save_submission_normal(output_path,submission_number,submission_page_html):
    """Save regular image and text submissions"""
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
        story_header_data = get_url(story_header_link)
        if not story_header_data:
            raise exception("Failed to load story header image!")
        save_file(
            file_path = story_header_path,
            data = story_header_data,
            force_save = True,
            allow_fail = False
            )
        logging.debug("Saved story header image.")

    # Example download link: <a href="https://cdn.weasyl.com/~tsaiwolf/submissions/1136308/7c1d7ecc303bd165c5198f188617449ff0c4d5a078dbe977edc06078d9c6444c/tsaiwolf-bedtimes-for-fenfen-erect.jpg?download"><span class="icon icon-20 icon-arrowDown"></span> Download</a>
    # Find download link
    download_link_search = re.search("""href="([^"]+weasyl.com/~(\w+)/submissions/[^"]+?download)">""", submission_page_html, re.IGNORECASE)
    if download_link_search:
        submission_media_link = download_link_search.group(1)# 'https://cdn.weasyl.com/~bunny/submissions/9000/1aeeaa6032d590e2f3692cba05ad95ac9090b61098cc720833f88c5abd03ea27/bunny-ashes-badge.png?'

        submission_media = get_url(submission_media_link)
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
    else:
        # Handle lack of download link
        if check_if_dl_skip_is_permitted(submission_number,submission_page_html):
            logging.info("Permitting failure to find download link.")
            appendlist(
                lines = repr(submission_number),
                list_file_path=os.path.join("debug", "submission_linkfind_error.txt"),
                initial_text="# List of submission IDs where download link could not be found.\r\n"
                )
        else:
            logging.error("Could not find download link!")
            raise Exception("Could not find download link!")

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
    return True


def save_submission(output_path, submission_number):
    """Download a submission from weasyl
    save to <username>/submission/<submission_number>_<submission_filename.ext>
    and <username>/submission/<submission_number>.html
    Return True if successful"""
    # Load the submission page
    submission_page_url = "https://www.weasyl.com/submission/"+str(submission_number)
    logging.debug("submission_page_url: "+repr(submission_page_url))
    submission_page_html = get_url(submission_page_url)
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

    # Decide how to handle the submission
    if detect_if_bandcamp_submission(submission_page_html) is True:
        # Handle bandcamp submission
        logging.warning("Submission is bandcamp..")
        save_bandcamp_submission(
            output_path,
            submission_number,
            submission_page_html
            )
    elif detect_if_googledocs_submission(submission_page_html):
        # Handle google docs submission
        logging.warning("Submission is googledocs, only saving html.")
        save_submission_google_docs(
            output_path,
            submission_number,
            submission_page_html
            )
    elif detect_if_youtube_submission(submission_page_html):
        # Handle youtube submission
        logging.warning("Submission is youtube, only saving html.")
        save_submission_youtube(
            output_path,
            submission_number,
            submission_page_html
            )
    else:
        # Handle normal image or story submission
        save_submission_normal(
            output_path,
            submission_number,
            submission_page_html
            )
    # Save the tags
    save_submission_tag_history(output_path, submission_number)
    logging.debug("Finished saving submission_number: "+repr(submission_number))
    return True


def save_submission_range(output_path,start_number,stop_number):
    logging.info("Saving range of submissions:"+repr(start_number)+" to "+repr(stop_number))
    for submission_number in xrange(start_number,stop_number):
        success = save_submission(output_path,submission_number)
        if success:
            appendlist(
                lines = repr(submission_number),
                list_file_path=os.path.join("debug", "submission_success.txt"),
                initial_text="# List of successfully grabbed submission IDs.\r\n"
                )
        else:
            appendlist(
                lines = repr(submission_number),
                list_file_path=os.path.join("debug", "submission_fail.txt"),
                initial_text="# List of failed submission IDs.\r\n"
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
    """Run various test cases"""
    logging.info('running test cases')
    #save_submission(output_path=config.root_path,submission_number=1220462)# text download AND image
    #save_submission(output_path=config.root_path,submission_number=1169192)# text download AND image
    #save_submission(output_path=config.root_path,submission_number=1199683)# text download AND image
    #save_submission(output_path=config.root_path,submission_number=1221326)# googledocs, no download link
    #save_submission(output_path=config.root_path,submission_number=1241596)# youtube, no download link
    save_submission(output_path=config.root_path,submission_number=10118)# bandcamp, no embed
    save_submission(output_path=config.root_path,submission_number=10280)# Friends only
    #save_submission(output_path=config.root_path,submission_number=1241567)# regular image submission
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
