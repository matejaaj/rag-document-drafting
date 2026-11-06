from app.services.template.template_parsers.markdown import MarkdownTemplateParser


def test_every_first_and_second_level_heading_becomes_a_section():
    content = "# Uvod\nTekst uvoda.\n## Metodologija\n### Uzorak\n# Zaključak\n".encode()

    template = MarkdownTemplateParser().parse(content, "izvestaj.md")

    assert template.sections == ["Uvod", "Metodologija", "Zaključak"]


def test_template_without_headings_has_one_section_named_after_the_file():
    template = MarkdownTemplateParser().parse("Samo tekst, bez naslova.".encode(), "zapisnik.md")

    assert template.sections == ["zapisnik"]
