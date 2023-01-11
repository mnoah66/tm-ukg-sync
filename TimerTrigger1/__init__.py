import os
import datetime
import logging
import json
import time
from collections import defaultdict


import requests

import azure.functions as func

from helperfuncs import helper_functions, employee_list_helpers, employee_cleanup


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info("Starting now which should be 03:00 UTC, so 11pm Eastern...")
    company_id = str(os.getenv('COMPANYID'))
    print(company_id)

    # Text Magic headers
    tm_headers = {
        'x-tm-key': os.getenv('TMAPIKEY'),
        'Content-Type':'application/x-www-form-urlencoded',
        'x-tm-username':os.getenv('TMUSERNAME')
    }

    headers = employee_list_helpers.kronos_login_and_return_header()
    logging.info("headers = ......")
    union_dict = employee_list_helpers.get_union_values(headers, company_id)
    home_depts = employee_list_helpers.get_home_department_values(headers, company_id)


    all_employees = employee_list_helpers.get_active_employees(headers, company_id)
    all_employees = employee_list_helpers.build_employees_dict(all_employees, union_dict, home_depts, headers, company_id)

    clean = employee_cleanup.remove_na_employees(all_employees) 
    all_employees = employee_cleanup.clean_phones_or_remove(clean)

    logging.info("Building group dicts now......")
    residential = employee_list_helpers.get_residential(all_employees)
    subs = employee_list_helpers.get_subs(all_employees)
    union = employee_list_helpers.get_union(all_employees, subs)
    non_union = employee_list_helpers.get_non_union(all_employees)

    #### Time for TextMagic Stuff

    tm_session = requests.Session()
    tm_session.headers.update(tm_headers)

    # Dictionary of list names and their IDs
    # {'1-Orange':1249085, '1-Beechtree':875492}
    list_dict = helper_functions.get_lists(tm_session)


    helper_functions.update_subs_list(subs, tm_session)

    helper_functions.update_union_list(union, tm_session)
    
    helper_functions.update_non_union_list(non_union, tm_session)
    
    helper_functions.update_residential_lists(residential, tm_session, list_dict) 
    
    payload_list = []
    for k, v in all_employees.items():
        payload_list.append(v)

    url = "https://prod-111.westus.logic.azure.com:443/workflows/857a1997c5924c6c9c8c5dd1c381fbac/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=4nERQqLXXbqWSYSrJJCU8KIm25692HKHD6NdtA2Ethc"
    r = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload_list))

    logging.info("All done....\/\/\/\/\/\/\/\/\/\/\/")


    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
