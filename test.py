import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.keys import Keys
import os
import csv
import random
import json

ts = int(time.time())

#filename = "mediatest" + str(ts) + ".csv"

ff_options = Options()

with open('sets/medialong.json', 'r') as url_file:
    test_urls = json.load(url_file)

ff_binary = '/Applications/Firefox.app/Contents/MacOS/firefox'
#ff_binary = '/Applications/Firefox Beta.app/Contents/MacOS/firefox'
#ff_binary = '/Applications/FirefoxNightly.app/Contents/MacOS/firefox'

profile = FirefoxProfile("/Users/dominik/Library/Application Support/Firefox/Profiles/pwuh6421.veryclean")

##### DEFINE OPTION TO RUN ############
### Regular run on vanilla profile
# option = "regular_DSL"

### scroll.com
option = "scroll"
#scroll profile
profile = FirefoxProfile("/Users/dominik/Library/Application Support/Firefox/Profiles/lkxwo17i.scroll")

### private browsing
#option = "private_DSL"
#ff_options.add_argument("-private")

# Private browsing
# if option == "private_DSL":
    # ff_options.add_argument("-private")
#ff_options.setBinary('/Applications/FirefoxNightly.app/Contents/MacOS/firefox')

driver = webdriver.Firefox(firefox_profile=profile,firefox_options=ff_options, firefox_binary = ff_binary )  # Optional argument, if not specified will search path.
driver.set_page_load_timeout(120)

for x in range(0,10):
    print(str(x+1) + ". Runde")
    #driver = webdriver.Firefox(firefox_profile=profile,firefox_options=ff_options, firefox_binary = ff_binary )  # Optional argument, if not specified will search path.

    with driver.context(driver.CONTEXT_CHROME):
        driver.execute_async_script("var callback = arguments[arguments.length - 1]; Services.clearData.deleteData(Services.clearData.CLEAR_ALL_CACHES, callback);")
        print "All caches cleared!"

    #driver.set_page_load_timeout(120)
    random.shuffle(test_urls)

    for i, data in enumerate(test_urls):

        print(data)
        driver.get(data['link'])
        # time.sleep(3)
        navStart = driver.execute_script("return performance.getEntriesByType('resource')")
        filename = "./runs/cold/" + option + "_cold_" + str(ts) + "_" + "resourcetimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
        with open(filename, 'a') as results_file:
            json.dump(navStart,results_file)

        # with driver.context(driver.CONTEXT_CHROME):
        #     blockers = driver.execute_async_script("var callback = arguments[arguments.length - 1]; gBrowser.selectedBrowser.getContentBlockingLog().then(callback);")
        #     print blockers

        navStart = driver.execute_script("return performance.getEntriesByType('navigation')")
        filename = "./runs/cold/" + option + "_cold_" + str(ts) + "_" + "navigationtimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
        with open(filename, 'a') as results_file:
            json.dump(navStart,results_file)

    for j, data in enumerate(test_urls):

        driver.get(data['link'])
        # time.sleep(3)
        navStart = driver.execute_script("return performance.getEntriesByType('resource')")
        filename = "./runs/cached/" + option + "_cached_" + str(ts) + "_" + "resourcetimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
        with open(filename, 'a') as results_file:
            json.dump(navStart,results_file)

        # with driver.context(driver.CONTEXT_CHROME):
        #     blockers = driver.execute_async_script("var callback = arguments[arguments.length - 1]; gBrowser.selectedBrowser.getContentBlockingLog().then(callback);")
        #     print blockers

        navStart = driver.execute_script("return performance.getEntriesByType('navigation')")
        filename = "./runs/cached/" + option + "_cached_" + str(ts) + "_" + "navigationtimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
        with open(filename, 'a') as results_file:
            json.dump(navStart,results_file)
    #     # try:
    #     #     driver.get(data['link'])
    #     #     time.sleep(3)
    #     #     navStart = driver.execute_script("return performance.getEntriesByType('resource')")
    #     #     filename = "./runs/cold/" + "cold_" + str(ts) + "_" + "resourcetimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
    #     #     with open(filename, 'a') as results_file:
    #     #         json.dump(navStart,results_file)
    #     #
    #     #     #with selenium.context(selenium.CONTEXT_CHROME):
    #     #
    #     #         #blockers = driver.execute_async_script("var callback = arguments[arguments.length - 1]; gBrowser.selectedBrowser.getContentBlockingLog().then(callback);")
    #     #         #print blockers
    #     #
    #     #     navStart = driver.execute_script("return performance.getEntriesByType('navigation')")
    #     #     filename = "./runs/cold/" + "cold_" + str(ts) + "_" + "navigationtimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
    #     #     with open(filename, 'a') as results_file:
    #     #         json.dump(navStart,results_file)
    #     #
    #     #
    #     # except:
    #     #     navStart = driver.execute_script("return performance.getEntriesByType('resource')")
    #     #     filename = "./runs/cold/" + "cold_" + str(ts) + "_" + "resourcetimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
    #     #     with open(filename, 'a') as results_file:
    #     #         json.dump(navStart,results_file)
    #     #
    #     #     navStart = driver.execute_script("return performance.getEntriesByType('navigation')")
    #     #     filename = "./runs/cold/" + "cold_" + str(ts) + "_" + "navigationtimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
    #     #     with open(filename, 'a') as results_file:
    #     #         json.dump(navStart,results_file)
    #     #     continue
    #
    # for j, data in enumerate(test_urls):
    #
    #     try:
    #         driver.get(data['link'])
    #         time.sleep(3)
    #         navStart = driver.execute_script("return performance.getEntriesByType('resource')")
    #         filename = "./runs/cached/" + "cached_" + str(ts) + "_" + "resourcetimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
    #         with open(filename, 'a') as results_file:
    #             json.dump(navStart,results_file)
    #
    #         navStart = driver.execute_script("return performance.getEntriesByType('navigation')")
    #         filename = "./runs/cached/" + "cached_" + str(ts) + "_" + "navigationtimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
    #         with open(filename, 'a') as results_file:
    #             json.dump(navStart,results_file)
    #
    #
    #     except:
    #         navStart = driver.execute_script("return performance.getEntriesByType('resource')")
    #         filename = "./runs/cached/" + "cached_" + str(ts) + "_" + "resourcetimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
    #         with open(filename, 'a') as results_file:
    #             json.dump(navStart,results_file)
    #
    #         navStart = driver.execute_script("return performance.getEntriesByType('navigation')")
    #         filename = "./runs/cached/" + "cached_" + str(ts) + "_" + "navigationtimings" + "_" + data['tag'].encode("utf-8") + "_" + str(x) + ".json"
    #         with open(filename, 'a') as results_file:
    #             json.dump(navStart,results_file)
    #         continue

driver.quit()
