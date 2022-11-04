from datetime import datetime, timezone

import pytest

from squidalytics.data.scrape_version_releases import (
    get_version_release_dates,
    map_date_to_version,
)


class TestVersionReleases:
    @pytest.mark.internet
    def test_get_version_release_dates(self) -> None:
        versions = get_version_release_dates()
        assert isinstance(versions, dict)
        assert len(versions) > 0
        assert versions["1.0.0"] == datetime(
            2022, 4, 19, 0, 0, tzinfo=timezone.utc
        )

    @pytest.mark.internet
    @pytest.mark.parametrize(
        "date, expected_version",
        [
            (datetime(2022, 4, 19, 0, 1, tzinfo=timezone.utc), "1.0.0"),
            (datetime(2022, 9, 2, 0, 1, tzinfo=timezone.utc), "1.1.0"),
            (datetime.strptime("2022-09-30 -0600", "%Y-%m-%d %z"), "1.1.2"),
        ],
        ids=[
            "2022-04-19 00:01 UTC - 1.0.0",
            "2022-09-02 00:01 UTC - 1.1.0",
            "2022-09-30 00:00 CST - 1.1.2",
        ],
    )
    def test_map_date_to_version(
        self, date: datetime, expected_version: str
    ) -> None:
        version = map_date_to_version(date)
        assert version == expected_version
