# ReplayAnalysis
Various tools for decompiling / analyzing Rocket League replays

Current Pipeline:
![pipeline is in Parserformat.png](Parser%20format.png)

If you want to add a new stat it is best to do it in the advanced stats section of the pipeline.
You should look at:<br />
[Stat base classes](replay_analysis/analysis/stats/stats.py)<br />
[Where you add a new stat](replay_analysis/analysis/stats/stats_list.py)

If you want to see the output format of the stats created you can look [here](api)

Compile the proto files by running in this directory
`setup.bat` or `setup.sh` depending on your operating system.

# Running
Create a folder called `replays`
Put a rocket league replay into this folder and then run
`decompile_replays.py`
