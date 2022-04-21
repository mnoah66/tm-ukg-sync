
def remove_na_employees(all_employees):
    ''' Removes school employees, employees with no home_dept, and emps on leave'''
    for key in list(all_employees.keys()):
        if all_employees[key]['entity'] == 4818468:
            del all_employees[key]
            continue
        if all_employees[key]['home_dept'] == '':
            del all_employees[key]
            continue
        if all_employees[key]['on_leave'] == 'Yes':
            del all_employees[key]
            continue
    return all_employees

def clean_phones_or_remove(all_employees):
    ''' Cleans phone numbers.  Removes employee if their phone is missing or bad data'''
    specialChars = "()-. "
    for key in list(all_employees.keys()):
        phone = all_employees[key]['cell']
        if phone == "Cell Not Found":
            del all_employees[key]
            continue
        for character in specialChars:
            phone = phone.replace(character, '')
        if len(phone) == 10:
            phone = "1" + phone
        if len(phone) == 11 and phone[0] != "1":
            del all_employees[key]
            continue
        all_employees[key]['cell'] = phone
    return all_employees