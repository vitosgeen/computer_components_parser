
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
import time

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

        driver = webdriver.Chrome(options=options)
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

def download_file(url, type='get', data_post=None, headers=None, sleep_time=0):
    #get hash of url
    hash = hashlib.md5(url.encode()).hexdigest()
    if type == 'post':
        hash = hashlib.md5((url + str(data_post)).encode()).hexdigest()
    
    # check if file exists
    if os.path.exists(f'./downloads/{hash}'):
        return read_file(f'./downloads/{hash}')
    
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
                response = requests.get(url, headers=headers)
            elif type == 'post':
                response = requests.post(url, data=data_post, headers=headers)
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