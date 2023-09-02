import time
import pyautogui
import pyperclip


class SeleniumArb:
    def paste_here(self, text):
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')

    def click(self, elem):
        self.driver.execute_script("arguments[0].click();", elem)

    def close_page(self):
        count_tab = len(self.driver.window_handles)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[count_tab - 2])

    def open_page(self, href):
        count_tab = len(self.driver.window_handles)
        self.driver.switch_to.window(self.metamask_handle)
        self.driver.execute_script(f"window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[count_tab])
        self.driver.get(href)
        time.sleep(2)