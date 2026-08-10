from anime365.chips import Chip, ChipCondition, build_chips


def test_build_chips_single_condition() -> None:
    assert build_chips([ChipCondition(field="genre", operator="@=", value=[8, 35])]) == "genre@=8,35"


def test_build_chips_multiple_conditions() -> None:
    chips: list[Chip] = [
        ChipCondition(field="genre", operator="@=", value=[8, 35]),
        "genre_op=and",
    ]
    assert build_chips(chips) == "genre@=8,35;genre_op=and"


def test_build_chips_scalar_value() -> None:
    assert build_chips([ChipCondition(field="year", operator="=", value=2024)]) == "year=2024"
