import time
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from metamask import Metamask
from config import URLS, MUTE_CONFIGS, SYNCSWAP_CONFIGS, INFO, SPACEFI_CONFIGS, PANCAKE_CONFIGS, MAV_CONFIGS
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from functools import wraps


class Trader(Metamask):
    def __init__(self, seed_phrase, show_display, proxy):
        self.option_screen = "--window-size=1720,1280"
        self.counters = {}
        try:
            super().__init__(seed_phrase=seed_phrase, show_display=show_display, proxy=proxy)
        except Exception:
            try:
                self.driver.quit()
            except Exception:
                pass
        self.now_sites = {}

    def get_site(self, name, init=True):
        if name in self.now_sites:
            if name == 'space':
                self.open_page(URLS[name])
                self.now_sites[name] = self.driver.current_window_handle
            else:
                self.driver.switch_to.window(self.now_sites[name])
        else:
            self.open_page(URLS[name])
            self.now_sites[name] = self.driver.current_window_handle
            if init:
                self.init_site(name)

    def init_site(self, name, connect=True):
        init_method = self.__getattribute__(name + '_init')
        init_method(connect)

    def mute_init(self, connect):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/header[1]/div[4]/div/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/header[1]/div[4]/div/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div/header[1]/div[4]/div/button'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/button/div/div/div[2]/div')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/button/div/div/div[2]/div')))
        self.click(self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/button/div/div/div[2]/div'))
        self.counters['mute'] = 0
        self.connect_to_site()

    def syncswap_init(self, connect):
        self.syncswap_now_selected = ['ETH', 'USDC']
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.col.align.relative .pointer')))
        self.click(self.driver.find_element(By.CSS_SELECTOR, '.col.align.relative .pointer'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="navi-tool"]/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="navi-tool"]/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="navi-tool"]/button'))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div/div/div/div/div[1]/div[2]/div[1]/div[2]/p'))
        self.connect_to_site()

    def space_init(self, connect):
        self.space_now_selected = ['ETH', '']
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="connect-wallet"]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="connect-wallet"]'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="connect-METAMASK"]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="connect-METAMASK"]'))
        self.connect_to_site()

    def pancake_init(self, connect):
        self.pancake_now_selected = ['ETH', 'CAKE']
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[1]/nav/div[2]/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[1]/nav/div[2]/button'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="portal-root"]/div/div/div[2]/div/div/div/div[2]/div[1]/div[2]/div[1]/div[1]/div/div')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="portal-root"]/div/div/div[2]/div/div/div/div[2]/div[1]/div[2]/div[1]/div[1]/div/div'))
        self.connect_to_site()

    def mav_init(self, connect):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/header[2]/div/div/div/div[2]/div[2]/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="root"]/div/header[2]/div/div/div/div[2]/div[2]/button'))
        container = self.driver.find_element(By.XPATH, "/html/body/onboard-v2")
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', container)
        element_inside_shadow_dom = shadow_root.find_element(By.CSS_SELECTOR, "input")
        self.click(element_inside_shadow_dom)
        time.sleep(0.5)
        self.click(shadow_root.find_element(By.CSS_SELECTOR, 'button'))
        self.connect_to_site()

    def zkswap_init(self, connect):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[3]/div/label/div')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[3]/div/label/div'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/button'))

        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="btnConnectWallet"]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnConnectWallet"]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="btnConnectWallet"]'))

        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="connect-METAMASK"]/div[2]/div')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="connect-METAMASK"]/div[2]/div'))
        time.sleep(5)
        self.connect_to_site()


    def zkbridge_init(self, connect):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__nuxt"]/div/main/div/div[4]/form/div[2]/div[1]/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__nuxt"]/div/main/div/div[4]/form/div[2]/div[1]/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div/main/div/div[4]/form/div[2]/div[1]/button'))

        time.sleep(5)
        cont = self.driver.find_element(By.XPATH, '/html/body/w3m-modal')
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', cont)
        cont1 = shadow_root.find_element(By.CSS_SELECTOR, 'w3m-modal-router')
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', cont1)
        cont2 = shadow_root.find_element(By.CSS_SELECTOR, "w3m-connect-wallet-view")
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', cont2)
        cont3 = shadow_root.find_element(By.CSS_SELECTOR, "w3m-desktop-wallet-selection")
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', cont3)
        cont4 = shadow_root.find_element(By.CSS_SELECTOR, 'w3m-modal-footer .w3m-grid w3m-wallet-button')
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', cont4)
        btn = shadow_root.find_element(By.CSS_SELECTOR, 'button')
        self.click(btn)
        time.sleep(1)
        self.connect_to_site()

    def zkns_init(self, connect):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[1]/div/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[1]/div/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[1]/div/button'))
        self.connect_to_site()

    def orbiter_init(self, connect):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[2]/span')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[2]/span')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[2]/span'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/span')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/span')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div/div[2]/span'))
        self.connect_to_site()

    def eralend_init(self, connect):
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__next"]/header/div/div/div[2]/div/div[1]/button')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/header/div/div/div[2]/div/div[1]/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="__next"]/header/div/div/div[2]/div/div[1]/button'))

        container = self.driver.find_element(By.XPATH, "/html/body/onboard-v2")
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', container)
        agree = shadow_root.find_element(By.CSS_SELECTOR, "input")
        self.click(agree)
        elem = shadow_root.find_element(By.CSS_SELECTOR, '.wallets-container div:first-child button div')
        self.click(elem)
        self.connect_to_site()
        time.sleep(5)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[3]/div[3]/div[2]/div[8]/button')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[1]/div[3]/div[3]/div[2]/div[8]/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[3]/div[3]/div[2]/div[8]/button'))

    def eralend_supply(self, count_eth):
        self.get_site('eralend')
        time.sleep(6)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="simple-tabpanel-0"]/form/div/div[1]/div[1]/div[2]/input')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="simple-tabpanel-0"]/form/div/div[1]/div[1]/div[2]/input')
        for i in str(count_eth):
            elem.send_keys(i)
            time.sleep(0.1)
        time.sleep(3)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="simple-tabpanel-0"]/form/div/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="simple-tabpanel-0"]/form/div/button')))
        self.driver.find_element(By.XPATH, '//*[@id="simple-tabpanel-0"]/form/div/button').click()
        time.sleep(10)
        self.confirm_tx()
        time.sleep(30)
        self.driver.refresh()

    def eralend_withdraw(self, count_eth):
        self.get_site('eralend')
        time.sleep(10)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="markets-modal"]/div/div/div[1]/div/div/button[2]/span')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="markets-modal"]/div/div/div[1]/div/div/button[2]/span')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="markets-modal"]/div/div/div[1]/div/div/button[2]/span')
        self.click(elem)

        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="simple-tabpanel-1"]/form/div/div/div[1]/p[1]')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="simple-tabpanel-1"]/form/div/div/div[1]/div/input')
        for i in str(count_eth):
            elem.send_keys(i)
            time.sleep(0.1)

        time.sleep(5)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="simple-tabpanel-1"]/form/div/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="simple-tabpanel-1"]/form/div/button')))
        self.driver.find_element(By.XPATH, '//*[@id="simple-tabpanel-1"]/form/div/button').click()
        time.sleep(10)
        self.confirm_tx()
        time.sleep(30)
        self.driver.refresh()

    @staticmethod
    def _swap(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            time.sleep(1)
            func(self, *args, **kwargs)
            self.confirm_tx()
            time.sleep(30)

        return inner

    def zkswap_swap(self, token1, count1, token2):
        self.get_site('zkswap')
        try:
            count1 = float(str(count1)[:8])
        except Exception:
            pass
        self.zkswap_change_tokens(token1, count1, token2)
        self.zkswap_approve()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="swap-button"]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="swap-button"]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="swap-button"]'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="confirm-swap-or-send"]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="confirm-swap-or-send"]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="confirm-swap-or-send"]'))
        time.sleep(2)
        self.confirm_tx()
        time.sleep(30)
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/reach-portal[4]/div[2]/div/div/div/div/div/div[2]/button')))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/reach-portal[4]/div[2]/div/div/div/div/div/div[2]/button')))
            self.click(self.driver.find_element(By.XPATH, '/html/body/reach-portal[4]/div[2]/div/div/div/div/div/div[2]/button'))
        except Exception:
            pass
    def zkswap_change_tokens(self, token1, count1, token2):
        tokens = (token1, token2)
        buttons = ('//*[@id="swap-currency-input"]/div/div[2]/button', '//*[@id="swap-currency-output"]/div/div[2]/button')
        for num, btn in enumerate(buttons):
            self.zkswap_chose_token(tokens[num], buttons[num])
        input1 = self.driver.find_element(By.XPATH, '//*[@id="swap-currency-input"]/div/div[2]/input')
        input1.send_keys(Keys.CONTROL + 'a')
        input1.send_keys(Keys.DELETE)
        self.click(input1)
        input1.send_keys(str(count1))

    def zkswap_chose_token(self, token, btn):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, btn)))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, btn)))
        self.click(self.driver.find_element(By.XPATH, btn))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="token-search-input"]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="token-search-input"]')))
        input = self.driver.find_element(By.XPATH, '//*[@id="token-search-input"]')
        input.send_keys(token)
        time.sleep(2)
        container = self.driver.find_element(By.XPATH, '/html/body/reach-portal[4]/div[2]/div/div/div/div/div[3]/div[1]/div/div')
        btn = container.find_element(By.CSS_SELECTOR, 'div:first-child')
        self.click(btn)
        time.sleep(2)

    def zkswap_approve(self):
        time.sleep(1)
        try:
            self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="swap-page"]/div/div[2]/div/button[1]')))
            self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="swap-page"]/div/div[2]/div/button[1]')))
            elem = self.driver.find_element(By.XPATH, '//*[@id="swap-page"]/div/div[2]/div/button[1]')
            self.click(elem)
            self.approve()
            time.sleep(20)
        except (NoSuchElementException, selenium.common.TimeoutException):
            pass
    def mute_swap(self, token1, count1, token2):
        try:
            count1 = float(str(count1)[:4])
        except Exception:
            pass
        self.get_site('mute')
        time.sleep(2)
        self.mute_change_tokens(token1, count1, token2)
        time.sleep(1)
        self.mute_approve()
        time.sleep(1)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/button')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/button')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/button')
        self.click(elem)
        self.confirm_tx()
        time.sleep(30)
        try:
            self.big_wait(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[3]/div[1]')))
            self.click(self.driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[1]'))
        except Exception:
            pass
    @_swap
    def syncswap_swap(self, token1, count1, token2):
        try:
            count1 = float(str(count1)[:8])
        except Exception:
            pass
        self.get_site('syncswap')
        self.syncswap_change_tokens(token1, count1, token2)
        self.syncswap_approve()
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, SYNCSWAP_CONFIGS['swap_btn'])))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, SYNCSWAP_CONFIGS['swap_btn'])))
        elem = self.driver.find_element(By.XPATH, SYNCSWAP_CONFIGS['swap_btn'])
        self.click(elem)

    def space_swap(self, token1, count1, token2):
        try:
            count1 = float(str(count1)[:8])
        except Exception:
            pass
        self.get_site('space')
        self.space_change_tokens(token1, count1, token2)
        self.space_approve()
        time.sleep(1)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, SPACEFI_CONFIGS['swap_btn'])))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, SPACEFI_CONFIGS['swap_btn'])))
        elem = self.driver.find_element(By.XPATH, SPACEFI_CONFIGS['swap_btn'])
        self.click(elem)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="confirm-swap-or-send"]')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="confirm-swap-or-send"]')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="confirm-swap-or-send"]')
        self.click(elem)
        self.confirm_tx()
        time.sleep(30)
        self.close_page()

    @_swap
    def pancake_swap(self, token1, count1, token2):
        try:
            count1 = float(str(count1)[:8])
        except Exception:
            pass
        self.get_site('pancake')
        self.pancake_change_tokens(token1, count1, token2)
        self.pancake_approve()
        time.sleep(30)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, PANCAKE_CONFIGS['swap_btn'])))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, PANCAKE_CONFIGS['swap_btn'])))
        elem = self.driver.find_element(By.XPATH, PANCAKE_CONFIGS['swap_btn'])
        self.click(elem)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="confirm-swap-or-send"]')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="confirm-swap-or-send"]')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="confirm-swap-or-send"]')
        self.click(elem)

    def mav_swap(self, token1, count1, token2):
        self.get_site('mav')
        self.mav_change_tokens(token1, count1, token2)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button'))

        self.mav_approve()
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button')
        self.click(elem)
        self.confirm_tx()
        time.sleep(30)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button[1]')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button[1]')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button[1]')
        self.click(elem)

    @_swap
    def zkbridge_bridge(self, count):
        self.get_site('zkbridge')
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="amount-input"]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="amount-input"]')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="amount-input"]')
        elem.send_keys(str(count))
        time.sleep(1)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__nuxt"]/div/main/div/div[4]/form/div[5]/div[1]/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__nuxt"]/div/main/div/div[4]/form/div[5]/div[1]/button')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div/main/div/div[4]/form/div[5]/div[1]/button')
        self.click(elem)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="headlessui-dialog-panel-25"]/div[2]/div[5]/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="headlessui-dialog-panel-25"]/div[2]/div[5]/button')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="headlessui-dialog-panel-25"]/div[2]/div[5]/button')
        self.click(elem)

    @_swap
    def syncswap_add_liquiduty(self, usdc_to_add):
        if 'syncswap' not in self.now_sites:
            self.get_site('syncswap')
        self.get_site('syncswap_liquid', init=False)
        time.sleep(1)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div[2]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/button/div/div[5]/a/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div[2]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/button/div/div[5]/a/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div[2]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/button/div/div[5]/a/button'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[1]/div[3]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[1]/div[3]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[1]/div[3]'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/div[2]/span/span[1]/span[2]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/div[2]/span/span[1]/span[2]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/div[2]/span/span[1]/span[2]'))
        elem = self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/div[1]/div[1]/div/div[2]/input')
        elem.send_keys(str(usdc_to_add))
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/div[4]/div[1]/div[2]/button')))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/div[4]/div[1]/div[2]/button')))
            self.click(self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/div[4]/div[1]/div[2]/button'))
        except Exception:
            pass
        else:
            self.approve()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[5]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[2]/button'))

    @_swap
    def mute_add_liquiduty(self, usdc_to_add):
        self.get_site('mute')
        self.get_site('mute_liquid', init=False)
        time.sleep(10)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div[3]/div/div/div[1]/div/button')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div/div[3]/div/div/div[1]/div/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[3]/div/div/div[1]/div/button'))
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/input')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/input')))
        elem = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/input')
        elem.send_keys(usdc_to_add)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/button[2]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/button[2]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/button[2]'))

    @_swap
    def mute_remove_liquiduty(self):
        self.get_site('mute')
        self.get_site('mute_liquid', init=False)
        time.sleep(10)
        self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div/div[1]/div/button')))
        self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div/div[1]/div/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div/div[1]/div/button'))

        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div[1]/button[2]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div[1]/button[2]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div[1]/button[2]'))

        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div[3]/button[4]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div[3]/button[4]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/div[3]/button[4]'))

        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/button[2]')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/button[2]')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div/button[2]'))
        self.approve()
        time.sleep(15)

    @_swap
    def domain(self, name):
        self.get_site('zkns')
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/input')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/input')))
        input = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/input')
        input.send_keys(name)
        input.send_keys(Keys.ENTER)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[1]/div/div[1]/div[2]/div/div/div[3]/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[1]/div/div[1]/div[2]/div/div/div[3]/button')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/div[1]/div/div[1]/div[2]/div/div/div[3]/button'))

    def orbiter(self, count_eth):
        time.sleep(1)
        self.get_site('orbiter')
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/input')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/input')))
        input = self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/input')
        input.send_keys(str(count_eth))
        time.sleep(10)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/span/span')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/span/span')))
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div/span/span').click()
        time.sleep(10)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[4]/div/span')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[4]/div/span')))
        self.click(self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[4]/div/span'))
        time.sleep(5)
        self.confirm_tx()
        time.sleep(100)

    def get_price_mute(self):
        self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, MUTE_CONFIGS.get('min_price'))))
        time.sleep(1)
        text = self.driver.find_element(By.XPATH, MUTE_CONFIGS.get('min_price')).text.split(' ')[0]
        return text

    def get_price_syncswap(self):
        time.sleep(3)
        elem = self.driver.find_element(By.XPATH, SYNCSWAP_CONFIGS.get('min_price_open'))
        self.click(elem)
        self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, SYNCSWAP_CONFIGS.get('min_price'))))
        text = self.driver.find_element(By.XPATH, SYNCSWAP_CONFIGS.get('min_price')).text.split(' ')[0]
        return text

    def get_price_space(self):
        self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, SPACEFI_CONFIGS.get('min_price'))))
        time.sleep(1)
        text = self.driver.find_element(By.XPATH, SPACEFI_CONFIGS.get('min_price')).text.split(' ')[0]
        return text

    def get_price_pancake(self):
        self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, PANCAKE_CONFIGS.get('min_price'))))
        time.sleep(1)
        text = self.driver.find_element(By.XPATH, PANCAKE_CONFIGS.get('min_price')).text.split(' ')[0]
        return text

    def get_price_mav(self):
        self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, MAV_CONFIGS.get('min_price'))))
        time.sleep(1)
        text = self.driver.find_element(By.XPATH, MAV_CONFIGS.get('min_price')).text.split(' ')[0]
        return text


    def mute_change_tokens(self, token1, count1, token2):
        tokens = (token1, token2)
        time.sleep(2)
        if self.counters.get('mute', 0) > 0:
            btn1 = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div[2]/div[1]/div[1]/div[2]/button')
            btn2 = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button')
            buttons = (btn1, btn2)
        else:
            btn1 = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div[2]/div[1]/div[1]/button')
            btn2 = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div[2]/div[3]/div[1]/button')
            buttons = (btn1, btn2)
        self.counters['mute'] += 1
        for num, btn in enumerate(buttons):
            self.click(btn)
            self.mute_chose_token(tokens[num])
        input1 = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/div[2]/div[1]/div[1]/div[1]/input')
        input1.send_keys(Keys.CONTROL + 'a')
        input1.send_keys(Keys.DELETE)
        self.click(input1)
        input1.send_keys(str(count1))

    def syncswap_change_tokens(self, token1, count1, token2):
        tokens = (token1, token2)
        buttons = (self.driver.find_element(By.XPATH, SYNCSWAP_CONFIGS['btn'][0]), self.driver.find_element(By.XPATH, SYNCSWAP_CONFIGS['btn'][1]))
        for num, btn in enumerate(buttons):
            if self.syncswap_now_selected[num] == tokens[num]:
                continue
            else:
                self.syncswap_now_selected[num] = tokens[num]
                self.click(btn)
                self.syncswap_chose_token(tokens[num])
        input1 = self.driver.find_element(By.XPATH, SYNCSWAP_CONFIGS['token1_input'])
        input1.send_keys(Keys.CONTROL + 'a')
        input1.send_keys(Keys.DELETE)
        self.click(input1)
        input1.send_keys(str(count1))

    def space_change_tokens(self, token1, count1, token2):
        tokens = (token1, token2)
        buttons = (self.driver.find_element(By.XPATH, SPACEFI_CONFIGS['btn'][0]), self.driver.find_element(By.XPATH, SPACEFI_CONFIGS['btn'][1]))
        for num, btn in enumerate(buttons):
            if self.space_now_selected[num] == tokens[num]:
                continue
            else:
                self.space_now_selected[num] = tokens[num]
                self.click(btn)
                self.space_chose_token(tokens[num])
        time.sleep(1)
        input1 = self.driver.find_element(By.XPATH, SPACEFI_CONFIGS['token1_input'])
        input1.send_keys(Keys.CONTROL + 'a')
        input1.send_keys(Keys.DELETE)
        self.click(input1)
        input1.send_keys(str(count1))

    def pancake_change_tokens(self, token1, count1, token2):
        tokens = (token1, token2)
        buttons = (self.driver.find_element(By.XPATH, PANCAKE_CONFIGS['btn'][0]), self.driver.find_element(By.XPATH, PANCAKE_CONFIGS['btn'][1]))
        for num, btn in enumerate(buttons):
            if self.pancake_now_selected[num] == tokens[num]:
                continue
            else:
                self.pancake_now_selected[num] = tokens[num]
                self.click(btn)
                self.pancake_chose_token(tokens[num])
        time.sleep(1)
        input1 = self.driver.find_element(By.XPATH, PANCAKE_CONFIGS['token1_input'])
        input1.send_keys(Keys.CONTROL + 'a')
        input1.send_keys(Keys.DELETE)
        self.click(input1)
        input1.send_keys(str(count1))

    def mav_change_tokens(self, token1, count1, token2):
        tokens = (token1, token2)
        buttons = (self.driver.find_element(By.XPATH, MAV_CONFIGS['btn'][0]), self.driver.find_element(By.XPATH, MAV_CONFIGS['btn'][1]))
        for num, btn in enumerate(buttons):
            self.click(btn)
            self.mav_chose_token(tokens[num])
        time.sleep(1)
        input1 = self.driver.find_element(By.XPATH, MAV_CONFIGS['token1_input'])
        input1.send_keys(Keys.CONTROL + 'a')
        input1.send_keys(Keys.DELETE)
        input1.click()
        input1.send_keys(str(count1))

    def mute_chose_token(self, token):
        time.sleep(5)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[3]/input')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/input')))
        elem = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/input')
        elem.send_keys(Keys.CONTROL + 'a')
        elem.send_keys(Keys.DELETE)
        self.click(elem)
        elem.send_keys(token)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[3]/ul/li[1]/button')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/ul/li[1]/button')))
        self.click(self.driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/ul/li[1]/button'))
        time.sleep(1)

    def syncswap_chose_token(self, token):
        elem = self.driver.find_element(By.XPATH, SYNCSWAP_CONFIGS['search'])
        elem.send_keys(Keys.CONTROL + 'a')
        elem.send_keys(Keys.DELETE)
        self.click(elem)
        elem.send_keys(token)
        time.sleep(2)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"{SYNCSWAP_CONFIGS['token_container']}")))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"{SYNCSWAP_CONFIGS['token_container']}")))
        parent_element = self.driver.find_element(By.CSS_SELECTOR, f"{SYNCSWAP_CONFIGS['token_container']}")
        tokens = parent_element.find_elements(By.XPATH, './div')
        for now_token in tokens:
            time.sleep(1)
            if token in now_token.text:
                self.click(now_token)
                break

    def space_chose_token(self, token):
        time.sleep(1)
        if token == 'ETH':
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/reach-portal[1]/div[3]/div/div/div/div/div[1]/div[2]/div[2]/div[1]')))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/reach-portal[1]/div[3]/div/div/div/div/div[1]/div[2]/div[2]/div[1]')))
            self.click(self.driver.find_element(By.XPATH, '/html/body/reach-portal[1]/div[3]/div/div/div/div/div[1]/div[2]/div[2]/div[1]'))
        else:
            elem = self.driver.find_element(By.XPATH, SPACEFI_CONFIGS['search'])
            elem.send_keys(Keys.CONTROL + 'a')
            elem.send_keys(Keys.DELETE)
            self.click(elem)
            elem.send_keys(token)
            self.wait.until(EC.visibility_of_element_located((By.XPATH, f"{SPACEFI_CONFIGS['token_container']}")))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, f"{SPACEFI_CONFIGS['token_container']}")))
            self.click(self.driver.find_element(By.XPATH, f"{SPACEFI_CONFIGS['token_container']}"))

    def pancake_chose_token(self, token):
        time.sleep(1)
        elem = self.driver.find_element(By.XPATH, PANCAKE_CONFIGS['search'])
        elem.send_keys(Keys.CONTROL + 'a')
        elem.send_keys(Keys.DELETE)
        self.click(elem)
        elem.send_keys(token)
        time.sleep(1)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, f"{PANCAKE_CONFIGS['token_container']}")))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f"{PANCAKE_CONFIGS['token_container']}")))
        self.click(self.driver.find_element(By.XPATH, f"{PANCAKE_CONFIGS['token_container']}"))

    def mav_chose_token(self, token):
        time.sleep(1)
        elem = self.driver.find_element(By.XPATH, MAV_CONFIGS['search'])
        time.sleep(1)
        elem.send_keys(token)
        time.sleep(1)
        parent_element = self.driver.find_element(By.XPATH, f"{MAV_CONFIGS['token_container']}")
        child_element = parent_element.find_element(By.XPATH, f".//*[text()='{token}']")
        child_element.click()

    def mute_approve(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/button')))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/button')))
            element = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div/div[2]/button')
            if element.text.startswith(MUTE_CONFIGS['approve_starswith']):
                self.click(element)
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            pass
        except selenium.common.exceptions.TimeoutException:
            pass
        else:
            self.approve()

    def syncswap_approve(self):
        time.sleep(1)
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, SYNCSWAP_CONFIGS['approve_btn'])))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, SYNCSWAP_CONFIGS['approve_btn'])))
            element = self.driver.find_element(By.XPATH, SYNCSWAP_CONFIGS['approve_btn'])
            self.click(element)
        except NoSuchElementException:
            pass
        except selenium.common.exceptions.TimeoutException:
            pass
        else:
            self.approve()

    def space_approve(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, SPACEFI_CONFIGS['approve_btn'])))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, SPACEFI_CONFIGS['approve_btn'])))
            element = self.driver.find_element(By.XPATH, SPACEFI_CONFIGS['approve_btn'])
            self.click(element)
        except NoSuchElementException:
            pass
        except selenium.common.exceptions.TimeoutException:
            pass
        else:
            self.approve()

    def pancake_approve(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, PANCAKE_CONFIGS['approve_btn'])))
            self.wait.until(EC.element_to_be_clickable((By.XPATH, PANCAKE_CONFIGS['approve_btn'])))
            element = self.driver.find_element(By.XPATH, PANCAKE_CONFIGS['approve_btn'])
            self.click(element)
        except NoSuchElementException:
            pass
        except selenium.common.exceptions.TimeoutException:
            pass
        else:
            self.approve()

    def mav_approve(self):
        try:
            time.sleep(10)
            self.big_wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button')))
            self.big_wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button')))
            element = self.driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div[1]/div[2]/div/button')
            if 'approve' in element.text.lower():
                self.click(element)
            else:
                raise selenium.common.exceptions.TimeoutException()
        except NoSuchElementException:
            pass
        except selenium.common.exceptions.TimeoutException:
            pass
        else:
            self.approve()