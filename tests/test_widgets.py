from types import SimpleNamespace
from custom_components.casvi.sensor import CasviUnreadWidget


def coordinator():
    return SimpleNamespace(entry=SimpleNamespace(entry_id='account'),children={'a':'Child A','b':'Child B'},data={'total':100,'messages':[
        {'id':'1','idPara':2,'leido':'0','fechaEnvio':'2026-09-25','asunto':'Older','idUsuAlumno':'a'},
        {'id':'2','idPara':3,'leido':'0','fechaEnvio':'2026-09-26','asunto':'Newer','alumnosReferidos':[{'id':'a'},{'id':'b'}]},
        {'id':'3','idPara':4,'leido':'0','fechaEnvio':'2026-09-27','asunto':'General'},
        {'id':'4','idPara':5,'leido':'1','fechaEnvio':'2026-09-28','asunto':'Read'},
    ]})


def test_slots_sort_only_unread_and_child_counts_do_not_guess():
    c=coordinator()
    assert CasviUnreadWidget(c).native_value=='General'
    assert CasviUnreadWidget(c,1).native_value=='Newer'
    assert CasviUnreadWidget(c,child='a',count=True).native_value==2
    assert CasviUnreadWidget(c,child='b',count=True).native_value==1
    assert CasviUnreadWidget(c,child='a').native_value=='Newer'
    assert 'message=2&recipient=3' in CasviUnreadWidget(c,child='a').extra_state_attributes['url']


def test_read_message_disappears_and_empty_slot_has_no_stale_metadata():
    c=coordinator();sensor=CasviUnreadWidget(c,2)
    assert sensor.native_value=='Older'
    c.data['messages'][0]['leido']='1'
    assert sensor.native_value=='Sin mensajes pendientes'
    assert 'id' not in sensor.extra_state_attributes
    assert sensor.extra_state_attributes['url']=='/colegio'
