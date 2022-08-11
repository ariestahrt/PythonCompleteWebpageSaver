# Python Complete Webpage Saver (inc. CSS, JS, and other local assets)

Hi everyone, I just make this tool I think its purpose is clear from the title. I know this is a silly idea and a waste of time making it... why not use python selenium and use pyautogui as UI automation to open the chrome tab and do CTRL-S hotkey like below:

```
from selenium import webdriver
import pyautogui
import time

driver = webdriver.Chrome('./chromedriver')

driver.get("https://www.python.org")
time.sleep(1)
pyautogui.hotkey('ctrl', 's')
time.sleep(1)
pyautogui.typewrite("Webpage Download")
pyautogui.hotkey('enter')
```

I made this in case I want to save a website with a specific HTML document in the past from an archive website provider (e.g. urlscan.io).