import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import os
import csv
import random
import json

ts = int(time.time())

filename = "mediatest" + str(ts) + ".csv"

ff_options = Options()

ff_binary = '/Applications/Firefox.app/Contents/MacOS/firefox'
#ff_binary = '/Applications/Firefox Beta.app/Contents/MacOS/firefox'
#ff_binary = '/Applications/FirefoxNightly.app/Contents/MacOS/firefox'

# Private browsing
ff_options.add_argument("-private")
#ff_options.setBinary('/Applications/FirefoxNightly.app/Contents/MacOS/firefox')

with open('sets/media.json', 'r') as url_file:
    test_urls = json.load(url_file)

for x in range(0,1):

    driver = webdriver.Firefox(firefox_options=ff_options, firefox_binary = ff_binary )  # Optional argument, if not specified will search path.

#    print x

    driver.set_page_load_timeout(120)
    random.shuffle(test_urls)

    for i, url in enumerate(test_urls):

        try:
            driver.get(url)
            navStart = driver.execute_script("return performance.getEntriesByType('navigation')")
            print(navStart)
            #navStart['url'] = str(url)
            #navStart['run'] = str(x)

            if os.path.exists(filename):
                #append_write = 'a' # append if already exists
                with open(filename, 'a') as results_file:
                    #csvwriter = csv.writer(results_file)
                    #csvwriter.writerow(navStart.values())
                    json.dump(navStart,results_file)
            else:
                #append_write = 'w' # make a new file if not
                with open(filename, 'wb') as results_file:
                    json.dump(navStart,results_file)
                    #csvwriter = csv.writer(results_file)
                    #csvwriter.writerow(navStart.keys())
                    #csvwriter.writerow(navStart.values())


        except:
            navStart = driver.execute_script("return performance.getEntriesByType('navigation')")
            print(navStart)
            #navStart['url'] = str(url)
            #navStart['run'] = str(x)

            if os.path.exists(filename):
                #append_write = 'a' # append if already exists
                with open(filename, 'a') as results_file:
                    json.dump(navStart,results_file)
                    #csvwriter = csv.writer(results_file)
                    #csvwriter.writerow(navStart.values())
            else:
                #append_write = 'w' # make a new file if not
                with open(filename, 'wb') as results_file:
                    json.dump(navStart,results_file)
                    #csvwriter = csv.writer(results_file)
                    #csvwriter.writerow(navStart.keys())
                    #csvwriter.writerow(navStart.values())

            continue

    driver.quit()
