import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from _Proxies import ProxiesCrawler
import random
import time
import re
import json
from selenium import webdriver


# Get names of all countries
def get_country_list():
    try:
        countries_list = []
        url = "https://www.theswiftcodes.com/browse-by-country/"
        time.sleep(1)
        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        country_ol_list = soup.find_all('ol', attrs={'class':'country'})
        for country_list in country_ol_list:
            countries = country_list.find_all('a')
            for country_data in countries:
                country = country_data.get_text()
                # convert single space to (-) for url
                country = str(country).replace(' ', '-')
                # for unique name
                if(country.lower() not in countries_list):
                    countries_list.append(country.lower())
        return countries_list
    except Exception as er:
        print(er)

# Check page number is more than one or not
def check_page_num(url, country_name):
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        RandomProxy = random.choice(ALL_PROXIES)
        print(f"Using Proxy: '{RandomProxy}', to scrape data: ")
        html_doc = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        # functionality of checking page number
        navigation = soup.find_all('div', attrs={'class':'navigation'})
        try:
            next_buttons = navigation[1].find_all('span', attrs={'class':'next'})
            if(next_buttons):
                a = next_buttons[1].find('a')
                a_str = a['href']
                # find number from given string using Regex
                match = re.search(r'/\d+/', a_str)
                num = int(match.group(0)[1:-1])
                return num
            else:
                False
        except Exception as e:
            pass
        
    except Exception as er:
        print(er)

# Get All pages data into a list and return it
def get_all_countries_data(country_names):
    try:
        JsonData = []
        for country_name in country_names:
            # GET IBAN STRUCTURE USING SELENIUM
            # ua = UserAgent()
            # print(f"Using selenium to scrape data: ")
            # time.sleep(1)
            # options = webdriver.ChromeOptions()
            # # Open in headless mode
            # options.add_argument('--headless')
            # options.add_argument(f'user-agent={ua.random}')
            # driver = webdriver.Chrome(options=options)
            # driver.implicitly_wait(10)
            # link = f'https://bank.codes/iban/structure/{country_name}/'
            # time.sleep(1)
            # driver.get(link)
            # soup = BeautifulSoup(driver.page_source, 'html.parser')
            # iban_div = soup.find('div', attrs={'class':'iban'})
            # iban_str = ''
            # if(iban_div):
            #     spans = iban_div.find_all('span')
            #     for span in spans:
            #         iban_str += span.get_text().strip()
            #     # print(iban_str)
            # driver.close()
            # ---------------------------------
            # temp_dict = {"swift_codes": []}
            # JsonData.append(temp_dict)

            url = f'https://www.theswiftcodes.com/{country_name}/'
            # Check Page Number is more than one or not
            pageNum = check_page_num(url,country_name)
            page_no = 1
            print(country_name)
            if(pageNum):
                while page_no <= pageNum:
                    try:
                        if(page_no != 1):
                            url = f'https://www.theswiftcodes.com/{country_name}/page/{page_no}/'

                        ua = UserAgent()
                        headers = {'User-Agent': ua.random}
                        RandomProxy = random.choice(ALL_PROXIES)
                        print(f"Using Proxy: '{RandomProxy}', to scrape data: ")
                        time.sleep(1)
                        html_doc = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers).text
                        soup = BeautifulSoup(html_doc, 'html.parser')
                        table = soup.find('table', attrs={'class':'swift-country'}).tbody
                        table_row = table.find_all("tr")
                        for tr in table_row:
                            table_data = tr.find_all("td")
                            bank = table_data[1].get_text().strip()
                            city = table_data[2].get_text().strip()
                            branch = table_data[3].get_text().strip()
                            swift_code = table_data[4].a.get_text().strip()
                            # store in list of JsonData
                            temp_dict = {'country':f'{str(country_name).capitalize()}',"bank": f"{bank}", "city": f"{city}", "branch": f"{branch}", "swiftCode": f"{swift_code}"}
                            # temp_dict['swift_codes'].append(temp_dict_2)
                            JsonData.append(temp_dict)

                        print(page_no)
                        page_no += 1
                    except Exception as e:
                        print(e)
                        continue

            else:
                ua = UserAgent()
                headers = {'User-Agent': ua.random}
                RandomProxy = random.choice(ALL_PROXIES)
                print(f"Using Proxy: '{RandomProxy}', to scrape data: ")
                time.sleep(1)
                html_doc = requests.get(url, proxies={RandomProxy[1]:RandomProxy[0]}, headers=headers).text
                soup = BeautifulSoup(html_doc, 'html.parser')
                table = soup.find('table', attrs={'class':'swift-country'}).tbody
                table_row = table.find_all("tr")
                for tr in table_row:
                    table_data = tr.find_all("td")
                    bank = table_data[1].get_text().strip()
                    city = table_data[2].get_text().strip()
                    branch = table_data[3].get_text().strip()
                    swift_code = table_data[4].a.get_text().strip()
                    # store in list of JsonData
                    temp_dict = {'country':f'{str(country_name).capitalize()}',"bank": f"{bank}", "city": f"{city}", "branch": f"{branch}", "swiftCode": f"{swift_code}"}
                    JsonData.append(temp_dict)

            print('--------------------\n')
        return JsonData
            
    except Exception as er:
        print(er)
        return JsonData


if __name__ == '__main__':
    # Get valid proxies
    ALL_PROXIES = ProxiesCrawler().get_proxies(0,10)
    # Get names of all countries
    country_list = get_country_list()
    if(country_list):
        json_data = get_all_countries_data(country_list)
        if(json_data):
             # Directly exporting to JSON
            with open("json_data/data.json", "w", encoding='utf-8') as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)
    