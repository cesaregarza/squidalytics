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

    def numerical_judgement(self) -> pd.Series:
        return self._obj["judgement"].map(self.JUDGE_MAP)
