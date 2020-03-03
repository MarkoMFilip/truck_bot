import os
import re
import sys
import time
import random
import pandas as pd
from datetime import datetime
from typing import Tuple, List, Callable


# ----------------------------------------------------------------------------------------------------------------------
#                                                 HELPER FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def ask(question: str, conv: List) -> Tuple[str, List]:
    """
    Wrapper function for asking the question. It will record the question and the answer in the ongoing conversation
    list variable. Also, if it detects that the user entered a quit keyword, it will exit the program without further
    prompt.

    Inputs
    :param question: question to ask user
    :param conv: ongoing conversation list

    Outputs
    :return: user's input, ongoing conversation list
    """
    statement = input(question)

    # Write the input into the ongoing conversation list
    conv.append('Bot: ' + question)
    conv.append('Customer: ' + statement)

    # Check if quit signal was sent
    check_quit(statement, conv)

    return statement, conv


def say(input_msg: str, conv: List) -> List:
    """
    Wrapper function for saying something to the user. It will print the input message to the terminal, and record it in
    the ongoing conversation list variable.

    Inputs
    :param input_msg: message to the user
    :param conv: ongoing conversation list

    Output
    :return: ongoing conversation list
    """
    # Print the statement
    print(input_msg)

    # Memorize it in the conversation list
    conv.append('Bot: ' + input_msg)

    return conv


def check_quit(statement: str, conv: List):
    """
    Quits the program if user input is 'q' or 'quit'.

    Input
    :param statement: user input
    :param conv: ongoing conversation list
    """
    if any([statement.lower() == x for x in ['q', 'quit']]):
        save_conv(conv, flag='quit')
        sys.exit(0)


def negative_answer(statement: str) -> bool:
    """
    Just a shorthand function for determining whether the user typed in a negative answer.

    Inputs
    :param statement: user input

    Outputs
    :return: boolean determining whether the user input is negative
    """
    return any([statement.lower() == x for x in ['n', 'no', 'not']])


def save_fleet(fleet: pd.DataFrame, conv: List):
    """
    Saves the fleet data in the designated folder as a cvs file.
    NOTE: assumes that the save folder already exists!

    Inputs
    :param fleet: pandas DataFrame that holds the fleet information
    :param conv: ongoing conversation list
    """
    fleet_path = conv[0]
    fleet.to_csv(fleet_path)


def save_conv(conv: List, flag: str = ''):
    """
    Saves the conversation data in the designated folder as a txt file.
    NOTE: assumes that the save folder already exists!

    Inputs
    :param conv: ongoing conversation list
    :param flag: flag to write additional information to the file; e.g. if the user quit the conversation
    """
    conv_path = conv[1]
    with open(conv_path, 'x') as conv_file:
        for line in conv[2:]:
            conv_file.write('{0}\n'.format(line))
        if flag == 'quit':
            conv_file.write('Customer has quit!\n')


# ----------------------------------------------------------------------------------------------------------------------
#                                                 FLEET FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def get_basic_info(data_path: str, conv: List) -> Tuple[str, str, List]:
    """
    From the basic info and the current date, constructs the base of the file name that will be used for storing the
    fleet data and the conversation history.

    NOTE: there is a nasty hack in this function, which stores data save path, and names of fleet and conversation save
    files as the first three items in the conversation list. This became necessary when I discovered that I forgot to
    implement saving the conversation in case when the user decides to quit the script during runtime. This can be
    implemented much more elegantly, but for the sake of expediency I'm just putting it here like this.

    Inputs
    :param data_path: folder path where data is stored; NOTE: this is part of the hack
    :param conv: ongoing conversation list

    :return: name of the current user, ID/designation of the fleet, and the ongoing conversation list
    """
    # Get the current date and form a string out of it
    today = '{0}'.format(datetime.date(datetime.now()))

    # NOTE: the following is a temporary fix for a save&quit bug! See commit log for details
    # Generate a temporary username and fleet_id
    rand = random.randint(1, 100000)
    username = 'user' + str(rand)
    fleet_id = 'fleet' + str(rand)
    conv_path = os.path.join(data_path, '_-_'.join([today, username, fleet_id, 'conversation.txt']))
    fleet_path = os.path.join(data_path, '_-_'.join([today, username, fleet_id, 'fleetdata.csv']))
    conv.insert(0, fleet_path)
    conv.insert(1, conv_path)

    # Start by getting the basic information: name, fleet designation
    username, conv = ask('Please tell me your name: ', conv)
    fleet_id, conv = ask('What is the designation of this fleet? ', conv)

    # If the username or the fleet ID contain spaces, remove them
    username = ''.join(username.split(' '))
    fleet_id = ''.join(fleet_id.split(' '))

    # Construct the base file name
    fn_base = '_-_'.join([today, username, fleet_id])

    # NOTE: the following lines are part of the hack
    fleet_suffix = '_-_fleetdata.csv'
    conv_suffix = '_-_conversation.txt'
    fleet_path = os.path.join(data_path, fn_base+fleet_suffix)  # construct the fleet file path
    conv_path = os.path.join(data_path, fn_base+conv_suffix)  # construct the conversation file path
    conv[0] = fleet_path
    conv[1] = conv_path

    # Output the data
    return username, fleet_id, conv


def get_input(input_msg: str, criterion: Callable, err_msg: str, conv: List) -> Tuple[str, List]:
    """
    Prompt the user for the input, check if it corresponds to the designated criterion, and if not prompt the user again
    but now by printing an error message.

    Inputs:
    :param input_msg: original message to the user, prompting for input
    :param criterion: criterion that user input needs to pass
    :param err_msg: error message to the user if the input does not pass the criterion
    :param conv: ongoing conversation list

    Outputs:
    :return: user input, verified against the criterion
    """
    # Ask the user for input
    statement, conv = ask(input_msg, conv)

    # Check if the input is correct
    try:
        assert criterion(statement)
    except AssertionError:
        statement, conv = get_input(err_msg, criterion, err_msg, conv)  # repeat until the user gets it or quits

    # Return this piece of conversation and the user input
    return statement, conv


def get_single_truck(truck_nr: int, conv: List) -> Tuple[pd.Series, List]:
    """
    Collects all the relevant information about a single truck in the fleet and returns it in pandas Series.

    Inputs:
    :param truck_nr: number of the truck in the fleet
    :param conv: ongoing conversation list

    Outputs
    :return: pandas Series with truck information, ongoing conversation list
    """
    conv = say('\nPlease provide details for vehicle nr. {0}.'.format(truck_nr), conv)

    # Get truck name
    input_msg = 'Brand: '
    criterion = str.isalpha
    err_msg = 'Brand name should not contain numbers; please try again: '
    brand, conv = get_input(input_msg, criterion, err_msg, conv)

    # Get truck model; TODO: ask a domain expert what would be a more general model name pattern
    input_msg = 'Model: '
    criterion = lambda x: re.match(r'[a-zA-Z]{2} \d+', x)  # assume this pattern due to lack of domain expertise
    err_msg = 'Model name should have the pattern of two letters followed by space followed by a series of numbers,' \
              'e.g. "SC 3200"; please try again: '
    model, conv = get_input(input_msg, criterion, err_msg, conv)

    # Get truck engine size in cubic centimeters
    input_msg = 'Engine size (in cubic centimeters): '  # TODO: would be nice to have unit awareness and conversion
    criterion = lambda x: re.match(r'^\d+$', x)
    err_msg = 'Engine size should contain only numbers; please try again: '
    engine_size, conv = get_input(input_msg, criterion, err_msg, conv)

    # Get number of truck axles
    input_msg = 'Number of truck axles: '
    criterion = lambda x: re.match(r'^\d{1,2}$', x)
    err_msg = 'Please enter only a single- or double-digit whole number: '
    axle_number, conv = get_input(input_msg, criterion, err_msg, conv)

    # Get truck weight in tonnes
    input_msg = 'Truck weight in metric tonnes: '
    criterion = lambda x: re.match(r'^\d+(\.\d*)?$', x)
    err_msg = 'Truck weight should contain only whole or decimal numbers; please try again: '
    weight, conv = get_input(input_msg, criterion, err_msg, conv)

    # Get maximal load of the truck in tonnes
    input_msg = 'Truck maximal load in metric tonnes: '
    criterion = lambda x: re.match(r'^\d+(\.\d*)?$', x)
    err_msg = 'Maximal load should contain only whole or decimal numbers; please try again: '
    max_load, conv = get_input(input_msg, criterion, err_msg, conv)

    # Put it all in the Series
    truck = pd.Series(data=[brand, model, engine_size, axle_number, weight, max_load],
                      index=['Brand', 'Model', 'Engine (cc)', 'Axle number', 'Weight (T)', 'Max load (T)'])

    # Check if the information is correct
    conv = say('Please check if the following information is correct (y/n): ', conv)
    for key, value in truck.to_dict().items():  # doing it this way in order to avoid "dtype:object" that pandas prints
        conv = say('{0:>15}   {1:<10}'.format(key, value), conv)
    statement, conv = ask('> ', conv)
    if negative_answer(statement):  # if the user input was negative
        conv = say('No problem, let\'s try again.', conv)
        conv = say('Please provide details for vehicle nr. {0}.'.format(truck_nr), conv)
        truck = get_single_truck(truck_nr, conv)

    # Return the truck information
    return truck, conv


def check_fleet(fleet: pd.DataFrame, conv: List) -> Tuple[pd.DataFrame, List]:
    """
    Takes the collected fleet information and asks a user to verify it. If there is something wrong, it collects again
    the correct information for a particular truck/row.

    Inputs
    :param fleet: pandas DataFrame with the information about all the trucks in the fleet
    :param conv: ongoing conversation list

    Outputs
    :return: pandas DataFrame with the information about all the trucks in the fleet, and ongoing conversation list
    """
    time.sleep(0.5)
    conv = say('\nFleet information collected. '
               'Please take a look at the table and tell us if everything is correct (y/n).\n', conv)
    conv = say(fleet.to_string(), conv)
    conv = say('\n', conv)
    statement, conv = ask('> ', conv)
    if negative_answer(statement):  # if user input is negative
        truck_nr, conv = get_input('What is the number of truck that contains incorrect information? ',
                                   str.isnumeric,
                                   'Please provide whole numbers only: ',
                                   conv)
        truck_nr = int(truck_nr)  # we made sure in the step above that this is going to be valid
        truck, conv = get_single_truck(truck_nr, conv)
        fleet.loc[truck_nr] = truck

        # Check it again
        fleet, conv = check_fleet(fleet, conv)

    # Return if everything is alright
    return fleet, conv


def get_fleet(conv: List) -> Tuple[pd.DataFrame, List]:
    """
    This is the main function for obtaining the fleet info. It collects all the user information and data, verifies it,
    and constructs a pandas DataFrame of the fleet where each row represents a single truck, and each column one
    property of that truck

    Inputs
    :param conv: ongoing conversation list

    Outputs
    :return: fleet information as a pandas DataFrame, and ongoing conversation list
    """

    # Initialize the fleet table
    fleet = pd.DataFrame(data=None,
                         columns=['Brand', 'Model', 'Engine (cc)', 'Axle number', 'Weight (T)', 'Max load (T)'])

    # Get the number of trucks in the fleet
    total_trucks, conv = get_input('How many vehicles are there in this fleet? ',
                                   str.isnumeric,
                                   'Please provide whole numbers only: ',
                                   conv)
    total_trucks = int(total_trucks)

    # Collect the fleet data
    conv = say('\nWe will now collect your fleet information.', conv)
    time.sleep(0.5)
    for truck_nr in range(1, total_trucks+1):
        truck, conv = get_single_truck(truck_nr, conv)  # get the properties of this truck
        fleet = fleet.append(truck, ignore_index=True)  # write it into the fleet table

    # Set the fleet index to start from 1, so that it's easier for customers to query it
    fleet.index += 1
    fleet.index.name = 'Truck nr.'

    # Check if the fleet information is correct; if not, re-do the offending rows
    fleet, conv = check_fleet(fleet, conv)

    return fleet, conv


# ----------------------------------------------------------------------------------------------------------------------
#                                                   MAIN function
# ----------------------------------------------------------------------------------------------------------------------

def main():
    """
    Perform the conversation with the customer, collect the data, write it into a csv file, and save the entire
    dialogue in a txt file.
    """
    # Initialize some variables
    data_path = './data'  # path to the data folder
    conv = []  # main conversation list, where the entire dialogue will be stored

    # Start the conversation
    conv = say('Hello, I am here to help you organize your fleet.', conv)
    conv = say('If at any point you want to quit from the program, just type "q" or "quit".', conv)
    time.sleep(0.5)
    conv = say('Let us first collect basic information.', conv)
    time.sleep(0.5)

    # Get basic information and construct the base of the file name used for saving the data
    username, fleet_id, conv = get_basic_info(data_path, conv)

    # Obtain the complete fleet information
    fleet, conv = get_fleet(conv)

    # Say goodbye
    conv = say('Thank you, and have a nice day!', conv)

    # Save the data
    save_fleet(fleet, conv)
    save_conv(conv)


# ----------------------------------------------------------------------------------------------------------------------
#                                                   MAIN function
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
