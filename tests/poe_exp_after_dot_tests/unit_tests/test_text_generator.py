from poe_exp_after_dot._Private.TextGenerator import TextGenerator, TemplateLoader, TextGenFail

_TEMPLATES = """
--- AAA ---
Some text: {xxx}. 
And Another text: {yyy}.
--- BBB, 1s -> AAA ---
Parameters of BBB: {xxx}, {yyy}.
--- CCC ---
{AAA} 
More text: {zzz}.
"""

def test_parse():
    def get_parameters():
        return {
            "xxx" : 12,
            "yyy" : "dummy",
            "zzz" : "another",
        }
    
    text_out = ""
    def set_text(text : str):
        nonlocal text_out
        text_out = text

    def take_text() -> str:
        nonlocal text_out
        text = text_out
        text_out = ""
        return text

    ### default ###
    loader = TemplateLoader()
    loader.parse(_TEMPLATES)

    generator = TextGenerator(loader.to_templates(), get_parameters, set_text)
    text_out = ""

    assert generator.gen_text("AAA") == "Some text: 12. And Another text: dummy."
    assert take_text() == "Some text: 12. And Another text: dummy."
    generator._update(0.5)
    assert take_text() == ""
    generator._update(0.5)
    assert take_text() == ""

    ### delay ###
    loader = TemplateLoader()
    loader.parse(_TEMPLATES)

    generator = TextGenerator(loader.to_templates(), get_parameters, set_text)
    text_out = ""

    assert generator.gen_text("BBB") == "Parameters of BBB: 12, dummy."
    assert take_text() == "Parameters of BBB: 12, dummy."
    generator._update(0.5)
    assert take_text() == ""
    generator._update(0.5)
    assert take_text() == "Some text: 12. And Another text: dummy."

    ### nesting ###
    loader = TemplateLoader()
    loader.parse(_TEMPLATES)

    generator = TextGenerator(loader.to_templates(), get_parameters, set_text)
    text_out = ""

    assert generator.gen_text("CCC") == "Some text: 12. And Another text: dummy. More text: another."
    assert take_text() == "Some text: 12. And Another text: dummy. More text: another."
    generator._update(0.5)
    assert take_text() == ""
    generator._update(0.5)
    assert take_text() == ""

    ### unknown template name ###
    loader = TemplateLoader()
    loader.parse(_TEMPLATES)

    generator = TextGenerator(loader.to_templates(), get_parameters, set_text)
    text_out = ""

    try:
        generator.gen_text("ZZZ")
    except TextGenFail as exception:
        assert str(exception) == "There is no template with name \"ZZZ\"."
    else:
        assert False, "No exception has been raised."




