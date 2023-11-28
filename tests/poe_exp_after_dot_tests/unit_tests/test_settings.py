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
    except Exception as exception:
        assert str(exception) == "Can not get value from temporal settings with full name \"xxx\"."
    else:
        assert False, "Expected exception."

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
    except Exception as exception:
        assert str(exception) == "Can not get value from temporal settings with full name \"xxx\"."
    else:
        assert False, "Expected exception."

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
    except Exception as exception:
        assert str(exception) == "Can not get value from temporal settings with full name \"xxx\"."
    else:
        assert False, "Expected exception."

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
    except Exception as exception:
        assert str(exception) == "Can not get value from temporal settings with full name \"xxx\"."
    else:
        assert False, "Expected exception."

    assert settings.get_val("aaa", int) == 12
    assert settings.get_val("bbb.ccc", int) == 23
    assert settings.get_val("bbb.eee", int) == 67
    assert settings.get_val("bbb.eee", str) == "67"
    assert settings.get_val("bbb.ddd", int, is_from_temporal = True) == 45

    ### save ###
    
    settings.save(file_name)

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_all_with_merge(tmpdir):
    file_name = tmpdir + "/settings.json"

    _make_settings(file_name, {"aaa" : 2, "bbb" : {"ccc" : -1}})

    settings = Settings()

    ### default and temporal ###

    settings.merge_with({
        "nnn" : 15,
        "bbb" : {
            "ccc" : 1
        }
    })

    settings.load(file_name)

    settings.merge_with({
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
    except Exception as exception:
        assert str(exception) == "Can not get value from temporal settings with full name \"xxx\"."
    else:
        assert False, "Expected exception."

    assert settings.get_val("aaa", int) == 12
    assert settings.get_val("bbb.ccc", int) == 23
    assert settings.get_val("bbb.eee", int) == 67
    assert settings.get_val("bbb.eee", str) == "67"
    assert settings.get_val("bbb.ddd", int, is_from_temporal = True) == 45

    ### save ###
    
    settings.save(file_name)

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}


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


def _make_settings(file_name : str, settings : dict[str, Any]):
    with open(file_name, "w") as file:
        file.write(json.dumps(settings, indent = 4))

def _load_settings(file_name : str) -> dict[str, Any]:
    with open(file_name, "r") as file:
        return json.loads(file.read())


