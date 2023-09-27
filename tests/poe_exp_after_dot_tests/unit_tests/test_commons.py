from poe_exp_after_dot._Private.Commons import merge_on_all_levels


def test_merge_on_all_levels():
    assert merge_on_all_levels({}, {}) == {}
    assert merge_on_all_levels({"a" : 1}, {}) == {"a" : 1}
    assert merge_on_all_levels({}, {"a" : 1}) == {"a" : 1}
    assert merge_on_all_levels({"a" : 1}, {"b" : 2}) == {"a" : 1, "b" : 2}
    assert merge_on_all_levels({"a" : 1, "c" : 3}, {"b" : 2}) == {"a" : 1, "b" : 2, "c" : 3}
    assert merge_on_all_levels({"a" : 1}, {"b" : 2, "c" : 3}) == {"a" : 1, "b" : 2, "c" : 3}

    assert merge_on_all_levels({"a" : 1, "c" : 4}, {"b" : 2, "c" : 3}) == {"a" : 1, "b" : 2, "c" : 3}
    assert merge_on_all_levels({"a" : 1, "c" : {}}, {"b" : 2, "c" : 3}) == {"a" : 1, "b" : 2, "c" : 3}
    assert merge_on_all_levels({"a" : 1, "c" : 4}, {"b" : 2, "c" : {}}) == {"a" : 1, "b" : 2, "c" : {}}

    assert merge_on_all_levels({"a" : 1, "c" : 4}, {"b" : 2, "c" : {"d" : 15}}) == {"a" : 1, "b" : 2, "c" : {"d" : 15}}
    assert merge_on_all_levels({"a" : 1, "c" : {}}, {"b" : 2, "c" : {"d" : 15}}) == {"a" : 1, "b" : 2, "c" : {"d" : 15}}
    assert merge_on_all_levels({"a" : 1, "c" : {"d" : 10}}, {"b" : 2, "c" : {"d" : 15}}) == {"a" : 1, "b" : 2, "c" : {"d" : 15}}
    assert merge_on_all_levels({"a" : 1, "c" : {"d" : 10, "e" : 88}}, {"b" : 2, "c" : {"d" : 15}}) == {"a" : 1, "b" : 2, "c" : {"d" : 15, "e" : 88}}

    assert merge_on_all_levels({"a" : 1, "c" : {"d" : 10, "e" : {"f" : 88, "g" : 44}}}, {"b" : 2, "c" : {"d" : 15, "e" : {"f" : 99, "h" : 71}}}) == {"a" : 1, "b" : 2, "c" : {"d" : 15, "e" : {"f" : 99, "g" : 44, "h" : 71}}}

