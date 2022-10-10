import requests
import string
import json
from bs4 import BeautifulSoup


def scrape_rxassist():
    '''
    Scrape the list of all drug brand names from RxAssist.org

        Returns:
            brand_list (list): list of all drug brand names on the site table
    '''

    # Get the site content
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
    }
    response = requests.get(
        'https://www.rxassist.org/pap-info/brand-drug-list-print',
        headers=headers     # include because the site seems to block traffic from a typical req
    )

    # Parse and navigate the html
    soup = BeautifulSoup(response.content, 'lxml')
    inner_table = soup.find('table').find('table')
    rows = inner_table.find_all('td')   # array of each row of the table on the site
    brand_elements = rows[::2]  # take every 2 data points because 2 columns in the table
    brand_list = [brand_element.font.contents[0] for brand_element in brand_elements]

    return brand_list


def scrape_rxlist():
    '''
    Scrape the drug brand names available from RxList.com

        Returns:
            brand_list (list): list of all drug brand names available throughout the site
    '''

    # This list will store all the names we accumulate
    brand_list = []

    # This site has info split across many pages so first define our outer loop links
    links = [
        f'https://www.rxlist.com/drugs/alpha_{letter}.htm' 
        for letter in list(string.ascii_lowercase)
    ]

    # Iterate through each letter in alphabet
    for link in links:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'lxml')
        brand_elements = soup.find(class_='AZ_results').find_all('li')

        # Iterate through each drug page
        for link_brand in brand_elements:
            link_brand = link_brand.a.get('href')
            response_brand = requests.get(link_brand)
            soup_brand = BeautifulSoup(response_brand.content, 'lxml')

            # Get brand name from the page and add it to the ongoing list
            info = soup_brand.find(class_='hero')
            brand_name_elem = info.find_all('li')[1]
            brand_name = brand_name_elem.find('span').contents
            brand_list += brand_name

    return brand_list


def main():
    '''Main execution function: saves lists of names from each site as JSON files.'''

    # RxAssist.org
    list_rxassist = scrape_rxassist()
    with open('raw/names_rxassist.json', 'w') as f:
        json.dump(list_rxassist, f)

    # RxList.com
    list_rxlist = scrape_rxlist()
    with open('raw/names_rxlist.json', 'w') as f:
        json.dump(list_rxlist, f)


if __name__ == '__main__':
    main()
