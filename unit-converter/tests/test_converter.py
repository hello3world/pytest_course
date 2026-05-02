from uc.converter import ConversionGraph
from uc.converter import Quantity
import pytest


@pytest.fixture(autouse=True)
def unit_registry():
    graph = ConversionGraph()

    # Register length units
    graph.add_unit("meter", "length")
    graph.add_unit("centimeter", "length")
    graph.add_unit("kilometer", "length")
    graph.add_unit("inch", "length")
    graph.add_unit("foot", "length")
    graph.add_unit("yard", "length")

    # Add linear conversions for length
    graph.add_linear("meter", "centimeter", scale=100)
    graph.add_linear("kilometer", "meter", scale=1000)
    graph.add_linear("inch", "centimeter", scale=2.54)
    graph.add_linear("foot", "inch", scale=12)
    graph.add_linear("yard", "foot", scale=3)

    return graph


@pytest.mark.parametrize(
    "from_unit, to_unit, expected",
    [
        ("meter", "centimeter", 100),
        ("kilometer", "meter", 1000),
        ("inch", "centimeter", 2.54),
        ("foot", "inch", 12),
        ("yard", "foot", 3),
    ]
)
def test_conversion(unit_registry, from_unit, to_unit, expected):
    graph = unit_registry
    quantity = Quantity(value=1, unit=from_unit)
    result = graph.convert(quantity, to_unit)
    assert result.value == expected


def pytest_generate_tests(metafunc):
    if "test_conversion_v2" in metafunc.function.__name__:
        metafunc.parametrize(
            "from_unit, to_unit, expected", 
            [
                ("meter", "centimeter", 100),
                ("kilometer", "meter", 1000),
                ("inch", "centimeter", 2.54),
                ("foot", "inch", 12),
                ("yard", "foot", 3),
            ]
        )

def test_conversion_v2(unit_registry, from_unit, to_unit, expected):
    graph = unit_registry
    quantity = Quantity(value=1, unit=from_unit)
    result = graph.convert(quantity, to_unit)
    assert result.value == expected