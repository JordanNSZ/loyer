import os
import time

from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_proxy(url_proxies = "https://free-proxy-list.net/"):
    """
    This function scraps proxy from a well-know website.
    It returns a dataframe containing elements for defining proxies and the proxies.  
    Args : 
    - url : the url to access the table of proxies to scrap.
    Returns :
    - proxy_list : a dataframe of https-compatbile proxies and elements relative to their definition such as 'IP Address' or 'Port'. . 
    """
    response = requests.get(url_proxies)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
	
    table = soup.find('table')
	
    header_row = table.find('tr') 
    columns = [cell.get_text(strip=True) for cell in soup.find('table').find_all('th')]

    data = []
    for row in table.find_all('tr')[1:]:  
        row_data = [cell.get_text(strip=True) for cell in row.find_all(['td'])]
        data.append(row_data)

    proxies = pd.DataFrame(data = data, columns=columns)
        
    proxies = proxies[proxies["Https"] == "yes"]
    
    proxies['url'] = "http://" + proxies["IP Address"] + ":" + proxies["Port"].astype('str')
    proxies.to_csv('proxies.csv', index=False)
	
    return proxies

def usable_proxies(proxies, url = "https://httpbin.org/ip"):
    """
    This function enables to retrieve active and https compatbile proxies from a dataframe containing some proxies. 
    It returns a set of usable proxies. 
    Args:
    - url : str, url of the website to test the proxy.
    - proxies : a dataframe where proxies are stocked. 
    Returns:
    - good_proxies, a set of active-https compatible proxies. 
    """
    good_proxies = set()

    for proxy in proxies["url"]:
        proxies = {"http": proxy,"https": proxy}
        try:
            reponse = requests.get(url, proxies=proxies, timeout=2)
            good_proxies.add(proxy)
            print(f"Le proxy {proxy} fonctionne.")
        except Exception:
            print(f"Le proxy {proxy} ne fonctionne pas.")

    return good_proxies
	

def get_pages(start=1, stop=1):
    """This access the page source of a web site. First it loads the proxies and search for the active ones. Then it tries to access the html code of the page 
    as long as the process hasen't succeed and the set of good proxies isn't empty. Finally, it produces a series of status messages: whether the page has been successfully 
    scraped and how many pages remain to be scraped. 

    Args: 
	    start : the first page to scrap (int).
        stop : the number of pages to be extracted after the first page (int).
    Returns: 
        pages : list of all pages' source code (UTF-8 encoded).
    """ 

    pages = []

    for page_nb in range(start, stop+1):
        proxies = get_proxy()
        good_proxies = usable_proxies(proxies=proxies)
        page_scraped = False
        
        while not page_scraped and len(proxies) > 0:
            
        #try:
            proxy = good_proxies.pop().replace("http://", "")
            firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
            firefox_capabilities['marionette'] = True
            firefox_capabilities['proxy'] = {
                                   "proxyType" : "MANUAL",
                                   "httpProxy": proxy,
                                   "sslProxy" : proxy
                                   }

            driver = webdriver.Firefox(capabilities = firefox_capabilities)
            page_url = f"https://www.logic-immo.com/location-immobilier-lyon-tous-codes-postaux,422_99/options/groupprptypesids=1,2,6,7/page={page_nb}"
            try:
                driver.get(page_url)
                time.sleep(15)
                pages.append(driver.page_source.encode('utf-8'))
                time.sleep(15)
                
                print(f"Page {page_nb} has been scraped!")
                driver.quit()
                
                page_scraped=True
                start += 1

            except Exception:
                print("Proxy doesn't work; trying the next one.")
        #except KeyError:
            #print("The set of proxies is empty !") ca n'est pas possible...
        
        if not page_scraped:
            print(f"Failed to scrape page {page_nb}. Moving to the next page.")
            
        if not len(proxies):
            print("No active proxies to use. The proxy search will resume.")
        
        if start < stop:
            print(f"Remains {stop-start} pages to scrap! \n Scraping stops at page {page_nb}.")
        elif start == stop:
            print(f"Remains {1} page to scrap!")
        else :
            print(f"All done: {stop} pages have been scraped!")

    return pages
