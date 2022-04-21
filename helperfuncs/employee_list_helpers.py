import os
import json
import time
import logging

import requests


def kronos_login_and_return_header():
    data = {
        'credentials':{
            'username': os.getenv('KRONOSUSERNAME') , 
            'password': os.getenv('KRONOSPASSWORD'), 
            'company': os.getenv('KRONOSCOMPANY')
            }
    }
    headers = {
        'Content-Type':'application/json',
        'accept':'application/json',
        'Api-Key':os.getenv('KRONOSAPIKEY')
    }
    # Make a POST request to LOGIN and get the token
    login_response = requests.post("https://secure.saashr.com/ta/rest/v1/login", json=data, headers=headers)
    json_data = json.loads(login_response.text)
    # Add the bearer token to the header
    headers = {
        'authentication': "Bearer " + str(json_data['token'])
    }
    return headers


def get_home_department_values(headers, company_id):
    home_depts = {}
    url=f"https://secure.saashr.com/ta/rest/v2/companies/{company_id}/config/cost-centers?tree_index=0"
    self=requests.get(url, headers=headers).json()['cost_centers']
    for item in self:
        home_depts[item['id']] = item['name']       
    return home_depts

def get_union_values(headers, company_id):
    union_dict = {}
    url=f"https://secure.saashr.com/ta/rest/v2/companies/{company_id}/config/cost-centers?tree_index=3"
    self=requests.get(url, headers=headers).json()
    logging.info(self)
    for item in self['cost_centers']:
        union_dict[item['id']] = item['name']
    return union_dict

# Build the initial all_employees dictionary
def get_active_employees(headers, company_id):
    all_employees = {}
    url = f"https://secure.saashr.com/ta/rest/v2/companies/{company_id}/employees?terminated=0"
    self = requests.get(url, headers=headers).json()
    for employee in self['employees']:
        if employee['status'] == 'Active':
            all_employees[employee['id']] = {'first_name': employee['first_name'], 'last_name': employee['last_name'], 'status': employee['status']}
    return all_employees

def get_emp_details(key, headers, company_id):
    opt, on_leave = '',''
    url = f"https://secure2.saashr.com/ta/rest/v2/companies/{company_id}/employees/{key}"
    kronosEmpObj = requests.get(url, headers=headers).json()
    try:
        cost_centers = kronosEmpObj['cost_centers_info']['defaults']
    except KeyError as e:
        # If they dont have a cost-center,
        # it is a ghost manager account
        return False
    for item in cost_centers:
        if item['index'] == 0:
            home_dept = item['value']['id']
        if item['index'] == 1:
            entity = item['value']['id'] # Either School or Arc
        if item['index'] == 3:
            union = item['value']['id']
    for item in kronosEmpObj['account_extra_fields']:
        if item['index'] == 1:
            opt = item['values'][0]['value']
        if item['index'] == 5:
            on_leave = item['values'][0]['value']            
    try:
        phone = kronosEmpObj['phones']['cell_phone']
    except:
        phone = 'Cell Not Found'
    return home_dept, union, opt, phone, on_leave, entity

def build_employees_dict(all_employees, union_dict, home_depts, headers, company_id):
    for key in all_employees.keys():
        try:
            home_dept, union, opt, cell_phone, on_leave, entity = get_emp_details(key, headers, company_id)
        except (ValueError, TypeError) as error:
            home_dept=union=opt=cell_phone=on_leave=entity = ''            
        all_employees[key]['home_dept_id'] = home_dept
        all_employees[key]['union_id'] = union
        all_employees[key]['opt'] = opt
        all_employees[key]['cell'] = cell_phone
        all_employees[key]['on_leave'] = on_leave
        all_employees[key]['entity'] = entity
        try:
            all_employees[key]['home_dept'] = home_depts[home_dept]
        except:
            all_employees[key]['home_dept'] = 0
        try:
            all_employees[key]['union'] = union_dict[union]
        except:
            all_employees[key]['union'] = 'NA'
        time.sleep(0.5)
    return all_employees


# Build Residential List, all regardless of opt-in
def get_residential(all_employees):
    residential ={}
    for key in all_employees.keys():
        if all_employees[key]['home_dept']:
            if 221 <= int(all_employees[key]['home_dept'][:3]) <= 260:
                program = all_employees[key]['home_dept']
                all_employees[key]['home_dept'] = program.replace(program[:3], '1')
                residential[key] =  all_employees[key]
    return residential       

# Build Subs List, all regardless of opt-in
def get_subs(all_employees):
    subs ={}
    for key in all_employees.keys():
        if all_employees[key]['home_dept'] == '199-Adult Services Subs':
            subs[key] =  all_employees[key]
    return subs

# Get Union List, opted-in, not already in subs
def get_union(all_employees, subs):
    union = {}
    for key in all_employees.keys():
        #Union, opted-in, NOT in SUBS
        if (all_employees[key]['union'] != "Non-Union") and (all_employees[key]['opt'] == "Opt In") and (key not in subs):
            union[key] = all_employees[key]
    return union

# Get Non-Union List that have opted-in
def get_non_union(all_employees):
    non_union = {}
    for key in all_employees.keys():
        #Non-Union, opt-in
        if (all_employees[key]['union'] == "Non-Union") and (all_employees[key]['opt'] == "Opt In"):
            non_union[key] = all_employees[key]
    return non_union