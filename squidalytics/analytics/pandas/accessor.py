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
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Calculates the winrate and games played for each combination of the
        given columns.

        Args:
            columns (list[str] | str): The columns to calculate the winrate for.

        Returns:
            tuple:
                pd.DataFrame: The winrate for the given columns.
                pd.DataFrame: The number of games played for the given columns.
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
