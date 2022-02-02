from bs4 import BeautifulSoup as bs
from datetime import datetime
import concurrent.futures
import requests
import pymongo
import re

aadm_dic = {}
acc_links = []
acc_mids = []
acc_names = []
requests_session = requests.Session()
client = pymongo.MongoClient("mongodb+srv://admin:admin@aadmtest.yer5q.mongodb.net/aadm_test?retryWrites=true&w=majority")
db = client.aadm_test
jailed = db.jailed

def main():
    startTime = datetime.now()
    acc_soup = getSoup()
    getLinksAndMIDS(acc_soup)
    buildDictionary()
    addCharges_Base()
    print(datetime.now() - startTime)
    print(aadm_dic)
    jailed.insert_many(aadm_dic)


# begin assembling skeleton of Dictionary
def buildDictionary():
    [addMIDToDict(i, mid) for i, mid in enumerate(acc_mids)]
    print("Finished building dictionary")

def addMIDToDict(i, mid):
    aadm_dic[str(mid)] = {
        'MID': mid,
        'Name': acc_names[i],
        'Url': acc_links[i],
        'Charges': []
    }

# get links and MIDs of every jailed person
def getLinksAndMIDS(ACC_SOUP):
    a_tags = ACC_SOUP.find_all('a')
    [tag_comp(tag) for tag in a_tags]
    print("Finished getting links and MIDs")

def tag_comp(tag):
    acc_names.append(tag.text)
    m = re.search("'(.+?)'", tag['onclick'])
    if m:
        link = 'http://enigma.athensclarkecounty.com/photo/' + m.group(1)
        acc_links.append(link)
        m = re.search("id=-(.+?)&", link)
        if m:
            acc_mids.append(int(m.group(1)))

# get content of base page
def getSoup():
    acc_url = "http://enigma.athensclarkecounty.com/photo/jailcurrent.asp"
    print("Finished getting lxml content")
    return bs(requests_session.get(acc_url).content, 'lxml')

def addCharges_Base():
    threads = 4
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(addCharges_Thread, acc_links)

def addCharges_Thread(link):
    charges_page = requests_session.get(link)
    charges_soup = bs(charges_page.content, 'lxml')
    charges_table = charges_soup.find('tbody', id='mrc_main_table')
    charges_table_items = charges_table.find_all('td')

    m = re.search("id=-(.+?)&", link)
    mid = str(m.group(1))

    temp = list(map(lambda x: x.text, charges_table_items))

    for i in range(0, len(temp), 7):
        if (temp[i + 3] == "$0.00" or temp[i + 3] == "$" or temp[i + 3] == ""):
            print(mid + " is disqualified -- link: " + link + " -- Had Invalid Bond Amount: " + temp[i + 3])
            del(aadm_dic[mid])
            return
        else:
            aadm_dic[mid]['Charges'].append({
                'Arresting Agency': temp[i].strip(),
                'Grade of Charge': temp[i + 1],
                'Charge Description': temp[i + 2],
                'Bond Amount': temp[i + 3],
            })
    print(mid + " qualifies")
    return

if __name__ == "__main__":
    main()