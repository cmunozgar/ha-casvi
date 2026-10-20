from types import SimpleNamespace
from unittest.mock import patch
from custom_components.casvi.panel import update_sidebar


def test_sidebar_tracks_unread_across_accounts_and_preserves_access():
    panel = SimpleNamespace(component_name='custom', sidebar_title='Colegio',
                            sidebar_icon='mdi:school-outline', config={'custom': 'kept'}, require_admin=True)
    row = {'leido': '0'}
    hass = SimpleNamespace(data={'frontend_panels': {'colegio': panel}, 'casvi': {
        'first': SimpleNamespace(data={'messages': []}),
        'second': SimpleNamespace(data={'messages': [row]}),
    }})
    with patch('custom_components.casvi.panel.frontend.async_register_built_in_panel') as register:
        update_sidebar(hass)
        assert register.call_args.kwargs['sidebar_icon'] == 'mdi:email-alert-outline'
        assert register.call_args.kwargs['require_admin'] is True
        assert register.call_args.kwargs['config'] == panel.config
        panel.sidebar_icon = 'mdi:email-alert-outline'
        register.reset_mock()
        update_sidebar(hass)
        register.assert_not_called()
        row['leido'] = '1'
        update_sidebar(hass)
        assert register.call_args.kwargs['sidebar_icon'] == 'mdi:school-outline'
