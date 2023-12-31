from poe_exp_after_dot._Private.FineFormatters import SECONDS_IN_WEEK, SECONDS_IN_DAY, SECONDS_IN_HOUR, SECONDS_IN_MINUTE, LT, GT
from poe_exp_after_dot._Private.FineFormatters import FineTime, FineExpPerHour, FinePercent, FineBareLevel, FineExp

def test_fine_exp():
    assert str(FineExp()) == "0exp"
    assert str(FineExp(0)) == "0exp"
    assert str(FineExp(1)) == "1exp"
    assert str(FineExp(999)) == "999exp"
    assert str(FineExp(1000)) == "1'000exp"
    assert str(FineExp(999999)) == "999'999exp"
    assert str(FineExp(1000000)) == "1'000'000exp"
    assert str(FineExp(999999999)) == "999'999'999exp"
    assert str(FineExp(1000000000)) == "1'000'000'000exp"
    assert str(FineExp(4250334444)) == "4'250'334'444exp"

    assert str(FineExp(4250334444 + 1)) == f"{GT}4'250'334'444exp"
    assert str(FineExp(-2)) == f"{LT}0exp"

def test_fine_bare_level():
    assert str(FineBareLevel())     == "0"
    assert str(FineBareLevel(0))    == "0"
    assert str(FineBareLevel(1))    == "1"
    assert str(FineBareLevel(99))   == "99"
    assert str(FineBareLevel(100))  == "100"

    assert str(FineBareLevel(101))  == f"{GT}100"
    assert str(FineBareLevel(-1))   == f"{LT}0"

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
    
    assert str(FineTime(99 * 7 * 24 * 60 * 60 + 6 * 24 * 60 * 60 + 23 * 60 * 60 + 59 * 60 + 59)) == "99w6d23h59m59s"

    assert str(FineTime(125, "s")) == "125s"

    assert str(FineTime(120 * 60 + 4, "m")) == "120m04s"
    assert str(FineTime(120 * 60 + 59, "m")) == "120m59s"

    assert str(FineTime(26 * 60 * 60 + 3 * 60 + 4, "h")) == "26h03m04s"
    assert str(FineTime(235 * 60 * 60 + 59 * 60 + 59, "h")) == "235h59m59s"

    assert str(FineTime(30 * 24 * 60 * 60  + 1 * 60 * 60 + 3 * 60 + 4, "d")) == "30d01h03m04s"
    assert str(FineTime(234 * 24 * 60 * 60  + 23 * 60 * 60 + 59 * 60 + 59, "d")) == "234d23h59m59s"

    assert str(FineTime((99 + 1) * SECONDS_IN_WEEK - 1))                           == "99w6d23h59m59s"
    assert str(FineTime((9999 + 1) * SECONDS_IN_DAY - 1, max_unit = "d"))          == "9999d23h59m59s"
    assert str(FineTime((9999999 + 1) * SECONDS_IN_HOUR - 1, max_unit = "h"))      == "9999999h59m59s"
    assert str(FineTime((9999999999 + 1) * SECONDS_IN_MINUTE - 1, max_unit = "m")) == "9999999999m59s"
    assert str(FineTime(9999999999999, max_unit = "s"))                             == "9999999999999s"

    ### out of visible range ###
    assert str(FineTime(0.1))   == f"{LT}1s"
    assert str(FineTime(0.01))  == f"{LT}1s"
    assert str(FineTime(0.009)) == f"{LT}1s"
    assert str(FineTime(0.1, is_show_ms_if_below_1s = True))    == "0s10ms"
    assert str(FineTime(0.01, is_show_ms_if_below_1s = True))   == "0s01ms"
    assert str(FineTime(0.009, is_show_ms_if_below_1s = True))  == f"{LT}1ms"

    ### cup ###

    assert str(FineTime(-1)) == f"{LT}0s"

    assert str(FineTime(2**64))                                 == f"{GT}9999999999999w"
    assert str(FineTime(2**64, is_just_weeks_if_cap = False))   == f"{GT}99w6d23h59m59s"

    assert str(FineTime((99 + 1) * SECONDS_IN_WEEK))                           == "100w"
    assert str(FineTime((9999 + 1) * SECONDS_IN_DAY, max_unit = "d"))          == "1428w"
    assert str(FineTime((9999999 + 1) * SECONDS_IN_HOUR, max_unit = "h"))      == "59523w"
    assert str(FineTime((9999999999 + 1) * SECONDS_IN_MINUTE, max_unit = "m")) == "992063w"
    assert str(FineTime(9999999999999 + 1, max_unit = "s"))                     == "16534391w"

    assert str(FineTime(
        (99 + 1)    * 7 * 24 * 60 * 60 +
        4           * 24 * 60 * 60 + 
        3           * 60 * 60 + 
        2           * 60 + 
        1,
        is_just_weeks_if_cap = False
    )) == f"{GT}99w6d23h59m59s"

    assert str(FineTime(
        (9999 + 1)  * 24 * 60 * 60 + 
        3           * 60 * 60 + 
        2           * 60 + 
        1, 
        max_unit = "d",
        is_just_weeks_if_cap = False
    )) == f"{GT}9999d23h59m59s"

    assert str(FineTime(
        (9999999 + 1) * 60 * 60 + 
        2 * 60 + 
        1, 
        max_unit = "h",
        is_just_weeks_if_cap = False
    )) == f"{GT}9999999h59m59s"

    assert str(FineTime((9999999999 + 1) * 60 + 1, max_unit = "m", is_just_weeks_if_cap = False)) == f"{GT}9999999999m59s"
    assert str(FineTime((9999999999999 + 1), max_unit = "s", is_just_weeks_if_cap = False)) == f"{GT}9999999999999s"

    ### color ###

    assert str(FineTime(
        99      * 7 * 24 * 60 * 60 + 
        6       * 24 * 60 * 60 + 
        23      * 60 * 60 + 
        59      * 60 + 
        59, 
        unit_color = "blue"
    )) == (
        "99<font color=\"blue\">w</font>"
        "6<font color=\"blue\">d</font>"
        "23<font color=\"blue\">h</font>"
        "59<font color=\"blue\">m</font>"
        "59<font color=\"blue\">s</font>"
    )

    assert str(FineTime(
        99      * 7 * 24 * 60 * 60 + 
        6       * 24 * 60 * 60 + 
        23      * 60 * 60 + 
        59      * 60 + 
        59, 
        value_color = "yellow"
    )) == (
        "<font color=\"yellow\">99</font>w"
        "<font color=\"yellow\">6</font>d"
        "<font color=\"yellow\">23</font>h"
        "<font color=\"yellow\">59</font>m"
        "<font color=\"yellow\">59</font>s"
    )

    assert str(FineTime(
        99      * 7 * 24 * 60 * 60 + 
        6       * 24 * 60 * 60 + 
        23      * 60 * 60 + 
        59      * 60 + 
        59, 
        value_color = "yellow", 
        unit_color = "blue"
    )) == (
        "<font color=\"yellow\">99</font><font color=\"blue\">w</font>"
        "<font color=\"yellow\">6</font><font color=\"blue\">d</font>"
        "<font color=\"yellow\">23</font><font color=\"blue\">h</font>"
        "<font color=\"yellow\">59</font><font color=\"blue\">m</font>"
        "<font color=\"yellow\">59</font><font color=\"blue\">s</font>"
    )

    ### exceptions ###
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
    assert str(FineExpPerHour(-999)) == "-999 exp/h"

    assert str(FineExpPerHour(-9999)) == "-9.99k exp/h"
    assert str(FineExpPerHour(1000)) == "1.00k exp/h"
    assert str(FineExpPerHour(1909)) == "1.90k exp/h"
    assert str(FineExpPerHour(1990)) == "1.99k exp/h"
    assert str(FineExpPerHour(1999)) == "1.99k exp/h"
    assert str(FineExpPerHour(-1999)) == "-1.99k exp/h"

    assert str(FineExpPerHour(10000)) == "10.0k exp/h"
    assert str(FineExpPerHour(19900)) == "19.9k exp/h"
    assert str(FineExpPerHour(99000)) == "99.0k exp/h"
    assert str(FineExpPerHour(99099)) == "99.0k exp/h"
    assert str(FineExpPerHour(99900)) == "99.9k exp/h"

    assert str(FineExpPerHour(999999)) == "999k exp/h"
    assert str(FineExpPerHour(-999999)) == "-999k exp/h"

    assert str(FineExpPerHour(9000000)) == "9.00M exp/h"
    assert str(FineExpPerHour(9010000)) == "9.01M exp/h"
    assert str(FineExpPerHour(9999999)) == "9.99M exp/h"
    assert str(FineExpPerHour(99099999)) == "99.0M exp/h"
    assert str(FineExpPerHour(99999999)) == "99.9M exp/h"
    assert str(FineExpPerHour(999999999)) == "999M exp/h"
    assert str(FineExpPerHour(-999999999)) == "-999M exp/h"

    assert str(FineExpPerHour(9999999999)) == "9.99B exp/h"
    assert str(FineExpPerHour(99999999999)) == "99.9B exp/h"
    assert str(FineExpPerHour(999999999999)) == "999B exp/h"
    assert str(FineExpPerHour(-999999999999)) == "-999B exp/h"
    assert str(FineExpPerHour(999999999999 + 1)) == f"{GT}999B exp/h"
    assert str(FineExpPerHour(-999999999999 - 1)) == f"{LT}-999B exp/h"

    assert str(FineExpPerHour(9999999, value_color = "blue"))                       == "<font color=\"blue\">9.99</font>M exp/h"
    assert str(FineExpPerHour(9999999, unit_color = "red"))                         == "9.99<font color=\"red\">M exp/h</font>"
    assert str(FineExpPerHour(9999999, value_color = "blue", unit_color = "red"))   == "<font color=\"blue\">9.99</font><font color=\"red\">M exp/h</font>"


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

