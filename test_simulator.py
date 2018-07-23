# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import time

import mozlog.structured
from marionette_harness import MarionetteTestCase
from marionette_driver.errors import TimeoutException
from marionette_driver.errors import InsecureCertificateException

# Change these parameters for your test

PAGES = [
    "https://google.com",
    "https://youtube.com",
    "https://facebook.com",
    "https://baidu.com",
    "https://wikipedia.org",
    "https://yahoo.com",
    "http://qq.com",
    "https://amazon.com",
    "https://taobao.com",
    "https://tmall.com",
    "https://twitter.com",
    "https://instagram.com",
    "https://google.co.in",
    "https://sohu.com",
    "http://live.com",
    "https://jd.com",
    "https://vk.com",
    "https://reddit.com",
    "https://sina.com",
    "https://weibo.com",
    "https://google.co.jp",
    "https://360.cn",
    "https://login.tmall.com",
    "https://blogspot.com",
    "https://yandex.ru",
    "https://google.ru",
    "https://netflix.com",
    "https://google.co.uk",
    "https://google.com.br",
    "https://google.com.hk",
    "https://linkedin.com",
    "https://csdn.net",
    "https://t.co",
    "https://google.fr",
    "https://ebay.com",
    "https://alipay.com",
    "https://twitch.tv",
    "https://google.de",
    "https://pages.tmall.com",
    "https://microsoft.com",
    "https://bing.com",
    "https://msn.com",
    "https://mail.ru",
    "https://wikia.com",
    "https://naver.com",
    "https://aliexpress.com",
]
PROCESS = "content"
HISTOGRAMS = [
    "CONTENT_PAINT_TIME",
    "GFX_OMTP_PAINT_WAIT_TIME",
    "CONTENT_LARGE_PAINT_PHASE_WEIGHT",
    "CONTENT_SMALL_PAINT_PHASE_WEIGHT",
]

# Internal constants

MAX_BAR_CHARS = 25
CLEAR_PING_SCRIPT = """
ChromeUtils.import("resource://gre/modules/TelemetrySend.jsm");
TelemetrySend.clearCurrentPings();
"""
INTERACT_SCRIPT = """
let [resolve] = arguments;
let de = document.documentElement;
let pageHeight = de.scrollHeight;

function isAtBottom() {
    return de.scrollTop >= (pageHeight - window.innerHeight - 0.5);
}
function isAtTop() {
    return de.scrollTop <= 0.5;
}

whileScrollingBottom = function() {
    if (isAtBottom()) {
        removeEventListener('scroll', whileScrollingBottom);
        addEventListener('scroll', whileScrollingTop);
        window.scrollBy({top: -pageHeight, behavior: 'smooth'});
    }
};
whileScrollingTop = function() {
    if (isAtTop()) {
        resolve(1);
    }
};

if (isAtBottom()) {
    resolve(1);
}

addEventListener('scroll', whileScrollingBottom);
window.scrollBy({top: pageHeight, behavior: 'smooth'});
"""
GET_PING_SCRIPT = """
ChromeUtils.import("resource://gre/modules/TelemetryController.jsm");
return TelemetryController.getCurrentPingData(true);
"""

class SimulatorTestCase(MarionetteTestCase):
    def setUp(self):
        MarionetteTestCase.setUp(self)
        self.logger = mozlog.structured.structuredlog.get_default_logger()

        self.marionette.set_context('chrome')
        self.marionette.timeout.page_load = 20
        self.marionette.execute_script(CLEAR_PING_SCRIPT)
        self.logger.info("cleared telemetry ping")

    def test_simulation(self):
        for page in PAGES:
            with self.marionette.using_context('content'):
                self.logger.info("loading %s" % page)
                try:
                    self.marionette.navigate(page)
                    self.logger.info("loaded!")
                    time.sleep(2)
                    self.marionette.execute_async_script(INTERACT_SCRIPT)
                    self.logger.info("interacted!")
                except TimeoutException as exc:
                    self.logger.info("navigating to %s hit timeout" % page)
                except InsecureCertificateException as exc:
                    self.logger.info("navigating to %s hit insecure certificate" % page)

    def tearDown(self):
        self.logger.info("finished loading pages")
        self.marionette.set_context('chrome')
        time.sleep(10)
        ping = self.marionette.execute_script(GET_PING_SCRIPT)
        self.logger.info("retrieved telemetry ping")

        histograms = {}
        for name in HISTOGRAMS:
            histogramSet = self.findHistograms(ping, PROCESS, name)
            for name, histogram in histogramSet.items():
                self.expandHistogram(histogram)
                histograms[name] = histogram

        with open('histograms.json', 'w') as out:
            json.dump(histograms, out, sort_keys=True, indent=2)

        with open('histograms.txt', 'w') as out:
            for name, histogram in histograms.items():
                rendered = self.renderHistogram(name, histogram)
                print >> out, rendered

        MarionetteTestCase.tearDown(self)

    def findHistograms(self, ping, process, name):
        payload = ping["payload"]

        histograms = {}
        keyedHistograms = {}
        if process == "parent":
            histograms = payload["histograms"]
            keyedHistograms = payload["keyedHistograms"]
        elif process in payload["processes"]:
            histograms = payload["processes"][process]["histograms"]
            keyedHistograms = payload["processes"][process]["keyedHistograms"]

        results = {}

        if name in histograms:
            results[name] = histograms[name]

        if name in keyedHistograms:
            for key, histogram in keyedHistograms[name].items():
                joinedName = "%s.%s" % (name, key)
                results[joinedName] = histogram

        return results

    def expandHistogram(self, histogram):
        sampleCount = 0
        for key, value in histogram["values"].items():
            sampleCount += value
        average = round(histogram["sum"] * 10 / sampleCount) / 10

        histogram["sample_count"] = sampleCount
        histogram["average"] = average

    def renderHistogram(self, name, histogram):
        text = "%s sample_count = %d average = %f\n" % (name, histogram["sample_count"], histogram["average"])

        maxLabelLen = 0
        maxValue = 0
        for bucket, value in histogram["values"].items():
            maxLabelLen = max(maxLabelLen, len(str(bucket)))
            maxValue = max(maxValue, int(value))

        sortedValues = sorted(map(lambda x: (int(x[0]), x[1]), histogram["values"].items()))

        for bucket, value in sortedValues:
            label = str(bucket)
            bars = int(round(MAX_BAR_CHARS * value / maxValue))

            text += "%s%s | %s%s | %d\n" % (label, ' ' * int(maxLabelLen - len(label)), '#' * bars, ' ' * int(MAX_BAR_CHARS - bars), value)

        return text
