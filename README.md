# ReplayAnalysis
Various tools for decompiling / analyzing Rocket League replays

Current Pipeline:
![pipeline is in Parserformat.png](Parser%20format.png)

If you want to add a new stat it is best to do it in the advanced stats section of the pipeline.
You should look at:<br />
[Stat base classes](carball/analysis/stats/stats.py)<br />
[Where you add a new stat](carball/analysis/stats/stats_list.py)

If you want to see the output format of the stats created you can look [here](api)

Compile the proto files by running in this directory
`setup.bat` (Windows) or `setup.sh` (Linux/mac)

# Running
Create a folder called `replays`
Put a rocket league replay into this folder and then run
`decompile_replays.py`
