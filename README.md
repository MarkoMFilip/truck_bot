# Interview bot

This is a small linear interview chat bot, whose purpose is to collect 
information about trucks that the user/client wants to add to their trucking
fleet, and construct a .csv file with the full truck fleet data. In addition, 
the bot will output the content of the conversation in a .txt file for eventual
future analysis. File names of the output data files are generated based on the 
date of conversation, name of the user, and truck fleet ID/designation.

As an additional feature, the script compares the truck brand name that the user
entered with the list of truck manufactureres scrapped from Wikipedia, and 
offers suggestions for correct spelling.


## Prerequisites

* Python >=3.5
* `pandas`
* `bs4` (BeautifulSoup4)


## Versions

The current version of the main script is the final one before I convert it to
OOP paradigm.

#### v1.2
 * Removed former "v1" and renamed "v2" script to just "truck_bot"
 * Exchanged the hack from former "v2" script with calls to global variables

#### v1.1
 * Introduced capability for recognizing and correcting truck brands from user 
input. If the user enters a brand whose name does not match something from 
the list, the script will offer a suggestion.
 * Various bug fixes.


## Example data

I have included the `data` folder with four example data sets: one where the 
user just follows the instructions in a straightforward manner ("ABC123"), one
where the user has corrected several entries ("HansKristian"), one where the 
user interrupted the script mid-way ("Interrupting"), and one where user quit
in the very first line ("user87926").


## Notes

There are several assumptions I made in the script for the sake of expediency.
All of them can be expanded or fixed as needed.

Domain-related
 * It is assumed that every fleet will have a separate ID/designation. There are
no limitations on which characters this designation can contain, which might
introduce problems when constructing file names for save data.
 * It is assumed that truck model has a very precise pattern for the name: two
letters, followed by space, followed by a series of numbers. This is most 
certainly not the case in reality, and was introduced here just for the sake of
expediency.

Code-related
 * The script assumes that `data` folder already exists, and that its path is 
fixed.
 * There is no unit conversion if users want to use for example liters instead
of cubic centimeters for engine capacity.
 * There is no conversion of values entered as a text (e.g. "thirty five") to
numbers ("35"). When asked for values, numbers must be given.

