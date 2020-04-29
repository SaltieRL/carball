## Important Methods
To effectively use the DataFrame object, below are listed some of the more valuable methods. Please make sure that you
search the pandas docs for clarifications, *before* asking questions.

#### data_frame.x.y
For example, `data_frame.game.time`.

This method simply narrows the scope to the selected column(s). The *x* variable refers to the first value of the tuple,
and the *y* variable refers to the second value of the tuple (if only x is provided, all columns belonging to that tuple
will be returned)

The first (left-most) column still refers to the consecutive in-game frames.

**Notes:**
 * To see all available columns, either refer to the given example, or do data_frame.info(verbose=True)

#### data_frame.loc()

For example, `data_frame.loc[1, 'Player']` `data_frame.loc[1, ('Player', 'ping')]`

`data_frame.loc[index, column_key]` where index is the in-game frame number, and column_key is the column that you wish
to access (to access a single, specific column, use the desired tuple in brackets).

**Notes:**
 * The index is an integer, not a string.
 * The column keys are always strings.

#### data_frame.at()

Exactly the same as .loc(), but should preferably be used to access single values, as opposed to many rows/columns.