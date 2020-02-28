# Interview bot

This is an example of a small linear interview bot, used to collect information
about trucks within a trucking fleet. After the interaction with the user it
saves all the fleet data in a .csv file, and the content of the conversation in 
a .txt. file. File names are generated based on the date of conversation, name
of the user, and truck fleet ID/designation.


## Prerequisites

Due to use of type annotations, Python 3.5 or higher is needed to run the script
correctly.
Of non-standard libraries, only `pandas` is needed.


## Versions

I have included two versions of the same bot in this repository. The first one, 
`truck_bot_v1.py`, is much cleaner and works as intended, except that it doesn't
save conversation information if the user quits the script before it naturally
ends. I have fixed this problem in `truck_bot_v2.py`, however the hacks I 
introduced in order to have this functionality are... not the best.


## Example data

I have included the `data` folder with two example data sets, one with both 
.csv and .txt files that resulted from the use of `truck_bot_v1.py`, and the 
other with just a .txt. file which demonstrated the enhanced quit functionality
of `truck_bot_v2.py`.


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

