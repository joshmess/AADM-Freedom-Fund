from bs4 import BeautifulSoup as bs
import requests
import re
import json
import pandas as pd
 
aadm_dic = []
 
acc_url = "http://enigma.athensclarkecounty.com/photo/jailcurrent.asp"
url_page = requests.get(acc_url)
acc_soup = bs(url_page.content, 'html.parser')
 
"""
THIS PIECE OF SCRIPT WILL SCRAPE EVERY HTML 'a' TAG AND USE REGULAR EXPRESSIONS
TO EXTRACT THE UNIQUE URL-END TO EVERY PERSON BEING HELD
 
FROM HERE, THE BASE URL IS CONCATENATED TO UNIQUE URL-END AND THEN ADDED TO A 
TEMPORARY LIST CALLED "links"
"""
links = []
names = []
a_tags = acc_soup.find_all('a')
 
for tag in a_tags:
    names.append(tag.text)
    m = re.search("'(.+?)'", tag['onclick'])
    if m:
        links.append('http://enigma.athensclarkecounty.com/photo/' + m.group(1))
 
"""
THIS PIECE OF SCRIPT WILL THEN UTILIZE OUR "links" LIST ALONGSIDE REGULAR EXPRESSIONS
TO EXTRACT THE UNIQUE ID ASSIGNED TO EVERY PERSON BEING HELD 
 
FROM HERE, THE UNIQUE ID IS ADDED TO A TEMPORARY LIST CALLED "mids"
"""
mids = []
 
for link in links:
    m = re.search("id=-(.+?)&", link)
    if m:
        mids.append(int(m.group(1)))
 
"""
THIS PIECE OF SCRIPT BEGINS BUILDING OUR DICTIONARY
"""
print("LENGTH OF LIST: " + str(len(links)))
i = 0
for id in mids:
    aadm_dic.append({
        'MID': id,
        'Name': names[i],
        'Url': links[i],
        'Charges': [],
        'Qualifies': 1
    })
    i = i + 1
 
"""
IN THIS SECTION WE SCRAPE THE INDIVIDUAL URLS OF EACH MID
"""
 
id_index = 0
for link in links: 
    print(id_index)
    print(names[id_index])
    print("*************")
    unique_url = link
    unique_page = requests.get(unique_url)
    unique_soup = bs(unique_page.content, 'html.parser')
 
    unique_charge_table = unique_soup.find('tbody', id='mrc_main_table')
    print(unique_charge_table)
    print("*************")
    print()
    unique_charge_table_items = unique_charge_table.find_all('td')
 
    temp = []
    for item in unique_charge_table_items:
        temp.append(item.text)
    
    charge_no = 0
    for i in range(0, len(temp), 7):
        aadm_dic[id_index]['Charges'].append({
            'Arresting Agency': temp[i].strip(),
            'Grade of Charge': temp[i + 1],
            'Charge Description': temp[i + 2],
            'Bond Amount': temp[i + 3],
        })
        if (aadm_dic[id_index]['Charges'][int(charge_no)]['Bond Amount'] == '$0.00' or aadm_dic[id_index]['Charges'][int(charge_no)]['Bond Amount'] == '$' or aadm_dic[id_index]['Charges'][int(charge_no)]['Bond Amount'] == ''):
            aadm_dic[id_index]['Charges'][int(charge_no)]['Disqualifies'] = True
            aadm_dic[id_index]['Qualifies'] = 0
        else:
            aadm_dic[id_index]['Charges'][int(charge_no)]['Disqualifies'] = False
        
        charge_no = charge_no + 1
    
    id_index = id_index + 1
 
df = pd.json_normalize(aadm_dic, 'Charges', ['MID', 'Name', 'Url', 'Qualifies'])
df.to_csv("aadm_db.csv")