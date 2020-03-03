"""
This function scrapes Wikipedia page with the list of all truck manufacturers. It is not foolproof as I was not covering
every possible type of problematic entry on the page. This is especially evident in the table column `Country`, where
all kind of residues can be found. However, the country of brand origin is not pertinent for the concrete task, so I'm
leaving the script as it is for now.
"""

import requests
import bs4
import re
import pandas as pd
from typing import Tuple, List


# ----------------------------------------------------------------------------------------------------------------------
#                                                 HELPER FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def remove_superfluous(text: str, pattern: List) -> str:
    """
    Strip the string from all superfluous text.

    Input
    :param text: text to be cleaned
    :param pattern: list of terms to be removed

    Output
    :return: cleaned text
    """
    for p in pattern:
        text = re.sub(p, '', text)
    return text


def clean_content(content: List) -> List:
    """
    Removes some specific unwanted elements from a list (e.g. trailing brackets).
    Source: https://stackoverflow.com/questions/4915920/how-to-delete-an-item-in-a-list-if-it-exists

    Input
    :param content: list to be manipulated

    Output
    :return: cleaned list
    """
    while '  (' in content: content.remove('  (')
    while ' (' in content: content.remove(' (')
    while ')' in content: content.remove(')')
    return content


# TODO: make function for cleaning the country entries in the table
'''
def verify_country(country: str, country_list: List) -> str:
    """

    :param country:
    :return:
    """
    if country not in country_list:
        country = ''
    return country
'''


# ----------------------------------------------------------------------------------------------------------------------
#                                                   FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def get_brand_and_company(content: bs4.element, strip_list: List) -> Tuple[str, str]:
    """
    Takes a truck table entry, parses it, and cleans it.
    Note however that at least one brand name instance does not have a link of any kind associated with it, and is just
    a pure string. This case is handled in the `else` statement.

    Input
    :param content: contents of the table entry for a particular truck brand holding brand name and company name
    :param strip_list: list of elements to be removed from the entries

    Output
    :return: tuple with name of the truck brand and the parent company
    """
    if isinstance(content, bs4.element.Tag):
        brand_name = remove_superfluous(content.next_element, strip_list)
        company_name = remove_superfluous(content['title'], strip_list)
    else:
        brand_name = remove_superfluous(content, strip_list)
        company_name = remove_superfluous(content, strip_list)
    return brand_name, company_name


def get_continent(content: bs4.element.Tag) -> str:
    """
    Completely empirically determined for this particular Wikipedia page, this function will identify the continent for
    the current truck brands table.

    Input
    :param content: content of the table with truck brand information

    Output
    :return: the name of the continent
    """
    tmp_content = content.parent
    for ii in range(4):
        tmp_content = tmp_content.previous_sibling
    try:
        continent = tmp_content.span['id'].replace('_', ' ')
    except TypeError:
        for ii in range(2):
            tmp_content = tmp_content.previous_sibling
        continent = tmp_content.span['id'].replace('_', ' ')
    return continent


def parse_trucks_page(data: bs4.BeautifulSoup, strip_list: List, frame_columns: List) -> pd.DataFrame:

    # Initialize the table DataFrame
    truck_brands = pd.DataFrame(data=None, columns=frame_columns)

    # Get all tables according to their continents
    table_all_continents = data.find_all('table', {'class': 'multicol', 'role': 'presentation'})
    for table_one_continent in table_all_continents:

        # Find the continent of origin for this table
        continent = get_continent(table_one_continent)

        # Get all the table entries
        table_contents = table_one_continent.find_all('li')

        # Go over each table entry and process them
        for brand in table_contents:

            # Get the content and clean it
            content = clean_content(brand.contents)

            # Get the company and brand names
            brand_name, company_name = get_brand_and_company(content[0], strip_list)

            # Get the country, if it exists
            # TODO: handle case when multiple countries are declared for a single brand
            if continent != 'Oceania':
                country = None  # if the country doesn't exist, initialize it to a None
            else:  # if the continent is Oceania, there's only one "country" there CURRENTLY producing trucks: Australia
                country = 'Australia'
            # Now get the country
            if len(content) > 1:
                # There are several ways country could be encoded; if a hyperlink is present, then it's wrapped between
                # <a> tags; if it is not, then it's just a string
                if isinstance(content[1], bs4.element.Tag):
                    # NOTE: this covers the case when there's no country associated with entry, but content[1] exists
                    try:
                        country = content[1]['title']
                    except KeyError:
                        country = None
                elif isinstance(content[1], bs4.element.NavigableString):
                    country = content[1].replace('(', '').replace(')', '').strip()

                # TODO: Verify that the country is indeed a country and not something weird
                # country = verify_country(country, country_list)

            # Write it into this country's DataFrame
            truck_brands = truck_brands.append(
                pd.DataFrame(data=[[brand_name, company_name, country, continent]], columns=frame_columns))

    # Sort by truck name and reset the index so that everything is numbered properly
    truck_brands = truck_brands.sort_values('Brand').reset_index(drop=True)

    return truck_brands


# ----------------------------------------------------------------------------------------------------------------------
#                                                     MAIN
# ----------------------------------------------------------------------------------------------------------------------

def truck_brands_table(save_path='./'):

    # Site from which we download data
    website_url = 'https://en.wikipedia.org/wiki/List_of_truck_manufacturers'

    # Words to be removed from brand names and companies
    # source: https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch05s02.html
    strip_list = [re.compile(r' \(.*\b(?:motor[cyles]+|lorry|truck[s]+|vehicle[s]+|automobile[s]+|manufacturer)\b.*\)'),
                  re.compile(r' \(.*\b(?:UK|Russia|Warrington|Turkey|Germany|France|Serbia|Czech)\b.*\)'),
                  re.compile(r' \(page does not exist\)')]

    # Columns of the end table
    columns = ['Brand', 'Company name', 'Country', 'Continent']

    # Get the data
    website = requests.get(website_url).text
    soup = bs4.BeautifulSoup(website, features='lxml')  # prerequisite: lxml library

    # Here I have visually inspected the retrieved code to find the tags that will enable me to extract the list of all
    # truck manufacturers. I have used the command `print(soup.prettify())`.

    # Obtain the table with information about all the truck brands, their parent companies, and the countries of origin
    truck_brands = parse_trucks_page(data=soup, strip_list=strip_list, frame_columns=columns)

    # Finally, write the data to .cvs
    truck_brands.to_csv(save_path)

    return truck_brands


# ----------------------------------------------------------------------------------------------------------------------
#                                                     BODY
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    save_here = './truck_brands.csv'

    all_brands = truck_brands_table(save_path=save_here)
