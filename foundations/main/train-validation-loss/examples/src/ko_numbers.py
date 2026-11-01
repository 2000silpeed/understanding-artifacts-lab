"""Korean readings for the numbers in the narration (screen keeps digits, TTS gets Hangul).

    sino("1,024")      -> 천이십사
    native("32")       -> 서른두        (counter form: 서른두 개, 세 번)
    decimal("0.50")    -> 영 점 오 영   (every digit after the point)
    pct("0.04%")       -> 영 점 영 사 퍼센트
    man("2만 3천")      -> 이만 삼천
    frac("2분의 1")     -> 이분의 일
"""
import re

DIG = "영일이삼사오육칠팔구"
NATIVE_ONES = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"]
NATIVE_TENS = ["", "열", "스물", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]


def sino_int(n):
    if n == 0:
        return "영"
    out = ""
    for unit, name in ((10 ** 8, "억"), (10 ** 4, "만")):
        if n >= unit:
            out += sino_int(n // unit) + name
            n %= unit
    for unit, name in ((1000, "천"), (100, "백"), (10, "십")):
        d = n // unit
        if d:
            out += ("" if d == 1 else DIG[d]) + name
        n %= unit
    if n:
        out += DIG[n]
    return out


def sino(show):
    return sino_int(int(show.replace(",", "")))


def native(show):
    n = int(show.replace(",", ""))
    if not 1 <= n <= 99:
        raise ValueError(f"native counter form only for 1..99: {show}")
    tens, ones = divmod(n, 10)
    if tens == 2 and ones == 0:
        return "스무"
    return NATIVE_TENS[tens] + NATIVE_ONES[ones]


def decimal(show):
    if "." not in show:
        return sino(show)
    a, b = show.split(".")
    return sino(a) + " 점 " + " ".join(DIG[int(c)] for c in b)


def pct(show):
    return decimal(show.rstrip("%")) + " 퍼센트"


def man(show):
    m = re.fullmatch(r"(\d+)만(?: (\d)천)?", show)
    if not m:
        raise ValueError(show)
    out = sino_int(int(m.group(1))) + "만"
    if m.group(2):
        out += " " + sino_int(int(m.group(2)) * 1000)
    return out


def frac(show):
    m = re.fullmatch(r"(\d+)분의 (\d+)", show)
    return sino_int(int(m.group(1))) + "분의 " + sino_int(int(m.group(2)))


READERS = {"sino": sino, "native": native, "decimal": decimal, "pct": pct, "man": man,
           "frac": frac, "text": lambda s: s}
