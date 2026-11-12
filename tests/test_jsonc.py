from __future__ import annotations

import pytest

from daedalus.jsonc import JsoncError, dumps, loads


def test_loads_allows_line_comments() -> None:
    value = loads(
        """
        {
          // default agent
          "default_agent": "orchestrator",
        }
        """
    )
    assert value == {"default_agent": "orchestrator"}


def test_loads_allows_block_comments_and_trailing_commas() -> None:
    value = loads(
        """
        {
          /* permissions */
          "permissions": [
            { "action": "shell", "resource": "*", "effect": "allow" },
          ],
        }
        """
    )
    assert value["permissions"][0]["effect"] == "allow"


def test_loads_ignores_comment_markers_inside_strings() -> None:
    value = loads(
        """
        {
          "url": "https://example.com/a//b",
          "text": "not /* a comment */"
        }
        """
    )
    assert value["url"] == "https://example.com/a//b"
    assert value["text"] == "not /* a comment */"


def test_loads_rejects_invalid_jsonc() -> None:
    with pytest.raises(JsoncError):
        loads('{"a": }')


def test_dumps_round_trip() -> None:
    value = {"name": "Daedalus", "enabled": True}
    assert loads(dumps(value)) == value
    assert dumps(value).endswith("\n")
