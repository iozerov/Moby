"""Module for working with Inspection Details files"""
from typing import Literal
import urllib.error
from dataclasses import dataclass, fields
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict
from constants import NULL_INT, NULL_STRING, INSPECTION_DETAILS_FOLDER_NAME


@dataclass
class Inspection:
    """Contains attributes that are parsed from Inspection Details files using 'parse_inspection_file' function"""
    case_status: Literal['OPEN', 'CLOSED']
    employer_name: str
    ############################################################
    union_status: Literal['Union', 'NonUnion']
    naics_code: int
    naics_name: str
    ############################################################
    inspection_type: Literal['Planned', 'Referral', 'Complaint', 'Unprog Rel', 'Fat/Cat', 'Prog Other', 'Accident',
                             'Prog Related', 'FollowUp', 'Unprog Other', 'Other', 'Monitoring']
    scope: Literal['Partial', 'Complete', 'Records']
    advance_notice: Literal['Y', 'N']
    ownership: Literal['Private', 'LocalGovt', 'StateGovt']
    safety_or_health: Literal['Safety', 'Health']
    # 'Violation Summary' table ################################
    total_initial_violations: int
    total_current_violations: int
    total_initial_penalty: str
    total_current_penalty: str
    total_fta_penalty: str


DATASETS_DICT = {
    'Enforcement Cases with Initial Penalties of $40,000 or Above': {
        '1437214.015': Inspection(
            case_status='CLOSED',
            employer_name='U.S. Postal Service - Pomona Main Post Office',
            union_status='NonUnion',
            naics_code=491110,
            naics_name='Postal Service',
            inspection_type='Planned',
            scope='Complete',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=5,
            total_current_violations=4,
            total_initial_penalty='$68,282',
            total_current_penalty='$44,013',
            total_fta_penalty='$0',
        ),
        '1603495.015': Inspection(
            case_status='OPEN',
            employer_name='104612 - Inter-Group Mgmt Inc Dba Rh Brandtjen - Co',
            union_status='NonUnion',
            naics_code=238910,
            naics_name='Site Preparation Contractors',
            inspection_type='Fat/Cat',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=4,
            total_current_violations=4,
            total_initial_penalty='$75,250',
            total_current_penalty='$75,250',
            total_fta_penalty='$0',
        ),
        '1420390.015': Inspection(
            case_status='OPEN',
            employer_name='Wa317955522 - United Grain Corp',
            union_status='Union',
            naics_code=424510,
            naics_name='Grain and Field Bean Merchant Wholesalers',
            inspection_type='Complaint',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=6,
            total_current_violations=6,
            total_initial_penalty='$128,000',
            total_current_penalty='$30,000',
            total_fta_penalty='$0',
        ),
        '1482177.015': Inspection(
            case_status='CLOSED',
            employer_name='Indian Health Service/Phoenix Indian Medical Center (Pimc)',
            union_status='Union',
            naics_code=622110,
            naics_name='General Medical and Surgical Hospitals',
            inspection_type='Fat/Cat',
            scope='Partial',
            advance_notice='N',
            ownership=NULL_STRING,
            safety_or_health='Health',
            total_initial_violations=3,
            total_current_violations=3,
            total_initial_penalty='$0',
            total_current_penalty='$0',
            total_fta_penalty='$0',
        ),
        '317191393.0': Inspection(
            case_status=NULL_STRING,
            employer_name='La Amapola, Inc.',
            union_status='NonUnion',
            naics_code=445110,
            naics_name='Supermarkets and Other Grocery (except Convenience) Stores',
            inspection_type='FollowUp',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=6,
            total_current_violations=6,
            total_initial_penalty='$48,000',
            total_current_penalty='$31,000',
            total_fta_penalty='$0',
        ),
        '1575072.015': Inspection(
            case_status='CLOSED',
            employer_name='Trident Seafoods Corporation',
            union_status='NonUnion',
            naics_code=311710,
            naics_name=NULL_STRING,
            inspection_type='Accident',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=1,
            total_current_violations=NULL_INT,
            total_initial_penalty='$75,092',
            total_current_penalty='$0',
            total_fta_penalty='$0',
        ),
        '1591011.015': Inspection(
            case_status='OPEN',
            employer_name='North Pacific Seafoods, Inc.',
            union_status='NonUnion',
            naics_code=311710,
            naics_name=NULL_STRING,
            inspection_type='Complaint',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Health',
            total_initial_violations=28,
            total_current_violations=18,
            total_initial_penalty='$533,468',
            total_current_penalty='$94,365',
            total_fta_penalty='$0',
        ),
        '956197.015': Inspection(
            case_status='CLOSED',
            employer_name='Willcutt Block And Supply Company Of Tuscaloosa, Inc.',
            union_status='NonUnion',
            naics_code=327331,
            naics_name='Concrete Block and Brick Manufacturing',
            inspection_type='Planned',
            scope='Complete',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Health',
            total_initial_violations=11,
            total_current_violations=11,
            total_initial_penalty='$19,200',
            total_current_penalty='$11,550',
            total_fta_penalty='$30,500',
        ),
        '975067.015': Inspection(
            case_status='CLOSED',
            employer_name='Sabert Corporation',
            union_status='NonUnion',
            naics_code=493110,
            naics_name='General Warehousing and Storage',
            inspection_type='Referral',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=1,
            total_current_violations=1,
            total_initial_penalty='$70,000',
            total_current_penalty='$42,000',
            total_fta_penalty='$0',
        ),
    },
    'Fatality Inspection Data': {
        '1198722.015': Inspection(
            case_status='CLOSED',
            employer_name='Tk Potable Diving',
            union_status='NonUnion',
            naics_code=561990,
            naics_name='All Other Support Services',
            inspection_type='Fat/Cat',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Health',
            total_initial_violations=6,
            total_current_violations=6,
            total_initial_penalty='$0',
            total_current_penalty='$0',
            total_fta_penalty='$0',
        ),
        '1210520.015': Inspection(
            case_status='OPEN',
            employer_name='Rogelio Gomez Dba Rogelio Gomez',
            union_status='NonUnion',
            naics_code=238320,
            naics_name='Painting and Wall Covering Contractors',
            inspection_type='Fat/Cat',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=8,
            total_current_violations=8,
            total_initial_penalty='$60,240',
            total_current_penalty='$60,240',
            total_fta_penalty='$0',
        ),
    },
    'Reports of Fatalities and Catastrophes - Archive': {
        '976450.015': Inspection(
            case_status='CLOSED',
            employer_name='Aspen Imaging, Llc',
            union_status='Union',
            naics_code=323110,
            naics_name='Commercial Lithographic Printing',
            inspection_type='Planned',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=5,
            total_current_violations=5,
            total_initial_penalty='$11,900',
            total_current_penalty='$5,950',
            total_fta_penalty='$0',
        ),
        '1205339.015': Inspection(
            case_status='CLOSED',
            employer_name='Costa Farms, Llc',
            union_status='NonUnion',
            naics_code=111421,
            naics_name='Nursery and Tree Production',
            inspection_type='Fat/Cat',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=2,
            total_current_violations=2,
            total_initial_penalty='$25,350',
            total_current_penalty='$17,745',
            total_fta_penalty='$0',
        ),
    },
    'Severe Injury Reports': {
        '1016449.015': Inspection(
            case_status='CLOSED',
            employer_name='Costco Wholesale Corporation',
            union_status='NonUnion',
            naics_code=445110,
            naics_name='Supermarkets and Other Grocery (except Convenience) Stores',
            inspection_type='Referral',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=NULL_INT,
            total_current_violations=NULL_INT,
            total_initial_penalty=NULL_STRING,
            total_current_penalty=NULL_STRING,
            total_fta_penalty=NULL_STRING,
        ),
        '1017348.015': Inspection(
            case_status='CLOSED',
            employer_name='Hdt Expeditionary Systems Inc (Esg)',
            union_status='NonUnion',
            naics_code=333415,
            naics_name='Air-Conditioning and Warm Air Heating Equipment and Commercial and'
                       ' Industrial Refrigeration Equipment Manufacturing',
            inspection_type='Referral',
            scope='Partial',
            advance_notice='N',
            ownership='Private',
            safety_or_health='Safety',
            total_initial_violations=NULL_INT,
            total_current_violations=NULL_INT,
            total_initial_penalty=NULL_STRING,
            total_current_penalty=NULL_STRING,
            total_fta_penalty=NULL_STRING,
        ),
    },
}


def get_case_status(path_to_file: str) -> str:
    """Parses case status from **Inspection Details**. Used to refresh file with 'Open' cases."""
    with open(path_to_file, 'r', encoding='utf-8') as file:
        case_status = BeautifulSoup(file.read(), 'html.parser')\
            .find('div', {'class': "well well-small"})
    return case_status.text[len('Case Status: '):] if case_status is not None else NULL_STRING


def parse_inspection_file(path_to_file: str) -> Inspection:
    """Parses information from **Inspection Details** file and returns it as instance of Inspection
     dataclass.\n
    File example: https://www.osha.gov/ords/imis/establishment.inspection_detail?id=1595777.015 \n
    Definitions: https://www.osha.gov/data/inspection-detail-definitions#tab1
    """
    with open(path_to_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        case_status = soup.find('div', {'class': "well well-small"})
        span4_list = soup.find_all('div', {'class': "span4"})
        text_with_naics = span4_list[5].text
        naics_list = text_with_naics[text_with_naics.index('\nNAICS: ') + 8: -1].split('/')
        split_list = span4_list[6].text.split('\n')
        employer_str = soup.find('h4').text
    try:
        violation_summary_table = pd.read_html(path_to_file, match='Violation Summary')[0]
    except (urllib.error.URLError, ValueError, IndexError, KeyboardInterrupt):
        violation_summary_table = []
    return Inspection(
        case_status=case_status.text[len('Case Status: '):] if case_status else NULL_STRING,
        employer_name=employer_str[employer_str.index(' - ') + 3:],
        union_status=span4_list[4].text[len('Union Status: '):],
        naics_code=int(naics_list[0]),
        naics_name=naics_list[1] if len(naics_list) > 1 else NULL_STRING,
        inspection_type=split_list[0][len('Inspection Type: '):],
        scope=split_list[1][len('Scope: '):],
        advance_notice=split_list[2][len('Advanced Notice: '):],
        ownership=split_list[3][len('Ownership: '):] if not split_list[3].endswith('\xa0') else NULL_STRING,
        safety_or_health=span4_list[7].text.split('\n')[1][len('Safety/Health: '):],
        total_initial_violations=(
            int(violation_summary_table['Total'][0])
            if len(violation_summary_table) and pd.notna(violation_summary_table['Total'][0])
            else NULL_INT
        ),
        total_current_violations=(
            int(violation_summary_table['Total'][1])
            if len(violation_summary_table) and pd.notna(violation_summary_table['Total'][1])
            else NULL_INT
        ),
        total_initial_penalty=(
            violation_summary_table['Total'][2]
            if len(violation_summary_table) and pd.notna(violation_summary_table['Total'][2])
            else NULL_STRING
        ),
        total_current_penalty=(
            violation_summary_table['Total'][3]
            if len(violation_summary_table) and pd.notna(violation_summary_table['Total'][3])
            else NULL_STRING
        ),
        total_fta_penalty=(
            violation_summary_table['Total'][4]
            if len(violation_summary_table) and pd.notna(violation_summary_table['Total'][4])
            else NULL_STRING
        ),
    )


def get_inspection_details_list(inspection_number):
    """Used to add new columns using apply function:
    new_columns_names = list(Inspection.__annotations__.keys())
    df[new_columns_names] = df.apply(lambda row: get_inspection_details_list(str(row['Inspection Number'])),
    axis='columns', result_type='expand')
    """
    # if os.path.exists(inspection_number):
    ins = parse_inspection_file(f'{INSPECTION_DETAILS_FOLDER_NAME}/{inspection_number}.html')
    return [ins.__getattribute__(field.name) for field in fields(ins)]
    # else:
    # except FileNotFoundError:
    #     return ['No file'] * len(fields(Inspection))
