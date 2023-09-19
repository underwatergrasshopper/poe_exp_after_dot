from math import isclose as _isclose

from poe_exp_after_dot._Private.Overlay import FineTime, FineExpPerHour, FinePercent, Measurer

def test_fine_time():
    assert str(FineTime()) == "0s"
    assert str(FineTime(1)) == "1s"
    assert str(FineTime(9)) == "9s"
    assert str(FineTime(59)) == "59s"

    assert str(FineTime(60)) == "1m00s"
    assert str(FineTime(60 + 1)) == "1m01s"
    assert str(FineTime(60 + 9)) == "1m09s"
    assert str(FineTime(60 + 59)) == "1m59s"
    assert str(FineTime(60 + 60)) == "2m00s"

    assert str(FineTime(60 * 9 + 59)) == "9m59s"
    assert str(FineTime(60 * 59 + 59)) == "59m59s"

    assert str(FineTime(60 * 60)) == "1h00m00s"
    assert str(FineTime(1 * 60 * 60 + 1 * 60  + 5)) == "1h01m05s"
    assert str(FineTime(23 * 60 * 60  + 59 * 60 + 59)) == "23h59m59s"

    assert str(FineTime(24 * 60 * 60)) == "1d00h00m00s"
    assert str(FineTime(1 * 24 * 60 * 60 + 2 * 60 * 60 + 3 * 60 + 4)) == "1d02h03m04s"
    assert str(FineTime(6 * 24 * 60 * 60 + 23 * 60 * 60 + 59 * 60 + 59)) == "6d23h59m59s"

    assert str(FineTime(7 * 24 * 60 * 60)) == "1w0d00h00m00s"
    assert str(FineTime(999 * 7 * 24 * 60 * 60 + 6 * 24 * 60 * 60 + 23 * 60 * 60 + 59 * 60 + 59)) == "999w6d23h59m59s"

    assert str(FineTime(125, "s")) == "125s"

    assert str(FineTime(120 * 60 + 4, "m")) == "120m04s"
    assert str(FineTime(120 * 60 + 59, "m")) == "120m59s"

    assert str(FineTime(26 * 60 * 60 + 3 * 60 + 4, "h")) == "26h03m04s"
    assert str(FineTime(235 * 60 * 60 + 59 * 60 + 59, "h")) == "235h59m59s"

    assert str(FineTime(30 * 24 * 60 * 60  + 1 * 60 * 60 + 3 * 60 + 4, "d")) == "30d01h03m04s"
    assert str(FineTime(234 * 24 * 60 * 60  + 23 * 60 * 60 + 59 * 60 + 59, "d")) == "234d23h59m59s"

    assert str(FineTime(
        999     * 7 * 24 * 60 * 60 + 
        6       * 24 * 60 * 60 + 
        23      * 60 * 60 + 
        59      * 60 + 
        59, 
        unit_color = "blue"
    )) == (
        "999<font color=\"blue\">w</font>"
        "6<font color=\"blue\">d</font>"
        "23<font color=\"blue\">h</font>"
        "59<font color=\"blue\">m</font>"
        "59<font color=\"blue\">s</font>"
    )

    assert str(FineTime(
        999     * 7 * 24 * 60 * 60 + 
        6       * 24 * 60 * 60 + 
        23      * 60 * 60 + 
        59      * 60 + 
        59, 
        value_color = "yellow"
    )) == (
        "<font color=\"yellow\">999</font>w"
        "<font color=\"yellow\">6</font>d"
        "<font color=\"yellow\">23</font>h"
        "<font color=\"yellow\">59</font>m"
        "<font color=\"yellow\">59</font>s"
    )

    assert str(FineTime(
        999     * 7 * 24 * 60 * 60 + 
        6       * 24 * 60 * 60 + 
        23      * 60 * 60 + 
        59      * 60 + 
        59, 
        value_color = "yellow", 
        unit_color = "blue"
    )) == (
        "<font color=\"yellow\">999</font><font color=\"blue\">w</font>"
        "<font color=\"yellow\">6</font><font color=\"blue\">d</font>"
        "<font color=\"yellow\">23</font><font color=\"blue\">h</font>"
        "<font color=\"yellow\">59</font><font color=\"blue\">m</font>"
        "<font color=\"yellow\">59</font><font color=\"blue\">s</font>"
    )

    assert _fine_time_with_exception(time_ = 10, max_unit = "wrong") == "Unexpected value of 'max_unit' parameter."

def _fine_time_with_exception(**kwarg):
    try:
        FineTime(**kwarg)
    except Exception as exception:
        return str(exception)
    else:
        return None

def test_fine_exp_per_hour():
    assert str(FineExpPerHour()) == "0 exp/h"
    assert str(FineExpPerHour(1)) == "1 exp/h"
    assert str(FineExpPerHour(99)) == "99 exp/h"
    assert str(FineExpPerHour(999)) == "999 exp/h"

    assert str(FineExpPerHour(1000)) == "1.00k exp/h"
    assert str(FineExpPerHour(1909)) == "1.90k exp/h"
    assert str(FineExpPerHour(1990)) == "1.99k exp/h"
    assert str(FineExpPerHour(1999)) == "1.99k exp/h"

    assert str(FineExpPerHour(10000)) == "10.0k exp/h"
    assert str(FineExpPerHour(19900)) == "19.9k exp/h"
    assert str(FineExpPerHour(99000)) == "99.0k exp/h"
    assert str(FineExpPerHour(99099)) == "99.0k exp/h"
    assert str(FineExpPerHour(99900)) == "99.9k exp/h"

    assert str(FineExpPerHour(999999)) == "999k exp/h"

    assert str(FineExpPerHour(9000000)) == "9.00m exp/h"
    assert str(FineExpPerHour(9010000)) == "9.01m exp/h"
    assert str(FineExpPerHour(9999999)) == "9.99m exp/h"
    assert str(FineExpPerHour(99099999)) == "99.0m exp/h"
    assert str(FineExpPerHour(99999999)) == "99.9m exp/h"
    assert str(FineExpPerHour(999999999)) == "999m exp/h"
    assert str(FineExpPerHour(9999999999)) == "9999m exp/h"

    assert str(FineExpPerHour(9999999, value_color = "blue")) == "<font color=\"blue\">9.99</font>m exp/h"
    assert str(FineExpPerHour(9999999, unit_color = "red")) == "9.99<font color=\"red\">m exp/h</font>"
    assert str(FineExpPerHour(9999999, value_color = "blue", unit_color = "red")) == "<font color=\"blue\">9.99</font><font color=\"red\">m exp/h</font>"


def test_fine_percent():
    fp = FinePercent()
    assert str(fp) == "0.00%"
    assert fp.get_integer() == 0
    assert fp.get_2_dig_after_dot() == 0

    fp = FinePercent(1)
    assert str(fp) == "1.00%"
    assert fp.get_integer() == 1
    assert fp.get_2_dig_after_dot() == 0

    fp = FinePercent(0.01)
    assert str(fp) == "0.01%"
    assert fp.get_integer() == 0
    assert fp.get_2_dig_after_dot() == 1

    fp = FinePercent(12.3401)
    assert str(fp) == "12.34%"
    assert fp.get_integer() == 12
    assert fp.get_2_dig_after_dot() == 34

    fp = FinePercent(12.3499)
    assert str(fp) == "12.34%"
    assert fp.get_integer() == 12
    assert fp.get_2_dig_after_dot() == 34

    fp = FinePercent(-12.3499)
    assert str(fp) == "-12.34%"
    assert fp.get_integer() == -12
    assert fp.get_2_dig_after_dot() == -34

    fp = FinePercent(12.3499, is_sign = True)
    assert str(fp) == "+12.34%"
    assert fp.get_integer() == 12
    assert fp.get_2_dig_after_dot() == 34

    fp = FinePercent(-12.3499, is_sign = True)
    assert str(fp) == "-12.34%"
    assert fp.get_integer() == -12
    assert fp.get_2_dig_after_dot() == -34

    assert str(FinePercent(-12.3499, integer_color = "blue")) == "-<font color=\"blue\">12</font>.34%"
    assert str(FinePercent(-12.3499, two_dig_after_dot_color = "green")) == "-12.<font color=\"green\">34</font>%"
    assert str(FinePercent(-12.3499, integer_color = "blue", two_dig_after_dot_color = "green")) == "-<font color=\"blue\">12</font>.<font color=\"green\">34</font>%"

    assert str(FinePercent(12.3499, integer_color = "blue")) == "<font color=\"blue\">12</font>.34%"
    assert str(FinePercent(12.3499, two_dig_after_dot_color = "green")) == "12.<font color=\"green\">34</font>%"
    assert str(FinePercent(12.3499, integer_color = "blue", two_dig_after_dot_color = "green")) == "<font color=\"blue\">12</font>.<font color=\"green\">34</font>%"


def test_measurer():
    measurer = Measurer()

    assert measurer.is_update_fail() == False

    assert measurer.get_level() == 0

    assert measurer.get_progress() == 0.0

    assert measurer.get_progress_step() == 0.0
    assert measurer.get_progress_step_in_exp() == 0.0
    assert measurer.get_progress_step_time() == 0.0

    assert measurer.get_time_to_10_percent() == float('inf')
    assert measurer.get_time_to_next_level() == float('inf')

    measurer = Measurer()

    measurer.update(900, 5.0 * 60)
    
    assert measurer.is_update_fail() == False

    assert measurer.get_level() == 2

    assert _isclose(measurer.get_progress(), 30.3643, abs_tol = 0.0001)

    assert _isclose(measurer.get_progress_step(), 30.3643, abs_tol = 0.0001)
    assert measurer.get_progress_step_in_exp() == 375
    assert measurer.get_progress_step_time() == 0

    assert measurer.get_time_to_10_percent() == float('inf')
    assert measurer.get_time_to_next_level() == float('inf')

    measurer.update(1000, 2.0 * 60)
    
    assert measurer.is_update_fail() == False

    assert measurer.get_level() == 2

    assert _isclose(measurer.get_progress(), 38.4615, abs_tol = 0.0001)

    assert _isclose(measurer.get_progress_step(), 8.0972, abs_tol = 0.0001)
    assert measurer.get_progress_step_in_exp() == 100
    assert measurer.get_progress_step_time() == 2.0 * 60

    assert _isclose(measurer.get_time_to_10_percent(), 148.2, abs_tol = 0.01)
    assert _isclose(measurer.get_time_to_next_level(), 912.0, abs_tol = 0.01)

    # FORMAT:
    # LVL 98 57.93%
    # +0.51% in 30m14s
    # 12.8m exp/h
    # 10% in 3h05m10s
    # next in 1d10h30m45s

    measurer = Measurer()

    assert _update(measurer, 0, 1) == (
        "LVL 1 0.00%\n"
        "+0.00% in 1s\n"
        "0 exp/h\n"
        "10% in never\n"
        "next in never\n"
    )
    assert _update(measurer, 0, 1) == (
        "LVL 1 0.00%\n"
        "+0.00% in 1s\n"
        "0 exp/h\n"
        "10% in never\n"
        "next in never\n"
    )
    assert _update(measurer, 100, 5) == (
        "LVL 1 19.04%\n"
        "+19.04% in 5s\n"
        "72.0k exp/h\n"
        "10% in 3s\n"
        "next in 21s\n"
    )
    assert _update(measurer, 100, 5) == (
        "LVL 1 19.04%\n"
        "+0.00% in 5s\n"
        "0 exp/h\n"
        "10% in never\n"
        "next in never\n"
    )
    assert _update(measurer, 100, 5) == (
        "LVL 1 19.04%\n"
        "+0.00% in 5s\n"
        "0 exp/h\n"
        "10% in never\n"
        "next in never\n"
    )
    assert _update(measurer, 200, 1) == (
        "LVL 1 38.09%\n"
        "+19.04% in 1s\n"
        "360k exp/h\n"
        "10% in 1s\n"
        "next in 3s\n"
    )
    assert _update(measurer, 263, 1) == (
        "LVL 1 50.09%\n"
        "+12.00% in 1s\n"
        "226k exp/h\n"
        "10% in 1s\n"
        "next in 4s\n"
    )
    assert _update(measurer, 524, 10) == (
        "LVL 1 99.80%\n"
        "+49.71% in 10s\n"
        "93.9k exp/h\n"
        "10% in 2s\n"
        "next in 0s\n"
    )
    assert _update(measurer, 600, 10) == (
        "LVL 2 6.07%\n"
        "+6.07% in 0s\n"
        "0 exp/h\n"
        "10% in never\n"
        "next in never\n"
    )
    assert _update(measurer, 1400, 10) == (
        "LVL 2 70.85%\n"
        "+64.77% in 10s\n"
        "288k exp/h\n"
        "10% in 2s\n"
        "next in 4s\n"
    )
    assert _update(measurer, 2000, 10) == (
        "LVL 3 11.87%\n"
        "+11.87% in 0s\n"
        "0 exp/h\n"
        "10% in never\n"
        "next in never\n"
    )
    assert _update(measurer, 3000, 60 * 60) == (
        "LVL 3 61.35%\n"
        "+49.48% in 1h00m00s\n"
        "1.00k exp/h\n"
        "10% in 12m08s\n"
        "next in 46m52s\n"
    )
    assert _update(measurer, 2750, 60 * 60) == (
        "LVL 3 48.98%\n"
        "-12.37% in 1h00m00s\n"
        "-250 exp/h\n"
        "10% in never\n"
        "next in never\n"
    )
    assert _update(measurer, 3000, 60 * 60) == (
        "LVL 3 61.35%\n"
        "+12.37% in 1h00m00s\n"
        "250 exp/h\n"
        "10% in 48m30s\n"
        "next in 3h07m26s\n"
    )

    # debug
    #measurer = Measurer()
    #print(_update(measurer, 0, 1))
    #print(_update(measurer, 100, 5))
    #print(_update(measurer, 200, 1))
    #print(_update(measurer, 263, 1))
    #print(_update(measurer, 524, 10))
    #print(_update(measurer, 600, 10))
    #print(_update(measurer, 1400, 10))
    #print(_update(measurer, 2000, 10))
    #print(_update(measurer, 3000, 60 * 60))
    #print(_update(measurer, 2750, 60 * 60))
    #print(_update(measurer, 3000, 60 * 60))

def _update(measurer : Measurer, total_exp : int, elapsed_time : float) -> str:
    measurer.update(total_exp, elapsed_time)

    return (
        f"LVL {measurer.get_level()} {FinePercent(measurer.get_progress())}\n"
        f"{FinePercent(measurer.get_progress_step(), is_sign = True)} in {FineTime(measurer.get_progress_step_time())}\n"
        f"{FineExpPerHour(measurer.get_exp_per_hour())}\n"
        f"10% in {FineTime(measurer.get_time_to_10_percent())}\n"
        f"next in {FineTime(measurer.get_time_to_next_level())}\n"
    )
