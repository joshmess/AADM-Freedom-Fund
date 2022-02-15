from bs4 import BeautifulSoup as bs
from datetime import datetime
import concurrent.futures
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selectorlib import Extractor
import time
import re

aadm_dic = {}
acc_links = []
acc_mids = []
acc_names = []

def main():
    startTime = datetime.now()
    acc_soup = getSoup()
    getLinksAndMIDS(acc_soup)
    buildDictionary()
    addCharges_Base()
    print(datetime.now() - startTime)
    print(aadm_dic)


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
    driver = webdriver.Chrome(ChromeDriverManager().install())
    acc_url = "http://enigma.athensclarkecounty.com/photo/jailcurrent.asp"
    driver.get(acc_url)
    soup = bs(driver.page_source, 'lxml')
    print("Finished getting lxml content")
    return soup

def addCharges_Base():
    threads = 4
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(addCharges_Thread, acc_links)

def addCharges_Thread(link):
    try:
        threaded_driver = webdriver.Chrome(ChromeDriverManager().install())

        m = re.search("id=-(.+?)&", link)
        mid = str(m.group(1))

        charges_page = threaded_driver.get(link)
        timeout = 120
        element_present = EC.presence_of_element_located((By.ID, 'mrc_main_table'))
        WebDriverWait(threaded_driver, timeout).until(element_present)
    except TimeoutException:
        print(mid + " Timed Out Waiting for Page to Load")
        return
    finally:
        print("Loaded Page for " + mid)

        charges_soup = bs(charges_page.page_source, 'lxml')

        charges_table = charges_soup.find('tbody', id='mrc_main_table')
        charges_table_items = charges_table.find_all('td')

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