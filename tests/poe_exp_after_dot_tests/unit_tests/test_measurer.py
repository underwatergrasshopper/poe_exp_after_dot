from math import isclose as _isclose
from time import time as _get_time

from poe_exp_after_dot._Private.FineFormatters import SECONDS_IN_WEEK, SECONDS_IN_DAY, SECONDS_IN_HOUR, SECONDS_IN_MINUTE
from poe_exp_after_dot._Private.FineFormatters import FineTime, FineExpPerHour, FinePercent, FineBareLevel, FineExp
from poe_exp_after_dot._Private.Logic          import Measurer

def test_measurer():
    time_ = 0

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

    time_ += 5.0 * 60
    measurer.update(900, time_)
    
    assert measurer.is_update_fail() == False

    assert measurer.get_level() == 2

    assert _isclose(measurer.get_progress(), 30.3643, abs_tol = 0.0001)

    assert _isclose(measurer.get_progress_step(), 30.3643, abs_tol = 0.0001)
    assert measurer.get_progress_step_in_exp() == 375
    assert measurer.get_progress_step_time() == 0

    assert measurer.get_time_to_10_percent() == float('inf')
    assert measurer.get_time_to_next_level() == float('inf')

    time_ += 2.0 * 60
    measurer.update(1000, time_)
    
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
    # 12.8M exp/h
    # 10% in 3h05m10s
    # next in 1d10h30m45s

    measurer = Measurer()

    assert _update(measurer, 0, 1) == (
        "LVL 1 0.00%\n"
        "+0.00% in 0s\n"
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
        "10% in 2s\n"
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
        "10% in <1s\n"
        "next in 3s\n"
    )
    assert _update(measurer, 263, 1) == (
        "LVL 1 50.09%\n"
        "+12.00% in 1s\n"
        "226k exp/h\n"
        "10% in <1s\n"
        "next in 4s\n"
    )
    assert _update(measurer, 524, 10) == (
        "LVL 1 99.80%\n"
        "+49.71% in 10s\n"
        "93.9k exp/h\n"
        "10% in 2s\n"
        "next in <1s\n"
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
        "10% in 1s\n"
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
        "10% in 12m07s\n"
        "next in 46m51s\n"
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

_time_accumulator = 0.0

def _update(measurer : Measurer, total_exp : int, elapsed_time : float) -> str:
    global _time_accumulator
    _time_accumulator += elapsed_time
    measurer.update(total_exp, _time_accumulator)

    return (
        f"LVL {measurer.get_level()} {FinePercent(measurer.get_progress())}\n"
        f"{FinePercent(measurer.get_progress_step(), is_sign = True)} in {FineTime(measurer.get_progress_step_time())}\n"
        f"{FineExpPerHour(measurer.get_exp_per_hour())}\n"
        f"10% in {FineTime(measurer.get_time_to_10_percent())}\n"
        f"next in {FineTime(measurer.get_time_to_next_level())}\n"
    )
