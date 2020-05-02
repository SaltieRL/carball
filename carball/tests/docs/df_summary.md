## Summary
The DataFrame is an instance of two-dimensional, size-mutable, potentially heterogeneous tabular data. It comes as part
of the pandas package (often imported as *pd*).

The index column (no header) represents each in-game frame from the replay (i.e. if the game runs in 60fps, there will
be 60 rows in the DataFrame for every second passed in the game).

Each column is a tuple, and detailed information about all of them can be seen by using `data_frame.info(verbose=True)`,
and the example below perfectly illustrates this structure.

**For extensive documentation, refer to [the official pandas website](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html).**