# ReplayAnalysis
Various tools for decompiling / analyzing Rocket League replays

Current Pipeline:
![pipeline is in Parserformat.png](Parser%20format.png)

If you want to add a new stat it is best to do it in the advanced stats section of the pipeline.
You should look at:<br />
[Stat base classes](replay_analysis/analysis/stats/stats.py)<br />
[Where you add a new stat you have added](replay_analysis/analysis/stats/stats_list.py)

If you want to see the output format of the stats created you can look [here](api)

# Setup
If on Windows you need to install pytables
run this from the home directory

`pip install replay_analysis\generated\tables-3.4.4-cp36-cp36m-win_amd64.whl`
