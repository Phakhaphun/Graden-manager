def calculate_revenue(quantity: float, price_per_unit: float) -> float:
    """คำนวณรายรับจากปริมาณคูณราคาต่อหน่วย"""
    return round(quantity * price_per_unit, 2)


def calculate_profit(revenue: float, cost: float) -> float:
    """คำนวณกำไรเบื้องต้นจากรายรับหักต้นทุน"""
    return round(revenue - cost, 2)
