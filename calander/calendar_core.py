"""Core Jalali/Gregorian/Islamic calendar utilities.

This module avoids third-party date libraries and implements:
- Jalali <-> Gregorian conversion
- A civil/tabular Islamic date approximation from Julian day number
- Weekday calculations
- Supported range validation
"""

from datetime import date

PERSIAN_MONTH_NAMES = [
    "Farvardin", "Ordibehesht", "Khordad",
    "Tir", "Mordad", "Shahrivar",
    "Mehr", "Aban", "Azar",
    "Dey", "Bahman", "Esfand"
]

WEEKDAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

GREGORIAN_MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

SUPPORTED_MIN = (1348, 10, 11)
SUPPORTED_MAX = (1416, 10, 30)


def div(a, b):
    return a // b


def gregorian_to_jdn(gy, gm, gd):
    a = (14 - gm) // 12
    y = gy + 4800 - a
    m = gm + 12 * a - 3
    return gd + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def jdn_to_gregorian(jdn):
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + (m // 10)
    return year, month, day


def gregorian_to_jd(y, m, d):
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3

    jd = d + ((153 * m2 + 2) // 5) + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045
    return jd


def jalali_to_gregorian(jy, jm, jd):
    jy2 = jy + 1595
    days = -355668 + (365 * jy2) + (jy2 // 33) * 8 + ((jy2 % 33) + 3) // 4 + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += ((jm - 7) * 30) + 186

    gy = 400 * (days // 146097)
    days %= 146097

    if days > 36524:
        gy += 100 * ((days - 1) // 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1

    gy += 4 * (days // 1461)
    days %= 1461

    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365

    gd = days + 1
    kab = 29 if is_gregorian_leap(gy) else 28
    sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    while gm <= 12 and gd > sal_a[gm]:
        gd -= sal_a[gm]
        gm += 1
    return gy, gm, gd


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621

    gy2 = gy + 1 if gm > 2 else gy
    days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


def is_gregorian_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def is_jalali_leap(year):
    leap_years = [1, 5, 9, 13, 17, 22, 26, 30]
    return (year % 33) in leap_years


def jalali_month_length(year, month):
    if 1 <= month <= 6:
        return 31
    if 7 <= month <= 11:
        return 30
    if month == 12:
        return 30 if is_jalali_leap(year) else 29
    raise ValueError("Invalid Jalali month")


def valid_jalali_date(year, month, day):
    if month < 1 or month > 12:
        return False
    if day < 1 or day > jalali_month_length(year, month):
        return False
    return within_supported_range(year, month, day)


def within_supported_range(year, month, day):
    return SUPPORTED_MIN <= (year, month, day) <= SUPPORTED_MAX


def jalali_to_iso(year, month, day):
    return f"{year:04d}-{month:02d}-{day:02d}"


def iso_to_jalali(iso_date):
    y, m, d = iso_date.split("-")
    return int(y), int(m), int(d)


def jalali_weekday(year, month, day):
    gy, gm, gd = jalali_to_gregorian(year, month, day)
    return date(gy, gm, gd).weekday()


def format_jalali(year, month, day):
    return f"{day} {PERSIAN_MONTH_NAMES[month - 1]} {year}"


def format_gregorian(gy, gm, gd):
    return f"{gd} {GREGORIAN_MONTH_NAMES[gm - 1]} {gy}"


def islamic_from_jdn(jdn):
    l = jdn - 1948440 + 10632
    n = (l - 1) // 10631
    l = l - 10631 * n + 354
    j = ((10985 - l) // 5316) * ((50 * l) // 17719) + (l // 5670) * ((43 * l) // 15238)
    l = l - ((30 - j) // 15) * ((17719 * j) // 50) - (j // 16) * ((15238 * j) // 43) + 29
    month = (24 * l) // 709
    day = l - (709 * month) // 24
    year = 30 * n + j - 30
    return year, month, day


def jalali_to_islamic(year, month, day):
    gy, gm, gd = jalali_to_gregorian(year, month, day)
    jdn = gregorian_to_jdn(gy, gm, gd)
    return islamic_from_jdn(jdn)


def system_today_jalali():
    today = date.today()
    return gregorian_to_jalali(today.year, today.month, today.day)
