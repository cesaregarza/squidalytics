import numpy as np
import pandas as pd


@pd.api.extensions.register_dataframe_accessor("squidalytics")
class SquidalyticsAccessor:
    JUDGE_MAP: dict[str, float] = {
        "WIN": 1,
        "LOSE": 0,
        "DRAW": 0.5,
        "EXEMPTED_LOSE": 0.5,
    }

    def __init__(self, pandas_obj: pd.DataFrame) -> None:
        self._obj = pandas_obj

    def numerical_judgement(self, include_exempt: bool = True) -> pd.Series:
        """Converts the judgement column to a numerical value. If include_exempt
        is True, then the EXEMPTED_LOSE judgement will be counted as a draw.
        Otherwise, it will be given a value of np.nan.

        Args:
            include_exempt (bool): Whether to include EXEMPTED_LOSE as a draw.
                Defaults to True.

        Returns:
            pd.Series: A series of numerical values representing the judgement.
        """
        JUDGE_MAP = self.JUDGE_MAP.copy()
        if not include_exempt:
            JUDGE_MAP["EXEMPTED_LOSE"] = np.nan
        return self._obj["judgement"].map(JUDGE_MAP)

    def winrate_grid(
        self, columns: list[str] | str
    ) -> tuple[pd.Series, pd.Series]:
        """Calculates the winrate and games played for each combination of the
        given columns.

        Args:
            columns (list[str] | str): The columns to calculate the winrate for.

        Returns:
            tuple:
                pd.Series: The winrate for the given columns.
                pd.Series: The number of games played for the given columns.
        """

        df = self._obj.copy()
        result_float = self.numerical_judgement()
        df = df.assign(result_float=result_float)

        if isinstance(columns, str):
            columns = [columns]

        groupby = df.groupby(columns)
        winrate = groupby["result_float"].mean()
        wincount = groupby["result_float"].count()
        return winrate, wincount

    def summarize_awards(self) -> pd.Series:
        """Summarizes the awards column.

        Returns:
            pd.Series: The number of times each award was given in the format
                `XG YS` where X is the number of gold medals and Y is the number
                of silver medals.
        """
        df = self._obj.copy()
        awards_cols = [col for col in df.columns if "award" in col.lower()]
        award_ranks = [col for col in awards_cols if "rank" in col.lower()]

        def _summarize_awards(row: pd.Series) -> str:
            golds, silvers = 0, 0
            for col in award_ranks:
                if row[col] == "GOLD":
                    golds += 1
                elif row[col] == "SILVER":
                    silvers += 1
            return f"{golds}G {silvers}S"

        return df.apply(_summarize_awards, axis=1)

    def format_for_cli(self, max_length: int = 20) -> pd.DataFrame:
        """Formats the dataframe for display in the CLI.

        Args:
            max_length (int): The maximum length of a string before it is
                truncated. Defaults to 20.

        Returns:
            pd.DataFrame: The formatted dataframe.
        """
        df = self._obj.copy()

        # Format datetimes for printing.
        dt_cols = df.select_dtypes(include="datetime64[ns, UTC]").columns
        df[dt_cols] = df[dt_cols].applymap(
            lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")
        )
        # Format timedelta for printing.
        td_cols = df.select_dtypes(include="timedelta64[ns]").columns

        def format_timedelta(td: pd.Timedelta) -> str:
            minutes, seconds = divmod(td.seconds, 60)
            return f"{minutes}:{seconds:02d}"

        df[td_cols] = df[td_cols].applymap(format_timedelta)

        # Truncate long strings
        str_cols = df.select_dtypes(include="string").columns
        df[str_cols] = df[str_cols].applymap(
            lambda s: s[:max_length] + "..." if len(s) > max_length else s
        )

        # Format floats
        float_cols = df.select_dtypes(include="float").columns
        df[float_cols] = df[float_cols].round(2)

        # Summarize awards columns
        awards = self.summarize_awards()
        awards_columns = [col for col in df.columns if "award" in col.lower()]
        df = df.drop(columns=awards_columns)
        df["awards"] = awards

        return df
