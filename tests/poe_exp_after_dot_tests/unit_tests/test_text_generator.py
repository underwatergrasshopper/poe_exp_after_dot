from poe_exp_after_dot._Private.TextGenerator import TextGenerator, TemplateLoader, TextGenFail

_TEMPLATES = """
--- AAA ---
Some text: {xxx}. 
And Another text: {yyy}.
--- BBB, 1s -> AAA ---
Parameters of BBB: {xxx}, {yyy}.
--- CCC, done -> AAA ---
Parameters of CCC: {xxx}, {yyy}.
"""

def test_parse():
    ### default ###
    loader = TemplateLoader()
    loader.parse(_TEMPLATES)

    generator = TextGenerator()
    generator.set_templates(loader.to_templates())

    generator.select_template("AAA")
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Some text: 12. And Another text: dummy."
    generator.update(0.5)
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Some text: 12. And Another text: dummy."
    generator.update(0.5)
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Some text: 12. And Another text: dummy."

    ### delay ###
    loader = TemplateLoader()
    loader.parse(_TEMPLATES)

    generator = TextGenerator()
    generator.set_templates(loader.to_templates())

    generator.select_template("BBB")
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Parameters of BBB: 12, dummy."
    generator.update(0.5)
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Parameters of BBB: 12, dummy."
    generator.update(0.5)
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Some text: 12. And Another text: dummy."
    generator.update(0.5)
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Some text: 12. And Another text: dummy."

    ### done ###
    loader = TemplateLoader()
    loader.parse(_TEMPLATES)

    generator = TextGenerator()
    generator.set_templates(loader.to_templates())

    generator.select_template("CCC")
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Parameters of CCC: 12, dummy."
    generator.update(0.0)
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Some text: 12. And Another text: dummy."

    ### done (delayed done) ###
    loader = TemplateLoader()
    loader.parse(_TEMPLATES)

    generator = TextGenerator()
    generator.set_templates(loader.to_templates())

    generator.select_template("CCC")
    assert generator.gen_text_no_done(xxx = 12, yyy = "dummy") == "Parameters of CCC: 12, dummy."
    generator.update(10.0)
    assert generator.gen_text_no_done(xxx = 12, yyy = "dummy") == "Parameters of CCC: 12, dummy."
    generator.done()
    generator.update(0.0)
    assert generator.gen_text(xxx = 12, yyy = "dummy") == "Some text: 12. And Another text: dummy."

    ### unknown template name ###
    loader = TemplateLoader()
    loader.parse(_TEMPLATES)

    generator = TextGenerator()
    generator.set_templates(loader.to_templates())

    try:
        generator.select_template("ZZZ")
    except TextGenFail as exception:
        assert str(exception) == "There is no template with name \"ZZZ\"."
    else:
        assert False, "No exception has been raised."




