import decimal
from math import pi


def rad_2_deg(radian):
    if isinstance(radian, decimal.Decimal):
        return float(radian.to_decimal()) * 180 / pi
    if isinstance(radian, float):
        return radian * 180 / pi
    else:
        return 0
