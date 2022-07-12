
from collections import defaultdict
import time

def delete_or_create_list(key, list_dict, tm_session):
    try:
        payload = {
        "all": 1
        }
        url = f"https://rest.textmagic.com/api/v2/lists/{list_dict[key]}/contacts/delete"
        # If above fails, it means that the list is not already in TM.
        r = tm_session.post(url, payload)
        return list_dict[key]
    except:
        #1. Create the list
        payload = {
            'name': key,
            'shared': 'true'
        }
        url = "https://rest.textmagic.com/api/v2/lists"
        r = tm_session.post(url, payload).json()
        return str(r['id'])

# RESIDENTIAL
def update_residential_lists(employees, tm_session, list_dict):
    res_group = defaultdict(list)
    # 1. Loop through all residential lists, group by home_dept
    for key, value in employees.items():
        res_group[value['home_dept']].append(value)
    # 2. Loop through home dept groupings, delete contacts
    for key, value in res_group.items():
        add_if_in_another_list = []
        
        # 1. Delete all contacts in that list or create the list.
        list_id = delete_or_create_list(key, list_dict, tm_session)

        time.sleep(0.5)
        #####################################
        for employee in value:
            # Add to list
            payload = {
                'lists': str(list_id), 
                'phone': employee['cell'],
                'firstName': employee['first_name'],
                'lastName': employee['last_name'],
            }
            url = f"https://rest.textmagic.com/api/v2/contacts/normalized"
            r = tm_session.post(url, payload)
            if "Phone number already exists" in r.text:
                # Get their TM ID and add to temp list
                url=f"https://rest.textmagic.com/api/v2/contacts/phone/{employee['cell']}"
                r = tm_session.get(url).json()
                employee_id = add_if_in_another_list.append(str(r['id'])) 
        if add_if_in_another_list:
            payload = {
                "contacts": ",".join(add_if_in_another_list)
            }
            url = f"https://rest.textmagic.com/api/v2/lists/{str(list_id)}/contacts"
            r = tm_session.put(url, payload).json() 

def update_non_union_list(non_union, tm_session):
    add_if_in_another_list = [] # list of contact IDs already in TM.  We will
                                # Use this to add these IDs to the Non-Union list at the end
    non_union_list_id = 2781593
    
    # 1. Delete all contacts in that list.
    payload = {
    "all": 1
    }
    url = f"https://rest.textmagic.com/api/v2/lists/{non_union_list_id}/contacts/delete"
    r = tm_session.post(url, payload)
    
    # 2. Add employees
    for key, value in non_union.items():
        payload = {
            'lists': str(non_union_list_id), ##### Hard-coded alert
            'phone': value['cell'],
            'firstName': value['first_name'],
            'lastName': value['last_name'],
        }
        url = f"https://rest.textmagic.com/api/v2/contacts/normalized"
        r = tm_session.post(url, payload)
        if "Phone number already exists" in r.text:
            # Get their TM ID and add to temp list
            url=f"https://rest.textmagic.com/api/v2/contacts/phone/{value['cell']}"
            r = tm_session.get(url).json()
            add_if_in_another_list.append(str(r['id'])) 
            
    if add_if_in_another_list:
        payload = {
            "contacts": ",".join(add_if_in_another_list)
        }
        url = f"https://rest.textmagic.com/api/v2/lists/{non_union_list_id}/contacts"
        r = tm_session.put(url, payload).json()

# UNION
def update_union_list(union, tm_session):
    add_if_in_another_list = [] # list of contact IDs already in TM.  We will
                                # Use this to add these IDs to the union list at the end
    union_list_id = 2779626
    
    # 1. Delete all contacts in that list.
    payload = {
    "all": 1
    }
    url = f"https://rest.textmagic.com/api/v2/lists/{union_list_id}/contacts/delete"
    r = tm_session.post(url, payload)
    #####################################
    
    # 2. Add employees
    for key, value in union.items():
        payload = {
            'lists': str(union_list_id), ##### Hard-coded alert
            'phone': value['cell'],
            'firstName': value['first_name'],
            'lastName': value['last_name'],
        }
        url = f"https://rest.textmagic.com/api/v2/contacts/normalized"
        r = tm_session.post(url, payload)
        if "Phone number already exists" in r.text:
            # Get their TM ID and add to temp list
            url=f"https://rest.textmagic.com/api/v2/contacts/phone/{value['cell']}"
            r = tm_session.get(url).json()
            add_if_in_another_list.append(str(r['id'])) 
    if add_if_in_another_list:
        payload = {
            "contacts": ",".join(add_if_in_another_list)
        }
        url = f"https://rest.textmagic.com/api/v2/lists/{union_list_id}/contacts"
        r = tm_session.put(url, payload).json()

# SUBS
def update_subs_list(subs, tm_session):
    add_if_in_another_list = [] # list of contact IDs already in TM.  We will
                                # Use this to add these IDs to the sub list at the end
    sub_list_id = 2778552
    
    # 1. Delete all contacts in that list.
    payload = {
    "all": 1
    }
    url = f"https://rest.textmagic.com/api/v2/lists/{sub_list_id}/contacts/delete"
    r = tm_session.post(url, payload)
    #####################################
    
    # 2. Add employees
    for key, value in subs.items():
        payload = {
            'lists': str(sub_list_id), ##### Hard-coded alert
            'phone': value['cell'],
            'firstName': value['first_name'],
            'lastName': value['last_name'],
        }
        url = f"https://rest.textmagic.com/api/v2/contacts/normalized"
        r = tm_session.post(url, payload)
        if "Phone number already exists" in r.text:
            # Get their TM ID and add to temp list
            url=f"https://rest.textmagic.com/api/v2/contacts/phone/{value['cell']}"
            r = tm_session.get(url).json()
            add_if_in_another_list.append(str(r['id'])) 
            
    if add_if_in_another_list:
        payload = {
            "contacts": ",".join(add_if_in_another_list)
        }
        url = f"https://rest.textmagic.com/api/v2/lists/{sub_list_id}/contacts"
        r = tm_session.put(url, payload).json()

def get_lists(tm_session):
    all_lists=[]
    def main():
        url = "https://rest.textmagic.com/api/v2/lists?limit=25" 
        first_page = tm_session.get(url).json()
        yield first_page
        num_pages = first_page['pageCount']

        for page in range(2, num_pages + 1):
            next_page = tm_session.get(url, params={'page': page}).json()
            yield next_page

    for page in main():
        all_lists.extend(page['resources'])

    # Convert lists of TM lists to dictionary
    list_dict = {}
    for i in range(len(all_lists)):
        list_dict[all_lists[i]['name']] = all_lists[i]['id']
    return list_dict