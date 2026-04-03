from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import BusinessError, parse_steam_id


@pytest.mark.parametrize(
    "url, expected_steam_id",
    [
        ("https://steamcommunity.com/profiles/76561197960435530/", "76561197960435530"),
        ("http://steamcommunity.com/profiles/76561197960435530", "76561197960435530"),
        ("https://www.steamcommunity.com/profiles/76561197960435530/", "76561197960435530"),
    ],
)
def test_parse_steam_id_valid_links(url: str, expected_steam_id: str):
    assert parse_steam_id(url) == expected_steam_id


@pytest.mark.parametrize(
    "url, expected_message",
    [
        ("https://example.com/profiles/76561197960435530/", "Неверная ссылка Steam"),
        ("https://steamcommunity.com/id/76561197960435530/", "Неверная ссылка Steam"),
        ("https://steamcommunity.com/profiles/7656119796043553/", "Неверная ссылка Steam"),
        ("https://steamcommunity.com/profiles/76561297960435530/", "Неверная ссылка Steam"),
        ("https://steamcommunity.com/profiles/7656119abc0435530/", "Неверная ссылка Steam"),
        ("ftp://steamcommunity.com/profiles/76561197960435530/", "Неверная ссылка Steam"),
    ],
)
def test_parse_steam_id_invalid_links(url: str, expected_message: str):
    with pytest.raises(BusinessError) as exc_info:
        parse_steam_id(url)

    assert exc_info.value.message == expected_message
