from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--headless")

    # add option current user data dir
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    # add user agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # add download directory
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    })
    return driver

def create_driver_unvisible():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--headless")
    # add measure of monitor size to avoid detection
    chrome_options.add_argument("window-size=1920,1080")

    # nessary options for headless mode to work properly with selenium for avoiding bot detection
    # User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0
    # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    # Accept-Language: en-US,en;q=0.5
    # Accept-Encoding: gzip, deflate, br, zstd
    # Connection: keep-alive
    # Cookie: _gcl_au=1.1.1988704317.1737913622; _ga_CG23NQ5S7K=GS1.1.1738508275.14.1.1738508944.0.0.0; _ga=GA1.1.1305428397.1737913622; _fbp=fb.1.1737913623246.569777362721416273; _ga_VY0CL36YRE=GS1.1.1738513112.9.1.1738513524.0.0.0; _tt_enable_cookie=1; _ttp=cgiDu68b_vPLostWriAXZplmjWK.tt.1; AcceptCookies=Yes; nlbi_2784046=b7x+E9C07GUnBimdHmvmiAAAAAA1rmtT1EkswMo7bNfxzqUL; incap_ses_878_2784046=K8ljCDxoBBty7PKSd0gvDOGan2cAAAAArnxDx++PHG2f/tlzyf3PcA==; ASPSESSIONIDAGBARCQT=NGKOGNPAMLCCDGEMHCLPENDK; nlbi_2836327=Mkr3MaDC4i6R5NC8rGmgIAAAAACYN4G+ETvvdrIsX/V2QCoy; incap_ses_878_2836327=tJSYcv+Wz2vl6vKSd0gvDOCan2cAAAAAY1Gj0/MECU0ksBTJyLpp6Q==; ASPSESSIONIDAGBCQBQT=FEAIFJMBPBHFDACPMCBMHMFC; ASPSESSIONIDCECDTBQS=ABCNDFJCJFLLJJIKGHDFLFCE; ASPSESSIONIDCGBCSBQT=EILACBGDIMBKACANBPHNGGMA; visid_incap_2836327=ymP+RQ+9SAOGeldxZecquFqJn2cAAAAAQkIPAAAAAADVA1xb/iqLnERUAq8hzNpo
    # Upgrade-Insecure-Requests: 1
    # Sec-Fetch-Dest: document
    # Sec-Fetch-Mode: navigate
    # Sec-Fetch-Site: cross-site
    # Priority: u=0, i
    # Pragma: no-cache
    # Cache-Control: no-cache
    # TE: trailers
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0")
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
    # add user agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # add download directory
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    })
    return driver

def close_driver(driver):
    driver.quit()