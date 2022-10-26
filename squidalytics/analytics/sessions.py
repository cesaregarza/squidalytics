from datetime import timedelta

import pandas as pd


def generate_session_ids(
    df: pd.DataFrame,
    session_length: int | pd.Timedelta | timedelta = 5,
    relative_column: bool = False,
) -> pd.DataFrame:
    """Generate session ids for each row in the dataframe.

    Args:
        df (pd.DataFrame): Dataframe with a datetime index.
        session_length (int | pd.Timedelta | timedelta): The max length allowed
            between two rows to be considered part of the same session. If an
            integer is passed, the unit is assumed to be minutes. Defaults to 5.
        relative_column (bool): If True, an additional column is added to the
            returned dataframe that indicates the relative position of the row
            within the session, from 0 to 1 inclusive on both ends. Defaults to
            False.

    Returns:
        pd.DataFrame: Dataframe with session ids.
    """
    if isinstance(session_length, int):
        session_length = timedelta(minutes=session_length)

    start_time = df["played_time"]
    end_time = df["end_time"]
    difference = start_time - end_time.shift()
    session_int = (difference > session_length).astype(int).cumsum()
    session_start = df.groupby(session_int)["played_time"].min()
    session_id_map = session_start.dt.strftime("%Y%m%d%H%M%S")
    session_id = session_int.map(session_id_map)
    if not relative_column:
        return session_id.to_frame()

    session_size = (
        session_int.value_counts().sub(1).clip(lower=1).pipe(session_int.map)
    )
    relative_position = df.groupby(session_int).cumcount() / session_size
    # Not necessary but for completeness, set all sessions of length 1 to 1.0,
    # since 1.0 marks the end of the session and is probably more intuitive.
    relative_position.loc[session_size == 1] = 1.0
    return pd.concat(
        [session_id, relative_position],
        axis=1,
        keys=["session_id", "relative_position"],
    )
