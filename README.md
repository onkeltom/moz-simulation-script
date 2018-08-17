# moz-simulation-script

A shell of a script using marionette to gather telemetry data from loading and
scrolling a page up and down with a predefined pageset in Firefox.

## Usage

1. (Optional) Add a telemetry probe for the desired metric you want to measure
1. (Optional) [Download](https://download-origin.cdn.mozilla.net/pub/firefox/nightly/) and place a nightly build in this directory
1. Open `test_simulator.py`
    1. Change `PAGE_SET` to the desired page set path
    1. Change `HISTOGRAMS` to the names of the histogram probes you want and their process
    1. Change `SCALARS` to the names of the scalar probes you want and their process
    1. Change `ITERATIONS` to the number of iterations you want to run
1. For a local build, run `../firefox/mach marionette test test_simulator.py`
1. For a nightly build, run `../firefox/mach --binary firefox/firefox.exe marionette test test_simulator.py`
	1. (Optional) Use `--pref pref.name:pref-value` to control behavior between runs

The script will output a folder `run` with results for the run
	1. `ping.json` - The raw ping data
	1. `histograms.json` - The raw selected histograms
	1. `histograms.txt` - Formatted histograms
	1. `scalars.json` - The raw selected scalars
