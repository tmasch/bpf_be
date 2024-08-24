#pylint: disable=C0114,C0304,C0116
import parse_date_1



def test_empty_date():
    d=""
    r=parse_date_1.parse_date(d)
    assert r.messages[0] == "No input"

def test_four_digit_date():
    d="1234"
    r=parse_date_1.parse_date(d)
    assert r.year == "1234"

def test_mm_dd_yyyy():
    d="12.12.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == "12"
    assert r.month == "12"
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_qq_dd_yyyy():
    d="??.12.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == "12"
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_xx_dd_yyyy():
    d="xx.12.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == "12"
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_qq_qq_yyyy():
    d="??.??.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == ""
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_xx_xx_yyyy():
    d="xx.xx.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == ""
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_qq_qq_qqqq():
    d="??.??.????"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == ""
    assert r.year == ""
    assert r.state == "SUCCESS"

def test_xx_xx_xxxx():
    d="xx.xx.xxxx"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == ""
    assert r.year == ""
    assert r.state == "SUCCESS"

def test_qq_qq_qqqq():
    d="??.??.????"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == ""
    assert r.year == ""
    assert r.state == "SUCCESS"


def test_d_mm_yyyyy():
    d="1.12.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == "01"
    assert r.month == "12"
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_q_mm_yyyy():
    d="?.12.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == "12"
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_x_mm_yyyy():
    d="x.12.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == "12"
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_q_qq_yyyy():
    d="?.??.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == "" 
    assert r.month == ""
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_x_xx_yyyy():
    d="x.xx.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == ""
    assert r.year == "1234"
    assert r.state == "SUCCESS"


def test_d_m_yyyy():
    d="1.2.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == "01"
    assert r.month == "02"
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_q_m_yyyy():
    d="?.2.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == "02"
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_q_m_yyyy():
    d="?.2.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == "02"
    assert r.year == "1234"
    assert r.state == "SUCCESS"


def test_x_m_yyyy():
    d="x.2.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == "02"
    assert r.year == "1234"
    assert r.state == "SUCCESS"


def test_mm_yyyy():
    d="12.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == "12"
    assert r.year == "1234"
    assert r.state == "SUCCESS"


def test_qq_yyyy():
    d="??.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == ""
    assert r.year == "1234"
    assert r.state == "SUCCESS"

def test_xx_yyyy():
    d="xx.1234"
    r=parse_date_1.parse_date(d)
    print(r)
    assert r.day == ""
    assert r.month == ""
    assert r.year == "1234"
    assert r.state == "SUCCESS"


def test_mmddyyy_error():
    d="1a.2b.1235"
    r=parse_date_1.parse_date(d)
    assert r.state == "FAIL"

def test_nnjh():
    d="17. Jh."
    r=parse_date_1.parse_date_range(d)
    print(r)
    assert r.start.year == "1600"
    assert r.end.year == "1699"

def test_nintynine_century():
    d="99./99. Jh.."
    r=parse_date_1.parse_date_range(d)
    print(r)
    assert r.state == "SUCCESS"
