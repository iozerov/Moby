"""Module contains all functions(with dictionaries for tests) that are used in multiple modules."""
import os
import urllib.request
import urllib.error
from zipfile import ZipFile
import pandas as pd

from typing import Dict, List

from scrapping_inspection_details import get_case_status
from constants import INSPECTION_DETAILS_FOLDER_NAME, FOUR_DIGIT_NAICS, TWO_DIGIT_NAICS,\
    EMPLOYER_NORMALIZED_NAMES, STATE_NAMES, FATALITY_OR_CATASTROPHE_NAMES

MONEY_TYPE_CONVERSION_TEST_CASES = {
    '$2,892,400.00': 2_892_400.0,
    '$533,468.00': 533_468.0,
    '$78,312.54': 78_312.54,
    '$3,803.05': 3803.05,
    '$170.89': 170.89,
    '$0.00': 0.0,
}


def money_string_to_number(money_string: str) -> float:
    """Input: $2,892,400.00; Output: 2892400.0"""
    return float(money_string.replace('$', '').replace(',', ''))


def money_number_to_string(money_number: float) -> str:
    """Input: 2892400.0; Output: $2,892,400.00"""
    return f"${money_number:,.2f}"


def mapping_employer_names(employer_name: str) -> str:
    """Unifies companies names to enable grouping operations."""
    for unified_name, old_names_list in EMPLOYER_NORMALIZED_NAMES.items():
        if employer_name in old_names_list:
            return unified_name
    return employer_name


def unification_of_fatalities(fatality_or_catastrophe_name: str) -> str:
    """Unifies fatality / catastrophe names in column to enable grouping operations."""
    for unified_name, old_names_list in FATALITY_OR_CATASTROPHE_NAMES.items():
        if fatality_or_catastrophe_name in old_names_list:
            return unified_name
    return fatality_or_catastrophe_name


def get_long_us_state_name_from_abbreviation(abbreviation: str) -> str:
    """Unifies companies names to enable grouping operations."""
    return STATE_NAMES[abbreviation] if abbreviation in STATE_NAMES.keys() else abbreviation


def get_naics_sector_numbers_by_names(naics_sector_names: List[str]) -> List[str]:
    """Get NAICS sector numbers by their names from 'TWO_DIGIT_NAICS.json'"""
    my_set = set()
    for naics_sector_name in naics_sector_names:
        my_set.update([key for key, value in TWO_DIGIT_NAICS.items() if value == naics_sector_name])
    return list(my_set)


def get_old_mapped_names(names_dict: dict) -> List[str]:
    """Concatenate lists from nested dictionary like 'EMPLOYER_NORMALIZED_NAMES.json'."""
    old_mapped_names = []
    for lst in names_dict.values():
        old_mapped_names += lst
    return old_mapped_names


def print_names_in_dictionary_which_are_absent_in_column(column: pd.Series, names: dict):
    """Helper function to be sure that all values from column are copied to dictionary correctly."""
    old_mapped_names = get_old_mapped_names(names)
    unique_col_names = column.unique()
    for name in old_mapped_names:
        if name not in unique_col_names:
            print(f"No such name in column: '{name}'")


def get_mapping_statistics(dictionary: dict) -> None:
    """Helper function to show how many old names are in each name."""
    for [name, names] in dictionary.items():
        print(name, len(names))


def print_cumulative_sum_for_column(column) -> None:
    """Helper function to see columns statistics on its categories in descending order."""
    sorted_series = column.value_counts()
    names = sorted_series.keys()
    values = sorted_series.tolist()
    length = len(column)
    for i, name in enumerate(names):
        curr = 100 * values[i] / length
        print('Delta % =', round(curr, 2), 'Percentage =', round(100 * values[i] / length, 2), '%',
              'Delta absolute =', values[i], name)


def parse_two_digit_naics_code(naics_code: str) -> str:
    """Returns sector name."""
    return TWO_DIGIT_NAICS[naics_code[:2]] if pd.notna(naics_code) else 'Non-classifiable'


def parse_four_digit_naics_code(naics_code: str) -> str:
    """Returns name of industry group if it's code is in 'FOUR_DIGIT_NAICS.json' file.
    Otherwise, returns sector name."""
    if pd.notna(naics_code):
        return FOUR_DIGIT_NAICS[naics_code[:4]]\
            if naics_code[:4] in FOUR_DIGIT_NAICS.keys()\
            else 'Other ' + TWO_DIGIT_NAICS[naics_code[:2]]
    return 'Non-classifiable'


def concat_zipped_csv_files(path, **kwargs) -> pd.DataFrame:
    """Returns dataframe with concatenated CSV files in archive."""
    zip_file = ZipFile(path, mode="r")
    return pd.concat([
        pd.read_csv(zip_file.open(text_file.filename), **kwargs)
        for text_file in zip_file.infolist()
        if text_file.filename.endswith('.csv')
    ], ignore_index=True)


def download_inspection_files(inspection_numbers: List[float]) -> List[float]:
    """Downloads **Inspection Details** files to folder by adding inspection_number to URL.
    Returns list of numbers that failed to download. \n
    Example: https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1595777.015 \n
    Definitions: https://www.osha.gov/data/inspection-detail-definitions#tab1
    """
    if not os.path.exists(INSPECTION_DETAILS_FOLDER_NAME):
        os.makedirs(INSPECTION_DETAILS_FOLDER_NAME)
    failed_numbers = []
    for index, number in enumerate(inspection_numbers):
        try:
            urllib.request.urlretrieve(
                url=f'https://www.osha.gov/ords/imis/establishment.inspection_detail?id={number}',
                filename=f'{INSPECTION_DETAILS_FOLDER_NAME}/{number}.html'
            )
        except (urllib.error.URLError, urllib.error.HTTPError, KeyboardInterrupt) as error:
            failed_numbers.append(number)
            print(f'{index}: {number} was failed to download: {error}')
        else:
            print(f'{index}: {number} was downloaded successfully')
    return failed_numbers


def download_open_cases_again(path_to_files: str) -> List[float]:
    """Downloads files with 'Open' or absent case statuses, and returns their numbers"""
    print("Detecting which files contain 'OPEN' or absent case statuses...")
    inspection_file_names = list(filter(
        lambda file_name: get_case_status(f'{path_to_files}/{file_name}') != 'CLOSED',
        os.listdir(path_to_files)
    ))
    print("Removing '.html' extension from file names...")
    open_inspection_numbers = list(map(lambda file_name: file_name[:-5], inspection_file_names))
    print(f"Downloading {len(open_inspection_numbers)} files...")
    failed_numbers = download_inspection_files(open_inspection_numbers)
    return open_inspection_numbers, failed_numbers

