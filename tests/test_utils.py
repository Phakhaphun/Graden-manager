from utils import calculate_revenue, calculate_profit


def test_calculate_revenue():
    assert calculate_revenue(2, 15) == 30


def test_calculate_profit():
    assert calculate_profit(30, 10) == 20
