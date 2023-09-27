from typing import Any
import json

from poe_exp_after_dot._Private.Settings import Settings

def test_settings_none_existing(tmpdir):
    file_name = tmpdir + "/settings.json"

    settings = Settings(file_name, {})
    settings.load_and_add_temporal({})
    settings.save()

    assert settings._default == {}
    assert settings._temporal == {}
    assert settings._settings == {}

    assert _load_settings(file_name) == {}

def test_settings_empty(tmpdir):
    file_name = tmpdir + "/settings.json"

    _make_settings(file_name, {})

    settings = Settings(file_name, {})
    settings.load_and_add_temporal({})
    settings.save()

    assert settings._default == {}
    assert settings._temporal == {}
    assert settings._settings == {}

    assert _load_settings(file_name) == {}

def test_settings_no_default_no_file_no_temporal(tmpdir):
    file_name = tmpdir + "/settings.json"

    settings = Settings(file_name, {})
    settings.load_and_add_temporal({})

    assert settings._default    == {}
    assert settings._temporal   == {}
    assert settings._settings   == {}

    ### set ###

    settings.set_val("aaa", 12, int)

    assert settings._default    == {}
    assert settings._temporal   == {"aaa" : 12}
    assert settings._settings   == {"aaa" : 12}
    
    settings.set_val("bbb.ccc", 23, int)

    assert settings._default    == {}
    assert settings._temporal   == {"aaa" : 12, "bbb" : {"ccc" : 23}}
    assert settings._settings   == {"aaa" : 12, "bbb" : {"ccc" : 23}}

    settings.set_val("bbb.ddd", 45, int, is_temporal_only = True)

    assert settings._default    == {}
    assert settings._temporal   == {"aaa" : 12, "bbb" : {"ccc" : 23, "ddd" : 45}}
    assert settings._settings   == {"aaa" : 12, "bbb" : {"ccc" : 23}}
    
    settings.set_val("bbb.eee", 67, str)

    assert settings._default    == {}
    assert settings._temporal   == {"aaa" : 12, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}}
    assert settings._settings   == {"aaa" : 12, "bbb" : {"ccc" : 23, "eee" : "67"}}

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
    assert settings.get_val("bbb.ddd", int, is_temporal = True) == 45

    ### save ###

    settings.save()

    assert _load_settings(file_name) == {"aaa" : 12, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_no_file_no_temporal(tmpdir):
    file_name = tmpdir + "/settings.json"

    settings = Settings(file_name, {"nnn" : 15, "bbb" : {"ccc" : 1}})
    settings.load_and_add_temporal({})

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._settings   == {"nnn" : 15, "bbb" : {"ccc" : 1}}

    ### set ###

    settings.set_val("aaa", 12, int)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 1}}
    
    settings.set_val("bbb.ccc", 23, int)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}

    settings.set_val("bbb.ddd", 45, int, is_temporal_only = True)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "ddd" : 45}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    
    settings.set_val("bbb.eee", 67, str)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

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
    assert settings.get_val("bbb.ddd", int, is_temporal = True) == 45

    ### save ###
    
    settings.save()

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_no_temporal(tmpdir):
    file_name = tmpdir + "/settings.json"

    _make_settings(file_name, {"aaa" : 2, "bbb" : {"ccc" : -1}})

    settings = Settings(file_name, {"nnn" : 15, "bbb" : {"ccc" : 1}})
    settings.load_and_add_temporal({})

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 2, "nnn" : 15, "bbb" : {"ccc" : -1}}
    assert settings._settings   == {"aaa" : 2, "nnn" : 15, "bbb" : {"ccc" : -1}}

    ### set ###

    settings.set_val("aaa", 12, int)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : -1}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : -1}}
    
    settings.set_val("bbb.ccc", 23, int)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}

    settings.set_val("bbb.ddd", 45, int, is_temporal_only = True)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "ddd" : 45}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    
    settings.set_val("bbb.eee", 67, str)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

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
    assert settings.get_val("bbb.ddd", int, is_temporal = True) == 45

    ### save ###
    
    settings.save()

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

def test_settings_all(tmpdir):
    file_name = tmpdir + "/settings.json"

    _make_settings(file_name, {"aaa" : 2, "bbb" : {"ccc" : -1}})

    settings = Settings(file_name, {"nnn" : 15, "bbb" : {"ccc" : 1}})
    settings.load_and_add_temporal({"nnn" : -15, "zzz" : {"qqq" : 67}})

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 2, "nnn" : -15, "bbb" : {"ccc" : -1}, "zzz" : {"qqq" : 67}}
    assert settings._settings   == {"aaa" : 2, "nnn" : 15, "bbb" : {"ccc" : -1}}

    ### set ###

    settings.set_val("aaa", 12, int)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : -1}, "zzz" : {"qqq" : 67}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : -1}}
    
    settings.set_val("bbb.ccc", 23, int)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23}, "zzz" : {"qqq" : 67}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}

    settings.set_val("bbb.ddd", 45, int, is_temporal_only = True)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23, "ddd" : 45}, "zzz" : {"qqq" : 67}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23}}
    
    settings.set_val("bbb.eee", 67, str)

    assert settings._default    == {"nnn" : 15, "bbb" : {"ccc" : 1}}
    assert settings._temporal   == {"aaa" : 12, "nnn" : -15, "bbb" : {"ccc" : 23, "ddd" : 45, "eee" : "67"}, "zzz" : {"qqq" : 67}}
    assert settings._settings   == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

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
    assert settings.get_val("bbb.ddd", int, is_temporal = True) == 45

    ### save ###
    
    settings.save()

    assert _load_settings(file_name) == {"aaa" : 12, "nnn" : 15, "bbb" : {"ccc" : 23, "eee" : "67"}}

def _make_settings(file_name : str, settings : dict[str, Any]):
    with open(file_name, "w") as file:
        file.write(json.dumps(settings, indent = 4))

def _load_settings(file_name : str) -> dict[str, Any]:
    with open(file_name, "r") as file:
        return json.loads(file.read())


