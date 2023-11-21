from poe_exp_after_dot._Private.TemplateLoader import TemplateLoader, Template, TemplateLoadFail


def test_parse():
    loader = TemplateLoader()
    loader.parse("")
    assert loader.to_templates() == {}
    assert loader.to_variables() == {}
    
    loader = TemplateLoader()
    loader.parse("--- Some Template ---\nAAA")
    assert loader.to_templates() == {"Some Template" : Template("AAA", 0.0, "")}
    assert loader.to_variables() == {}

    loader = TemplateLoader()
    loader.parse("AAA=BBB")
    assert loader.to_templates() == {}
    assert loader.to_variables() == {"AAA" : "BBB"}

    loader = TemplateLoader()
    loader.parse("AAA=BBB\n--- Some Template ---\nAAA")
    assert loader.to_templates() == {"Some Template" : Template("AAA", 0.0, "")}
    assert loader.to_variables() == {"AAA" : "BBB"}

    assert _parse("--- Some Template ---") == ({}, {"Some Template" : Template("", 0.0, "")})
    assert _parse("--- Some Template ---\nAAA") == ({}, {"Some Template" : Template("AAA", 0.0, "")})
    assert _parse("--- Some Template ---\nAAA\nBBB") == ({}, {"Some Template" : Template("AAABBB", 0.0, "")})

    assert _parse("# comment\n--- Some Template ---\nAAA\nBBB") == ({}, {"Some Template" : Template("AAABBB", 0.0, "")})
    assert _parse("# comment\n--- Some Template ---# comment\nAAA# comment\nBBB") == ({}, {"Some Template" : Template("AAABBB", 0.0, "")})

    assert _parse((
        "--- Some Template, done -> Other Template ---\n"
        "AAA"          
    )) == (
        {},
        {
            "Some Template" : Template("AAA", 0.0, "Other Template")
        }
    )

    assert _parse((
        "--- Some Template, 1s -> Other Template ---\n"
        "AAA"          
    )) == (
        {},
        {
            "Some Template" : Template("AAA", 1.0, "Other Template")
        }
    )

    assert _parse((
        "--- Some Template | Another Template, 2s -> Other Template ---\n"
        "AAA"          
    )) == (
        {},
        {
            "Some Template" : Template("AAA", 2.0, "Other Template"),
            "Another Template" : Template("AAA", 2.0, "Other Template")
        }
    )

    assert _parse((
        "---      Some Template     |      Another Template      , 2s     ->     Other Template    ---     \n"
        "AAA"          
    )) == (
        {},
        {
            "Some Template" : Template("AAA", 2.0, "Other Template"),
            "Another Template" : Template("AAA", 2.0, "Other Template")
        }
    )

    assert _parse((
        "--- Some A ---\n"      
        "--- Some B ---\n"
        "YYY\n"          
        "--- Some C | Some D ---\n"
        "AAA\n"          
        "BBB\n"          
    )) == (
        {},
        {
            "Some A" : Template("", 0.0, ""),
            "Some B" : Template("YYY", 0.0, ""),
            "Some C" : Template("AAABBB", 0.0, ""),
            "Some D" : Template("AAABBB", 0.0, "")
        }
    )

    assert _parse((
        "--- Some A, 1s -> Some B ---\n"      
        "--- Some B, 2s -> Some C ---\n"
        "YYY\n"          
        "--- Some C | Some D ---\n"
        "AAA\n"          
        "BBB\n"          
    )) == (
        {},
        {
            "Some A" : Template("", 1.0, "Some B"),
            "Some B" : Template("YYY", 2.0, "Some C"),
            "Some C" : Template("AAABBB", 0.0, ""),
            "Some D" : Template("AAABBB", 0.0, "")
        }
    )

    assert _parse((
        "# comment\n"
        "# comment\n"
        "XXX = TTT # comment\n"
        "\n"
        "YYY = UUU\n"
        "# comment\n"
        "--- Some A, 1s -> Some B ---\n"      
        "--- Some B, 2s -> Some C ---\n"
        "YYY\n"          
        "--- Some C | Some D ---\n"
        "AAA\n"          
        "BBB\n"          
    )) == (
        {
            "XXX" : "TTT",
            "YYY" : "UUU",
        },
        {
            "Some A" : Template("", 1.0, "Some B"),
            "Some B" : Template("YYY", 2.0, "Some C"),
            "Some C" : Template("AAABBB", 0.0, ""),
            "Some D" : Template("AAABBB", 0.0, "")
        }
    )

    assert _parse_with_exception("--- ---") == "No template name. Line: 1."
    assert _parse_with_exception("--- , done -> BBB ---") == "No template name. Line: 1."
    assert _parse_with_exception("--- AAA, 1.2s -> BBB ---") == "Delay is not a valid number. Should be a natural number. Line: 1."
    assert _parse_with_exception("--- AAA, done -> ---") == "No next template name. Line: 1."

    assert _parse_with_exception("=12") == "Variable name is not present. Line: 1."
    assert _parse_with_exception("CCC") == "No assignment to variable. Line: 1."

def _parse(content : str) -> tuple[dict[str, str], dict[str, Template]]:
    loader = TemplateLoader()
    loader.parse(content)
    return (loader.to_variables(), loader.to_templates())

def _parse_with_exception(content : str) -> str | None:
    """
    Returns
        Exception message if occurs.
    """
    loader = TemplateLoader()
    try:
        loader.parse(content)
    except Exception as exception:
        return str(exception)
    return None