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

But that solution will not save the page with all assets like assets that coming from the CSS file. This is the best solution for you to save the whole page to be accessible 100% offline.