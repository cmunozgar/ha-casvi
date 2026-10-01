from custom_components.casvi.api import menu_text


def test_removes_repeated_footer_with_html_and_line_breaks():
    value = '''<p>* Lentejas con verduras</p><p>* Pan</p>
    <p>NOTA: Primero y segundo plato se pueden repetir. Los niños pequeños pueden
    disponer de un puré variado diario de verduras, patatas y legumbres en sustitución del primer plato.</p>
    <p>Existe a su disposición información sobre las sustancias causantes de alergias e intolerancias alimentarias, conforme al Reglamento nº1169/2011.</p>'''
    result = menu_text(value)
    assert 'Lentejas con verduras' in result
    assert '* Pan' in result
    assert 'NOTA:' not in result
    assert 'Reglamento' not in result


def test_preserves_other_notes_and_dishes_after_footer():
    text = '* Arroz\nNOTA: Menú especial sin gluten.\n* Fruta'
    assert menu_text(text) == text
    assert menu_text(None) == ''
