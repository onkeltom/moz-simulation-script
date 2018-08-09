# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import time
import sys

import mozlog.structured
from marionette_harness import MarionetteTestCase
from marionette_driver.errors import ScriptTimeoutException
from marionette_driver.errors import TimeoutException
from marionette_driver.errors import InsecureCertificateException

# Change these parameters for your test

PAGE_SET = "sets/alexa50.json"
PROCESS = "content"
HISTOGRAMS = [
    "CONTENT_PAINT_TIME",
    "GFX_OMTP_PAINT_WAIT_TIME",
]
SCALARS = [
    "gfx.omtp.paint_wait_ratio",
]
ITERATIONS = 2

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
    return de.scrollTop >= (pageHeight - window.innerHeight - 2);
}
function isAtTop() {
    return de.scrollTop <= 2;
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

        with open(PAGE_SET) as page_set:
            self.pages = json.load(page_set)

        self.marionette.set_context('chrome')
        self.marionette.timeout.page_load = 20
        self.marionette.execute_script(CLEAR_PING_SCRIPT)
        self.logger.info("cleared telemetry ping")

    def test_simulation(self):
        for page in self.pages * ITERATIONS:
            with self.marionette.using_context('content'):
                self.logger.info("loading %s" % page)
                try:
                    self.marionette.navigate(page)
                    self.logger.info("loaded!")
                    time.sleep(2)
                    self.marionette.execute_async_script(INTERACT_SCRIPT)
                    self.logger.info("interacted!")
                except:
                    self.logger.info("caught %s" % sys.exc_info()[0])

    def tearDown(self):
        self.logger.info("finished loading pages")
        self.marionette.set_context('chrome')
        time.sleep(10)
        ping = self.marionette.execute_script(GET_PING_SCRIPT)
        self.logger.info("retrieved telemetry ping")

        histograms = {}
        scalars = {}

        for name in HISTOGRAMS:
            histogramSet = self.findHistograms(ping, PROCESS, name)
            for name, histogram in histogramSet.items():
                self.expandHistogram(histogram)
                histograms[name] = histogram

        for name in SCALARS:
            scalars[name] = self.findScalar(ping, PROCESS, name)

        with open('histograms.json', 'w') as out:
            json.dump(histograms, out, sort_keys=True, indent=2)
        with open('scalars.json', 'w') as out:
            json.dump(scalars, out, sort_keys=True, indent=2)

        with open('histograms.txt', 'w') as out:
            for name, histogram in sorted(histograms.items()):
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

    # TODO: Add support for keyed scalars
    def findScalar(self, ping, process, name):
        payload = ping["payload"]

        scalars = {}
        if process == "parent":
            scalars = payload["scalars"]
        elif process in payload["processes"]:
            scalars = payload["processes"][process]["scalars"]

        if name in scalars:
            return scalars[name]
        else:
            return None


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
