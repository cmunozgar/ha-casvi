from custom_components.casvi.message_format import message_nodes


def test_preserves_deliberate_breaks_and_formatting_without_source_indent():
    nodes=message_nodes('<p>Para niños:<br>🏊 Natación<br>🎯 Perfeccionamiento</p><p><u>TÍTULO</u></p><ul><li>Uno</li><li>Dos</li></ul>')
    assert [n.get('tag') for n in nodes[0]['children']]==[None,'br',None,'br',None]
    assert nodes[1]['children'][0]['tag']=='u'
    assert nodes[2]['tag']=='ul'
    assert message_nodes('<p>Hola\n     familias</p>')[0]['children']==[{'text':'Hola familias'}]


def test_removes_hidden_markers_and_active_html_and_keeps_safe_links():
    nodes=message_nodes('<p>A<span style="display:none">?<b>?</b></span><script>alert(1)</script><a href="https://example.com" onclick="bad()">Formulario</a><img src="https://example.com/tracker"></p>')
    assert nodes[0]['children']==[{'text':'A'},{'tag':'a','children':[{'text':'Formulario'}],'href':'https://example.com'}]
    assert 'href' not in message_nodes('<a href="javascript:alert(1)">No</a>')[0]
