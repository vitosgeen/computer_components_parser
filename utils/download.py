
import hashlib
import os
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

import urllib3

def download_file_by_selenium(url):

    # get hash of url
    hash = hashlib.md5(url.encode()).hexdigest()

    # check if file exists
    if os.path.exists(f'./downloads/{hash}'):
        return read_file(f'./downloads/{hash}')

    # create dir
    create_dir()

    # download file
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-features=NetworkService")
        options.add_argument("--disable-features=NetworkServiceInProcess")
        options.add_argument("--disable-features=IsolateOrigins")

        # set user agent
        options.add_argument(f'user-agent={get_random_user_agent()}')
        options.binary_location = "/usr/bin/google-chrome"

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(5)
        content = driver.page_source
        driver.quit()

    except Exception as e:
        print(e)
        return None
    
    # save file
    try:
        with open(f'./downloads/{hash}', 'w') as file:
            file.write(content)
    except Exception as e:
        print(e)
        return None
    
    return read_file(f'./downloads/{hash}')


def download_file_by_selenium_unvisible(url):

    # get hash of url
    hash = hashlib.md5(url.encode()).hexdigest()

    # check if file exists
    if os.path.exists(f'./downloads/{hash}'):
        return read_file(f'./downloads/{hash}')

    # create dir
    create_dir()

    # download file
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-features=NetworkService")
        chrome_options.add_argument("--disable-features=NetworkServiceInProcess")
        chrome_options.add_argument("--disable-features=IsolateOrigins")
        chrome_options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        chrome_options.add_argument("accept-language=en-US,en;q=0.5")
        chrome_options.add_argument("accept-encoding=gzip, deflate, br, zstd")
        chrome_options.add_argument("connection=keep-alive")
        # chrome_options.add_argument("cookie=_gcl_au=1.1.1988704317.1737913622; _ga_CG23NQ5S7K=GS1.1.1738508275.14.1.1738508944.0.0.0; _ga=GA1.1.1305428397.1737913622; _fbp=fb.1.1737913623246.569777362721416273; _ga_VY0CL36YRE=GS1.1.1738513112.9.1.1738513524.0.0.0; _tt_enable_cookie=1; _ttp=cgiDu68b_vPLostWriAXZplmjWK.tt.1; AcceptCookies=Yes; nlbi_2784046=b7x+E9C07GUnBimdHmvmiAAAAAA1rmtT1EkswMo7bNfxzqUL; incap_ses_878_2784046=K8ljCDxoBBty7PKSd0gvDOGan2cAAAAArnxDx++PHG2f/tlzyf3PcA==; ASPSESSIONIDAGBARCQT=NGKOGNPAMLCCDGEMHCLPENDK; nlbi_2836327=Mkr3MaDC4i6R5NC8rGmgIAAAAACYN4G+ETvvdrIsX/V2QCoy; incap_ses_878_2836327=tJSYcv+Wz2vl6vKSd0gvDOCan2cAAAAAY1Gj0/MECU0ksBTJyLpp6Q==; ASPSESSIONIDAGBCQBQT=FEAIFJMBPBHFDACPMCBMHMFC; ASPSESSIONIDCECDTBQS=ABCNDFJCJFLLJJIKGHDFLFCE; ASPSESSIONIDCGBCSBQT=EILACBGDIMBKACANBPHNGGMA; visid_incap_2836327=ymP+RQ+9SAOGeldxZecquFqJn2cAAAAAQkIPAAAAAADVA1xb/iqLnERUAq8hzNpo")
        chrome_options.add_argument("upgrade-insecure-requests=1")
        chrome_options.add_argument("sec-fetch-dest=document")
        chrome_options.add_argument("sec-fetch-mode=navigate")
        chrome_options.add_argument("sec-fetch-site=cross-site")
        chrome_options.add_argument("priority=u=0, i")
        chrome_options.add_argument("pragma=no-cache")
        chrome_options.add_argument("cache-control=no-cache")

        # add option current user data dir
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        # set user agent
        chrome_options.add_argument(f'user-agent={get_random_user_agent()}')
        # add download directory
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.binary_location = "/usr/bin/google-chrome"

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        time.sleep(5)
        content = driver.page_source
        driver.quit()

    except Exception as e:
        print(e)
        return None
    
    # save file
    try:
        with open(f'./downloads/{hash}', 'w') as file:
            file.write(content)
    except Exception as e:
        print(e)
        return None
    
    return read_file(f'./downloads/{hash}')

def download_file(url, type='get', data_post=None, headers=None, sleep_time=0, verify=None):
    #get hash of url
    hash = hashlib.md5(url.encode()).hexdigest()
    if type == 'post':
        hash = hashlib.md5((url + str(data_post)).encode()).hexdigest()
    
    # check if file exists
    if os.path.exists(f'./downloads/{hash}'):
        return read_file(f'./downloads/{hash}')
    
    if headers is None:
        headers = {
            'User-Agent': get_random_user_agent()
        }

    if verify == False:
        urllib3.disable_warnings()

    # create dir
    create_dir()
    
    # sleep for a few seconds
    if sleep_time > 0:
        time.sleep(sleep_time)

    # download file with a few attempts
    attempt = 0
    while attempt < 3:
        try:
            if type == 'get':
                response = requests.get(url, headers=headers, verify=verify)
            elif type == 'post':
                response = requests.post(url, data=data_post, headers=headers, verify=verify)
            else:
                return None
            break
        except Exception as e:
            print(e)
            attempt += 1
            time.sleep(5)
            continue
    
    # save file
    try:
        with open(f'./downloads/{hash}', 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(e)
        return None

    return read_file(f'./downloads/{hash}')

def create_dir():
    try:
        if not os.path.exists('./downloads'):
            os.makedirs('./downloads')
    except Exception as e:
        print(e)

def read_file(file):
    try:
        with open(file, 'r') as f:
            content = f.read()
            return content
    except Exception as e:
        print(e)
        return None

def get_random_user_agent():
    user_agents = collection_of_user_agents()
    return user_agents[random.randint(0, len(user_agents)-1)]

def collection_of_user_agents():
    return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    ]

def save_content_to_file(content, file):
    try:
        with open(file, 'w') as f:
            f.write(content)
    except Exception as e:
        print(e)
        return None