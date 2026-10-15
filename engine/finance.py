"""Financial functions. Interest rates go in and come out as percent per period."""
import math


def _rate(percent):
    return percent / 100


def ctrm(pint, fv, pv):
    """Periods needed for pv to grow to fv."""
    r = _rate(pint)
    return math.log(fv / pv) / math.log(1 + r)


def ddb(cost, salvage, life, period):
    """Double-declining-balance depreciation in one period."""
    if life <= 0 or period < 1 or period > life or int(period) != period:
        raise ValueError("period must be a whole number from 1 to life")
    book = cost
    for _ in range(int(period)):
        depreciation = min(book * 2 / life, max(book - salvage, 0))
        book -= depreciation
    return depreciation


def fv(pmt, pint, n):
    """Future value of equal payments at the end of each period."""
    r = _rate(pint)
    return pmt * n if r == 0 else pmt * ((1 + r) ** n - 1) / r


def gpm(cost, margin):
    """Selling price that gives this gross profit margin (percent of the price)."""
    if margin >= 100:
        raise ValueError("margin must be below 100%")
    return cost / (1 - _rate(margin))


def pmt(pv, pint, n):
    """Payment per period that pays off a loan of pv."""
    r = _rate(pint)
    return pv / n if r == 0 else pv * r / (1 - (1 + r) ** -n)


def pv(pmt, pint, n):
    """Present value of equal payments at the end of each period."""
    r = _rate(pint)
    return pmt * n if r == 0 else pmt * (1 - (1 + r) ** -n) / r


def rate(fv, pv, n):
    """Interest rate per period (percent) that grows pv to fv in n periods."""
    return ((fv / pv) ** (1 / n) - 1) * 100


def sln(cost, salvage, life):
    """Straight-line depreciation per period."""
    return (cost - salvage) / life


def syd(cost, salvage, life, period):
    """Sum-of-years'-digits depreciation in one period."""
    if period < 1 or period > life:
        raise ValueError("period must be from 1 to life")
    return (cost - salvage) * (life - period + 1) * 2 / (life * (life + 1))


def term(pmt, fv, pint):
    """Number of payments of pmt needed to reach fv."""
    r = _rate(pint)
    return fv / pmt if r == 0 else math.log(1 + fv * r / pmt) / math.log(1 + r)


# button -> (title, field labels, function)
SPECS = {
    "Ctrm": ("Compounding term", ["Periodic interest rate (%)", "Future value", "Present value"], ctrm),
    "Ddb": ("Double-declining depreciation", ["Asset cost", "Salvage value", "Asset life (periods)", "Period"], ddb),
    "Fv": ("Future value", ["Periodic payment", "Periodic interest rate (%)", "Number of periods"], fv),
    "Gpm": ("Gross profit margin (price needed)", ["Cost", "Margin (%)"], gpm),
    "Pmt": ("Periodic payment", ["Present value (loan)", "Periodic interest rate (%)", "Number of periods"], pmt),
    "Pv": ("Present value", ["Periodic payment", "Periodic interest rate (%)", "Number of periods"], pv),
    "Rate": ("Periodic interest rate (%)", ["Future value", "Present value", "Number of periods"], rate),
    "Sln": ("Straight-line depreciation", ["Asset cost", "Salvage value", "Asset life (periods)"], sln),
    "Syd": ("Sum-of-years'-digits depreciation", ["Asset cost", "Salvage value", "Asset life (periods)", "Period"], syd),
    "Term": ("Payment periods", ["Periodic payment", "Future value", "Periodic interest rate (%)"], term),
}
