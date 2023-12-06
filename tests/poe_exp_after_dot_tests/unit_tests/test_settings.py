from typing import Any
import json

from poe_exp_after_dot._Private.Settings import Settings

def test_settings_none_existing(tmpdir):
    file_name = tmpdir + "/settings.json"

    settings = Settings()
    settings.load(file_name)
    settings.save(file_name)

    assert settings.to_temporal() == {}
    assert settings.to_persistent() == {}

    assert _load_settings(file_name) == {}

def test_settings_empty(tmpdir):
    file_name = tmpdir + "/settings.json"

    _make_settings(file_name, {})

    settings = Settings()
    settings.load(file_name)
    settings.save(file_name)

    assert settings.to_temporal() == {}
    assert settings.to_persistent() == {}

    assert _load_settings(file_name) == {}

def test_settings_no_default_no_file_no_temporal(tmpdir):
    file_name = tmpdir + "/settings.json"

    settings = Settings()
    settings.load(file_name)
    settings.save(file_name)

    assert settings.to_temporal()   == {}
    assert settings.to_persistent() == {}

    ### set ###

    settings.set_val("aaa", 12, int)

    assert settings.to_temporal()   == {"aaa" : 12}
    assert settings.to_persistent() == {"aaa" : 12}
    
    settings.set_val("bbb.ccc", 23, int)

    assert settings.to_temporal()   == {"aaa" : 12, "bbb" : {"ccc" : 23}}
    assert settings.to_persistent() == {"aaa" : 12, "bbb" : {"ccc" : 23}}

    settings.set_val("bbb.ddd", 45, int, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 12, "bbb" : {"ccc" : 23, "ddd" : 45}}
    assert settings.to_persistent() == {"aaa" : 12, "bbb" : {"ccc" : 23}}
    
    settings.set_val("bbb.eee", 67, str)

    assert settings.to_temporal()   == {"aaa" : 12, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}}
    assert settings.to_persistent() == {"aaa" : 12, "bbb" : {"ccc" : 23, "eee" : "67"}}

    ### get ###
    try:
        settings.get_val("xxx", int)
    except KeyError as exception:
        assert str(exception) == "'xxx'"
    else:
        assert False, "Expected KeyError exception."

    try:
        settings.get_val("xxx.kkk.lll", int)
    except KeyError as exception:
        assert str(exception) == "'xxx.kkk.lll'"
    else:
        assert False, "Expected KeyError exception."

    assert settings.get_val("aaa", int) == 12
    assert settings.get_val("bbb.ccc", int) == 23
    assert settings.get_val("bbb.eee", int) == 67
    assert settings.get_val("bbb.eee", str) == "67"
    assert settings.get_val("bbb.ddd", int, is_from_temporal = True) == 45

    assert settings.try_get_val("xxx", int) == None

    assert settings.try_get_val("aaa", int) == 12
    assert settings.try_get_val("bbb.ccc", int) == 23
    assert settings.try_get_val("bbb.eee", int) == 67
    assert settings.try_get_val("bbb.eee", str) == "67"
    assert settings.try_get_val("bbb.ddd", int, is_from_temporal = True) == 45

    ### save ###

    settings.save(file_name)

    assert _load_settings(file_name) == {"aaa" : 12, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_no_file_no_temporal(tmpdir):
    file_name = tmpdir + "/settings.json"

    settings = Settings()

    #### default ###
    settings.set_val("nnn", 15, int)
    settings.set_val("bbb.ccc", 1, int)

    assert settings.to_temporal()     == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings.to_persistent()   == {"nnn" : 15, "bbb" : {"ccc" : 1}}

    settings.load(file_name)

    assert settings.to_temporal()     == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings.to_persistent()   == {"nnn" : 15, "bbb" : {"ccc" : 1}}

    ### set ###

    settings.set_val("aaa", 12, int)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 1}}
    
    settings.set_val("bbb.ccc", 23, int)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}

    settings.set_val("bbb.ddd", 45, int, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "ddd" : 45}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    
    settings.set_val("bbb.eee", 67, str)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

    ### get ###

    try:
        settings.get_val("xxx", int)
    except KeyError as exception:
        assert str(exception) == "'xxx'"
    else:
        assert False, "Expected KeyError exception."

    try:
        settings.get_val("xxx.kkk.lll", int)
    except KeyError as exception:
        assert str(exception) == "'xxx.kkk.lll'"
    else:
        assert False, "Expected KeyError exception."

    assert settings.get_val("aaa", int) == 12
    assert settings.get_val("bbb.ccc", int) == 23
    assert settings.get_val("bbb.eee", int) == 67
    assert settings.get_val("bbb.eee", str) == "67"
    assert settings.get_val("bbb.ddd", int, is_from_temporal = True) == 45

    ### save ###
    
    settings.save(file_name)

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_no_temporal(tmpdir):
    file_name = tmpdir + "/settings.json"

    _make_settings(file_name, {"aaa" : 2, "bbb" : {"ccc" : -1}})

    settings = Settings()

    ### default ###

    settings.set_val("nnn", 15, int)
    settings.set_val("bbb.ccc", 1, int)

    settings.load(file_name)

    assert settings.to_temporal()   == {"aaa" : 2, "nnn" : 15, "bbb" : {"ccc" : -1}}
    assert settings.to_persistent() == {"aaa" : 2, "nnn" : 15, "bbb" : {"ccc" : -1}}

    ### set ###

    settings.set_val("aaa", 12, int)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : -1}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : -1}}
    
    settings.set_val("bbb.ccc", 23, int)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}

    settings.set_val("bbb.ddd", 45, int, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "ddd" : 45}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    
    settings.set_val("bbb.eee", 67, str)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

    ### get ###

    try:
        settings.get_val("xxx", int)
    except KeyError as exception:
        assert str(exception) == "'xxx'"
    else:
        assert False, "Expected KeyError exception."

    try:
        settings.get_val("xxx.kkk.lll", int)
    except KeyError as exception:
        assert str(exception) == "'xxx.kkk.lll'"
    else:
        assert False, "Expected KeyError exception."

    assert settings.get_val("aaa", int) == 12
    assert settings.get_val("bbb.ccc", int) == 23
    assert settings.get_val("bbb.eee", int) == 67
    assert settings.get_val("bbb.eee", str) == "67"
    assert settings.get_val("bbb.ddd", int, is_from_temporal = True) == 45

    ### save ###
    
    settings.save(file_name)

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_all(tmpdir):
    file_name = tmpdir + "/settings.json"

    _make_settings(file_name, {"aaa" : 2, "bbb" : {"ccc" : -1}})

    settings = Settings()

    ### default and temporal ###

    settings.set_val("nnn", 15, int)
    settings.set_val("bbb.ccc", 1, int)

    settings.load(file_name)

    settings.set_tmp_val("nnn", -15, int)
    settings.set_val("zzz.qqq", 67, int, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 2, "nnn" : -15, "bbb" : {"ccc" : -1}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 2, "nnn" : 15, "bbb" : {"ccc" : -1}}

    ### set ###

    settings.set_val("aaa", 12, int)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : -1}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : -1}}
    
    settings.set_val("bbb.ccc", 23, int)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}

    settings.set_val("bbb.ddd", 45, int, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23, "ddd" : 45}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    
    settings.set_val("bbb.eee", 67, str)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

    ### get ###

    try:
        settings.get_val("xxx", int)
    except KeyError as exception:
        assert str(exception) == "'xxx'"
    else:
        assert False, "Expected KeyError exception."

    try:
        settings.get_val("xxx.kkk.lll", int)
    except KeyError as exception:
        assert str(exception) == "'xxx.kkk.lll'"
    else:
        assert False, "Expected KeyError exception."

    assert settings.get_val("aaa", int) == 12
    assert settings.get_val("bbb.ccc", int) == 23
    assert settings.get_val("bbb.eee", int) == 67
    assert settings.get_val("bbb.eee", str) == "67"
    assert settings.get_val("bbb.ddd", int, is_from_temporal = True) == 45

    ### save ###
    
    settings.save(file_name)

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_all_specific(tmpdir):
    file_name = tmpdir + "/settings.json"

    _make_settings(file_name, {"aaa" : 2, "bbb" : {"ccc" : -1}})

    settings = Settings()

    ### default and temporal ###

    settings.set_val("nnn", 15, int)
    settings.set_val("bbb.ccc", 1, int)

    settings.load(file_name)

    settings.set_tmp_int("nnn", -15)
    settings.set_int("zzz.qqq", 67, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 2, "nnn" : -15, "bbb" : {"ccc" : -1}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 2, "nnn" : 15, "bbb" : {"ccc" : -1}}

    ### set ###

    settings.set_int("aaa", 12)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : -1}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : -1}}
    
    settings.set_int("bbb.ccc", 23)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}

    settings.set_int("bbb.ddd", 45, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23, "ddd" : 45}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    
    settings.set_str("bbb.eee", 67)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

    ### get ###

    try:
        settings.get_int("xxx")
    except KeyError as exception:
        assert str(exception) == "'xxx'"
    else:
        assert False, "Expected KeyError exception."

    assert settings.try_get_int("xxx") is None

    try:
        settings.get_int("xxx.kkk.lll")
    except KeyError as exception:
        assert str(exception) == "'xxx.kkk.lll'"
    else:
        assert False, "Expected KeyError exception."

    assert settings.try_get_int("xxx.kkk.lll") is None

    assert settings.get_int("aaa") == 12
    assert settings.get_int("bbb.ccc") == 23
    assert settings.get_int("bbb.eee") == 67
    assert settings.get_str("bbb.eee") == "67"
    assert settings.get_int("bbb.ddd", is_from_temporal = True) == 45

    ### save ###
    
    settings.save(file_name)

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_specific(tmpdir):
    settings = Settings()

    ### default and temporal ###

    settings.set_int("aaa", 15.1)
    settings.set_float("bbb", 1.3)
    settings.set_str("ccc", 12)
    d = {"xxx" : 88}
    settings.set_dict("ddd", d)
    l = [23, 34, 45]
    settings.set_list("eee", l)
    settings.set_bool("fff", True)

    d["xxx"] = 11
    l[0] = 5

    assert settings.to_temporal()   == {"aaa" : 15, "bbb" : 1.3, "ccc" : "12", "ddd" : {"xxx" : 88}, "eee" : [23, 34, 45], "fff" : True}
    assert settings.to_persistent() == settings.to_temporal() 

    assert settings.get_int("aaa") == 15
    assert settings.get_float("bbb") == 1.3
    assert settings.get_str("ccc") == "12"
    assert settings.get_dict("ddd") == {"xxx" : 88}
    assert settings.get_list("eee") == [23, 34, 45]
    assert settings.get_bool("fff") == True

    settings.set_tmp_int("aaa", 16.1)
    settings.set_tmp_float("bbb", 2.3)
    settings.set_tmp_str("ccc", 13)
    d = {"xxx" : 89}
    settings.set_tmp_dict("ddd", d)
    l = [123, 134, 145]
    settings.set_tmp_list("eee", l)
    settings.set_tmp_bool("fff", False)

    d["xxx"] = 11
    l[0] = 5

    assert settings.to_temporal()   == {"aaa" : 16, "bbb" : 2.3, "ccc" : "13", "ddd" : {"xxx" : 89}, "eee" : [123, 134, 145], "fff" : False}
    assert settings.to_persistent() == {"aaa" : 15, "bbb" : 1.3, "ccc" : "12", "ddd" : {"xxx" : 88}, "eee" : [23, 34, 45], "fff" : True}

    assert settings.get_int("aaa") == 16
    assert settings.get_float("bbb") == 2.3
    assert settings.get_str("ccc") == "13"
    assert settings.get_dict("ddd") == {"xxx" : 89}
    assert settings.get_list("eee") == [123, 134, 145]
    assert settings.get_bool("fff") == False

    assert settings.get_int("aaa", is_from_temporal = False) == 15
    assert settings.get_float("bbb", is_from_temporal = False) == 1.3
    assert settings.get_str("ccc", is_from_temporal = False) == "12"
    assert settings.get_dict("ddd", is_from_temporal = False) == {"xxx" : 88}
    assert settings.get_list("eee", is_from_temporal = False) == [23, 34, 45]
    assert settings.get_bool("fff", is_from_temporal = False) == True

    assert settings.try_get_int("aaa") == 16
    assert settings.try_get_float("bbb") == 2.3
    assert settings.try_get_str("ccc") == "13"
    assert settings.try_get_dict("ddd") == {"xxx" : 89}
    assert settings.try_get_list("eee") == [123, 134, 145]
    assert settings.try_get_bool("fff") == False

    assert settings.try_get_int("aaa", is_from_temporal = False) == 15
    assert settings.try_get_float("bbb", is_from_temporal = False) == 1.3
    assert settings.try_get_str("ccc", is_from_temporal = False) == "12"
    assert settings.try_get_dict("ddd", is_from_temporal = False) == {"xxx" : 88}
    assert settings.try_get_list("eee", is_from_temporal = False) == [23, 34, 45]
    assert settings.try_get_bool("fff", is_from_temporal = False) == True

def test_settings_bool(tmpdir):
    settings = Settings()

    settings.set_int("aaa", 0)
    settings.set_int("bbb", 1)

    assert settings.to_temporal()   == {"aaa" : 0, "bbb" : 1}
    assert settings.to_persistent() == settings.to_temporal() 

    settings.get_bool("aaa") == False
    settings.get_bool("bbb") == True


def test_settings_all_with_merge(tmpdir):
    file_name = tmpdir + "/settings.json"

    _make_settings(file_name, {"aaa" : 2, "bbb" : {"ccc" : -1}})

    settings = Settings()

    ### default and temporal ###

    settings.merge({
        "nnn" : 15,
        "bbb" : {
            "ccc" : 1
        }
    })

    settings.load(file_name)

    settings.merge({
        "nnn" : -15,
        "zzz" : {
            "qqq" : 67
        }
    }, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 2, "nnn" : -15, "bbb" : {"ccc" : -1}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 2, "nnn" : 15, "bbb" : {"ccc" : -1}}

    ### set ###

    settings.set_val("aaa", 12, int)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : -1}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : -1}}
    
    settings.set_val("bbb.ccc", 23, int)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}

    settings.set_val("bbb.ddd", 45, int, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23, "ddd" : 45}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    
    settings.set_val("bbb.eee", 67, str)

    assert settings.to_temporal()   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}, "zzz" : {"qqq" : 67}}
    assert settings.to_persistent() == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

    ### get ###

    try:
        settings.get_val("xxx", int)
    except KeyError as exception:
        assert str(exception) == "'xxx'"
    else:
        assert False, "Expected KeyError exception."

    try:
        settings.get_val("xxx.kkk.lll", int)
    except KeyError as exception:
        assert str(exception) == "'xxx.kkk.lll'"
    else:
        assert False, "Expected KeyError exception."

    assert settings.get_val("aaa", int) == 12
    assert settings.get_val("bbb.ccc", int) == 23
    assert settings.get_val("bbb.eee", int) == 67
    assert settings.get_val("bbb.eee", str) == "67"
    assert settings.get_val("bbb.ddd", int, is_from_temporal = True) == 45

    ### save ###
    
    settings.save(file_name)

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_get_dict():
    settings = Settings()

    settings.set_val("aaa.bbb.ccc", 1, int)
    settings.set_val("aaa.bbb.ddd", 12, int)

    assert settings.get_val("aaa") == {"bbb" : { "ccc" : 1 , "ddd" : 12}}

def test_settings_copy():
    settings = Settings()

    settings.set_val("aaa", 15, int)
    settings.set_val("bbb.ccc", 1, int)

    assert settings.to_temporal()   == {"aaa" : 15, "bbb" : { "ccc" : 1}}
    assert settings.to_persistent() == settings.to_temporal() 

    settings.copy_val("aaa", "ddd")

    assert settings.to_temporal()   == {"aaa" : 15, "ddd" : 15, "bbb" : { "ccc" : 1}}
    assert settings.to_persistent() == settings.to_temporal() 

    settings.copy_val("bbb.ccc", "xxx.mmm")

    assert settings.to_temporal()   == {"aaa" : 15, "ddd" : 15, "bbb" : { "ccc" : 1}, "xxx" : { "mmm" : 1}}
    assert settings.to_persistent() == settings.to_temporal() 

    settings.copy_tmp_val("bbb.ccc", "aaa")

    assert settings.to_temporal()   == {"aaa" : 1, "ddd" : 15, "bbb" : { "ccc" : 1}, "xxx" : { "mmm" : 1}}
    assert settings.to_persistent() == {"aaa" : 15, "ddd" : 15, "bbb" : { "ccc" : 1}, "xxx" : { "mmm" : 1}}

    settings.copy_val("bbb", "aaa", is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : { "ccc" : 1}, "ddd" : 15, "bbb" : { "ccc" : 1}, "xxx" : { "mmm" : 1}}
    assert settings.to_persistent() == {"aaa" : 15, "ddd" : 15, "bbb" : { "ccc" : 1}, "xxx" : { "mmm" : 1}}

    settings.copy_val("aaa", "aaa", is_from_temporal = False, is_into_temporal_only = True)

    assert settings.to_temporal()   == {"aaa" : 15, "ddd" : 15, "bbb" : { "ccc" : 1}, "xxx" : { "mmm" : 1}}
    assert settings.to_persistent() == {"aaa" : 15, "ddd" : 15, "bbb" : { "ccc" : 1}, "xxx" : { "mmm" : 1}}

    settings.copy_val("xxx", "aaa", is_from_temporal = False, is_into_temporal_only = False)

    assert settings.to_temporal()   == {"aaa" : { "mmm" : 1}, "ddd" : 15, "bbb" : { "ccc" : 1}, "xxx" : { "mmm" : 1}}
    assert settings.to_persistent() == {"aaa" : { "mmm" : 1}, "ddd" : 15, "bbb" : { "ccc" : 1}, "xxx" : { "mmm" : 1}}

def test_settings_set_dict():

    settings = Settings()

    settings.set_val("aaa", {"bbb" : 12, "ccc" : 14})

    assert settings.to_temporal()   == {"aaa" : {"bbb" : 12, "ccc" : 14}}
    assert settings.to_persistent() == settings.to_temporal() 

    settings.set_val("aaa.bbb", {"xxx" : 23, "yyy" : 34})

    assert settings.to_temporal()   == {"aaa" : {"bbb" : {"xxx" : 23, "yyy" : 34}, "ccc" : 14}}
    assert settings.to_persistent() == settings.to_temporal() 

    assert settings.get_val("aaa.bbb.xxx") == 23
    assert settings.get_val("aaa.bbb.yyy") == 34
    assert settings.get_val("aaa.ccc") == 14

    assert settings.get_val("aaa.bbb") == {"xxx" : 23, "yyy" : 34}

def test_settings_set_list():

    settings = Settings()

    settings.set_val("aaa.bbb", [12, 23, 34])

    assert settings.to_temporal()   == {"aaa" : {"bbb" : [12, 23, 34]}}
    assert settings.to_persistent() == settings.to_temporal() 

    assert settings.get_val("aaa.bbb") == [12, 23, 34]


def _make_settings(file_name : str, settings : dict[str, Any]):
    with open(file_name, "w") as file:
        file.write(json.dumps(settings, indent = 4))

def _load_settings(file_name : str) -> dict[str, Any]:
    with open(file_name, "r") as file:
        return json.loads(file.read())


