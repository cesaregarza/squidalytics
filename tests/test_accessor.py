from functools import cached_property

import numpy as np
import pandas as pd
import pytest

from squidalytics.analytics.pandas import accessor as acc


class TestAccessor:

    STAGES = ["A", "B", "C", "D"]
    RULES = ["1", "2", "3", "4"]
    JUDGEMENTS = ["WIN", "LOSE", "DRAW", "EXEMPTED_LOSE"]
    NUM_ROWS = 10_000

    @cached_property
    def DATAFRAME(self) -> pd.DataFrame:

        # Generate random data
        data = []
        for _ in range(self.NUM_ROWS):
            data.append(
                {
                    "stage": np.random.choice(self.STAGES),
                    "rule": np.random.choice(self.RULES),
                    "judgement": np.random.choice(self.JUDGEMENTS),
                }
            )
        return pd.DataFrame(data)

    def test_numerical_judgement(self) -> None:
        """Test the numerical_judgement method."""
        df = self.DATAFRAME
        include_exempt = df.squidalytics.numerical_judgement()
        exclude_exempt = df.squidalytics.numerical_judgement(
            include_exempt=False
        )

        for i in range(self.NUM_ROWS):
            include = include_exempt[i]
            exclude = exclude_exempt[i]
            judgement = df["judgement"][i]

            if judgement == "EXEMPTED_LOSE":
                assert include == 0.5
                assert np.isnan(exclude)
            elif judgement == "DRAW":
                assert include == 0.5
                assert exclude == 0.5
            elif judgement == "WIN":
                assert include == 1
                assert exclude == 1
            elif judgement == "LOSE":
                assert include == 0
                assert exclude == 0

    def test_winrate_grid(self) -> None:
        df = self.DATAFRAME
        winrate, wincount = df.squidalytics.winrate_grid(["stage", "rule"])
        assert isinstance(winrate, pd.Series)
        assert isinstance(wincount, pd.Series)
        assert winrate.shape == (len(self.STAGES) * len(self.RULES),)
        assert wincount.shape == (len(self.STAGES) * len(self.RULES),)

        winrate, wincount = df.squidalytics.winrate_grid("stage")
        assert isinstance(winrate, pd.Series)
        assert isinstance(wincount, pd.Series)
        assert winrate.shape == (len(self.STAGES),)
        assert wincount.shape == (len(self.STAGES),)
