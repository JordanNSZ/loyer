import pandas as pd
import numpy as np
import re

def save_pages(pages):
    """This write the HTML content of each pages in bytes. There will be one HTML document per page ; 
    the HTML document is stored in the 'data' file.
    Args: 
        pages : list of pages' source code (UTF-8)
    Returns: 
    """
    if not os.path.isdir("data"):
        os.makedirs("data")
    #os.makedirs("data", exist_ok=True)

    for page_nb, page in enumerate(pages):
        with open(f"data/page_{page_nb}", "wb") as f_out:
            f_out.write(page)

def pages_parser():
    """This parses pages in order to extract, transform and load information from each page.

    Returns:
        pd.DataFrame : cleaned and transformed data from each page.
    """
    paths = os.listdir('data/')
    results = pd.DataFrame()
    
    for page_path in paths:
        with open('data/' + page_path, 'rb') as f_in:
            page = f_in.read().decode('utf-8')
            result = parse_page(page)
            #results = results.append(result)
            results = pd.concat([results, result], ignore_index=True)
            
    results.to_csv('loyer_lyon.csv', index=False)
    
def parse_page(page):
    """Parses data from a HTML page and return it as a dataframe
    The parsed data for each property advertisement is :
    - loyer € (rent)
    - type
    - surface (m2) (area)
    - …

    Args:
	    page : utf-8 encoded html page
    Returns:
	    pd.DataFrame: cleaned and transformed data
    """
    soup = BeautifulSoup(page, 'html.parser')
    soup = soup.find("section", attrs = {'class' : 'offerListSection pageContainer'})

    result = pd.DataFrame()
    result['housing_type'] = [clean_type(tag) for tag in soup.find_all(attrs={'class' : 'announceDtlInfosPropertyType'})]
    result['price'] = [clean_price(tag) for tag in soup.find_all(attrs={'class' : 'announceDtlPrice'})]
    result['nbr_rooms'] = [clean_nbrooms(tag) for tag in soup.find_all(attrs={'class' : 'announceDtlInfosNbRooms'})]
    result['area'] = [clean_area(tag) for tag in soup.find_all(attrs={'class' : 'announceDtlInfos announceDtlInfosArea'})]
    result['location'] = [clean_location(tag) for tag in soup.find_all(attrs={'class' : 'announcePropertyLocation'})]
    #result['description'] = [clean_description(tag) if tag != "" else "" for tag in soup.find_all(attrs={'class' : 'announceDtlDescription'})]

    return result

	
def clean_type(tag):
    text = tag.text.strip().replace('Location ', "")
    return text

def clean_price(tag):
    text = tag.text.strip()
    text = text.replace('\xa0', '') #remove non-breaking space between amount and €
    price = int(text.replace("€", "").replace(" ", ""))
    return price

def clean_nbrooms(tag):
    text = tag.text.strip()
    nb_rooms = int(text.split()[0])
    return nb_rooms
	
def clean_area(tag):
    text = tag.text.strip()
    surface = int(text.replace("m²", ""))
    return surface
	
def clean_location(tag):
    text = tag.text.strip()
    match = re.match(r".*\(([0-9]{5})\).*", text)
    if match is None:
        area = 'around_lyon'
        return area
    else:
        return match.group()[0]
"""		
def clean_description(tag):
    text = tag.text.strip()
    return text
    #si pb avec données vides essayer un if else comme pour area
    #e.g. if not tag: description = "" return description else: description=tag.test.strip() return description
    # peut être moins complexe en terme de logique que le if else de la compréhension de liste. 


def main():
    pages=get_pages(start = 1, stop = 2)
    save_pages(pages)
    pages_parser()

if __name__ == "__main__":
    main()
"""
