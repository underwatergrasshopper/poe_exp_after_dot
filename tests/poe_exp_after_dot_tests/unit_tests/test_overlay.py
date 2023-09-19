from poe_exp_after_dot._Private.Overlay import FineTime, FineExpPerHour

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
