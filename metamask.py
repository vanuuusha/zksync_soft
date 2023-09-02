import os.path
import time
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from SeleniumMain import SeleniumArb
from config import ALLOW_NET
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import requests
import shutil
from functools import wraps
from inner_funcs import print_with_time
import logging.config
from logger_configs import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
error_logger = logging.getLogger('error_logger')


class Metamask(SeleniumArb):
    def __init__(self, seed_phrase, show_display, proxy):
        self.show_display = show_display
        self.proxy = proxy
        self.seed_phrase = seed_phrase
        self.password = '25692569'
        self.ext_path = 'files/meta/metamask-chrome-10.3.0'
        self.ext_id = 'nkbihfbeogaeaoehlefnkodbefgpgknn'
        self.added_networks = []
        # self.download_metamask()

        self.open_chrome_with_metamask()
        self.register_to_metamask()

    @staticmethod
    def _metamask_confirm(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            time.sleep(2)
            current_handle = self.driver.current_window_handle
            self.driver.switch_to.window(self.metamask_handle)
            self.driver.get(self.metamask_url)
            func(self, *args, **kwargs)
            self.driver.switch_to.window(current_handle)
        return inner

    @staticmethod
    def _metamask_confirm_long(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            time.sleep(5)
            current_handle = self.driver.current_window_handle
            self.driver.switch_to.window(self.metamask_handle)
            self.driver.get(self.metamask_url)
            func(self, *args, **kwargs)
            self.driver.switch_to.window(current_handle)

        return inner

    def download_metamask(self):
        with requests.get('https://github.com/MetaMask/metamask-extension/releases/download/v10.3.0/metamask-chrome-10.3.0.zip', stream=True) as r:
            with open(self.ext_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

    def open_chrome_with_metamask(self):
        chrome_driver_path = 'files/chromedriver-win64/chromedriver-win64/chromedriver.exe'
        chrome_service = Service(executable_path=chrome_driver_path)
        if self.proxy:
            from seleniumwire import webdriver
        else:
            from selenium import webdriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-site-isolation-trials")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        from fake_useragent import UserAgent
        ua = UserAgent()
        chrome_options.add_argument(f"--user-agent={ua.chrome}")
        chrome_options.add_argument(f'--load-extension={os.path.abspath(os.path.join("files", "meta", "metamask-chrome-10.3.0"))}')
        if not self.show_display:
            chrome_options.add_argument("--headless=new")

        if self.proxy:
            options = {
                'proxy': {
                    'http': f'http://{self.proxy["login"]}:{self.proxy["password"]}@{self.proxy["ip"]}:{self.proxy["port"]}',
                    'https': f'https://{self.proxy["login"]}:{self.proxy["password"]}@{self.proxy["ip"]}:{self.proxy["port"]}',
                    'no_proxy': 'localhost,127.0.0.1',
                }
            }
            print(f'Использую прокси: {self.proxy["ip"]}:{self.proxy["port"]}')
            self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options, seleniumwire_options=options)
        else:
            self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        self.driver.set_window_size(1720, 1280)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: function() {return false}})")
        self.little_wait = WebDriverWait(self.driver, 5, 1)
        self.wait = WebDriverWait(self.driver, 10, 1)
        self.big_wait = WebDriverWait(self.driver, 30, 1)
        self.wait.until(EC.number_of_windows_to_be(2))
        self.metamask_handle = self.driver.window_handles[1]
        self.driver.switch_to.window(self.metamask_handle)
        self.driver.refresh()
        self.wait.until(EC.url_contains('home'))
        self.metamask_url = self.driver.current_url.split('#')[0]

    def register_to_metamask(self):
        time.sleep(2)
        self.driver.refresh()
        time.sleep(2)
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/button'))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div[2]/div/div[2]/div[1]/button'))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/div/div[5]/div[1]/footer/button[1]'))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.first-time-flow__textarea-wrapper input')))
        inputs = [self.driver.find_element(By.CSS_SELECTOR, "div.first-time-flow__textarea-wrapper input"), self.driver.find_element(By.XPATH, '//*[@id="password"]'), self.driver.find_element(By.XPATH, '//*[@id="confirm-password"]')]
        inputs[0].send_keys(self.seed_phrase)
        inputs[1].send_keys(self.password)
        inputs[2].send_keys(self.password)
        self.click(self.driver.find_element(By.CSS_SELECTOR, '.first-time-flow__terms.first-time-flow__checkbox'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/form/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/form/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/form/button'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div/button'))

    @staticmethod
    def change_network_wrapper(func):
        retry = 0
        def inner(self, name):
            nonlocal retry
            try:
                func(self, name)
            except Exception:
                retry += 1
                if retry == 3:
                    print_with_time('Не удалось сменить сеть')
                    raise Exception
                else:
                    self.driver.close()
                    self.driver.switch_to.window(self.metamask_handle)
                    inner(self, name)
        return inner

    @change_network_wrapper
    def change_network(self, name):
        self.open_page(ALLOW_NET[name]['url'])
        time.sleep(10)
        self.click(self.driver.find_element(By.XPATH, ALLOW_NET[name]['xpath']))
        if name not in self.added_networks:
            if len(self.added_networks) == 0:
                self.connect_to_site()
            time.sleep(5)
            self._change_network()
            self.added_networks.append(name)
        else:
            self.change_exsists_network(name)
        self.driver.close()
        self.driver.switch_to.window(self.metamask_handle)

    @_metamask_confirm
    def change_exsists_network(self, name):
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/button[2]'))

    @_metamask_confirm
    def _change_network(self):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/button[2]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/button[2]'))
        time.sleep(0.5)
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/button[2]'))

    @_metamask_confirm
    def connect_to_site(self):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[4]/div[2]/button[2]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[4]/div[2]/button[2]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[4]/div[2]/button[2]'))
        time.sleep(0.5)
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]'))

    @_metamask_confirm_long
    def approve(self):
        was_approved = False
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/button[2]')))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/button[2]')))
            self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/button[2]'))
            was_approved = True
        except TimeoutException:
            pass


        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]')))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]')))
            self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]'))
            was_approved = True
        except TimeoutException:
            pass

        if not was_approved:
            pass

    @_metamask_confirm_long
    def confirm_tx(self):
        was_confirm = False

        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/div[3]/footer/button[2]')))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/div[3]/footer/button[2]')))
            self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/div[3]/footer/button[2]'))
            was_confirm = True
        except TimeoutException:
            pass

        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//button[text()="Confirm"]')))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Confirm"]')))
            self.click(self.driver.find_element(By.XPATH, '//button[text()="Confirm"]'))
            was_confirm = True
        except TimeoutException:
            pass

        try:
            self.little_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]')))
            self.little_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]')))
            self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]'))
            was_confirm = True
        except TimeoutException:
            pass

        if not was_confirm:
            raise Exception('Не удался конфирм')

    @_metamask_confirm
    def withdraw_eth(self, count_eth, to):
        self.little_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div/div/div[2]/div/div[2]/button[2]/div')))
        self.little_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div/div/div[2]/div/div[2]/button[2]/div')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div/div/div[2]/div/div[2]/button[2]/div'))
        self.little_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div')))
        self.little_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div')
        elem.send_keys(to)
        self.little_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/div/div[3]/div[2]/div[1]/div/div[1]/div[1]/input')))
        self.little_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/div/div[3]/div[2]/div[1]/div/div[1]/div[1]/input')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/div/div[3]/div[2]/div[1]/div/div[1]/div[1]/input')
        elem.send_keys(count_eth)
        self.little_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]')))
        self.little_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[2]'))
        self.confirm_tx()
