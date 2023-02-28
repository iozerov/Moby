"""Module contains all constants that are used in multiple modules."""
import json
import os

from typing import Dict, List, AnyStr


LAST_DATE_OF_INTEREST = '2020-01-01'
ALL = 'ALL'

# Folder names
PROJECT_NAME = 'MOBY'
INSPECTION_DETAILS_FOLDER_NAME = 'Inspections'
MAPPING_FILES_FOLDER_NAME = 'Mapping_files_for_values_in_columns'


# Type-related constants
NULL_INT = -1
NULL_STRING = ''


# Loading JSON files. Changing current working directory is needed to prevent
# 'FileNotFoundError' when working in Jupyter Notebooks in 'Datasets' folder.

with open(f"{MAPPING_FILES_FOLDER_NAME}/EMPLOYER_NORMALIZED_NAMES.json", 'r', encoding='utf-8') as f:
    EMPLOYER_NORMALIZED_NAMES = json.load(f)
with open(f"{MAPPING_FILES_FOLDER_NAME}/FATALITY_OR_CATASTROPHE_NAMES.json", 'r', encoding='utf-8') as f:
    FATALITY_OR_CATASTROPHE_NAMES = json.load(f)
with open(f"{MAPPING_FILES_FOLDER_NAME}/FOUR_DIGIT_NAICS.json", 'r', encoding='utf-8') as f:
    FOUR_DIGIT_NAICS = json.load(f)
with open(f"{MAPPING_FILES_FOLDER_NAME}/NAICS_AGGREGATION_LEVELS.json", 'r', encoding='utf-8') as f:
    NAICS_AGGREGATION_LEVELS = json.load(f)
with open(f"{MAPPING_FILES_FOLDER_NAME}/STATE_NAMES.json", 'r', encoding='utf-8') as f:
    STATE_NAMES = json.load(f)
with open(f"{MAPPING_FILES_FOLDER_NAME}/TWO_DIGIT_NAICS.json", 'r', encoding='utf-8') as f:
    TWO_DIGIT_NAICS = json.load(f)
