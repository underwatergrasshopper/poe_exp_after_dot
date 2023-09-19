from poe_exp_after_dot._Private.Overlay import FineTime

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
