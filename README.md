# moz-simulation-script

A shell of a script using marionette to gather telemetry data from loading and
lightly interacting with a predefined pageset in Firefox.

## Usage

1. (Optional) Add a telemetry probe for the desired metric you want to measure
1. Open `test_simulator.py`
    1. Change `PAGE_SET` to the desired page set path
    1. Change `PROCESS` to the process you want to get the histograms from
    1. Change `HISTOGRAMS` to the names of the histogram probes you want
    1. Change `ITERATIONS` to the number of iterations you want to run
1. Run `../firefox/mach marionette test test_simulator.py`

The script will output a `histograms.json` and `histograms.txt` with the telemetry data from the run.
