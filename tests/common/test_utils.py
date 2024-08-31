import pytest

from app.common.utils import get_logger, one_liner, percent_chance


def test_one_liner():
    assert one_liner("Hello\nWorld") == "Hello World"
    assert one_liner("Too    many    spaces") == "Too many spaces"
    assert one_liner("Cut this text", cut_len=7) == "Cut thi"


def test_percent_chance():
    assert isinstance(percent_chance(50), bool)
    with pytest.raises(ValueError):
        percent_chance(101)
    with pytest.raises(ValueError):
        percent_chance(-1)


def test_get_logger():
    logger = get_logger("test_component")
    assert logger.name == "test_component"
    assert len(logger.handlers) == 1
    assert logger.level == 10  # DEBUG level
