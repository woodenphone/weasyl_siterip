weasyl_siterip
Python scraper for weasyl



Note:
Bandcamp submissions will only have the HTML of their page saved.



Usage:
Set up an account on weasyl
Enable all mature submissions in site options
Generate an API key on site
put API key from site into config file


Output paths:

<username>/submission/<submission_number>.html
<username>/submission/<submission_number>_<submission_filename.ext>

<username>/journal/<journal_number>.html

<username>/character/<character_number>_<character_filename.ext>
<username>/character/<character_number>.html




List of page types:

Submission (normal):
Image submission, primary target
Save download link and page HTML
Output paths:
<username>/submission/<submission_number>.html
<username>/submission/<submission_number>_<submission_filename.ext>


Submission(bandcamp):
Audio submission hosted externally on bandcamp
Save page HTML only
possibly has weasyl-hosted image too?
Output paths:
<username>/submission/<submission_number>.html
<username>/submission/<submission_number>_<submission_filename.ext>

Journal (normal):
Save page HTML only
Output paths:
<username>/journal/<journal_number>.html

Character:
save download link and page HTML, similar to image submission
Output paths:
<username>/character/<character_number>_<character_filename.ext>
<username>/character/<character_number>.html

User:
User page, not supported yet
Avatar and page HTML
Output paths:
None so far.




Files:
utils.py - General utility functions
config.py - Settings and configuration

"debug/" can be safely deleted whenever the program is not running.

tests/bandcamp_submission_true_1.htm - Example of a bandcamp submission
tests/youtube_submission_true_1.htm - Example of a youtube submission


