"""Persist event identities so only newly observed events increase the counter."""
from copy import deepcopy
import hashlib
from homeassistant.exceptions import HomeAssistantError
from .api import plain_text
from homeassistant.helpers.storage import Store


class EventTracker:
    def __init__(self, hass, entry_id):
        self.store = Store(hass, 1, f'casvi.events.{entry_id}')
        self.state = None
        self.hass = hass
        self.entry = None

    async def process(self, agenda):
        if self.state is None:
            self.state = await self.store.async_load() or {'children': {}}
        state = deepcopy(self.state)
        pending = state.setdefault('pending', {})
        targets = self.entry.options.get('notify_targets', []) if self.entry and self.entry.options.get('notify_events', False) else []
        for child, rows in agenda.items():
            ids = {str(row['id']) for row in rows if row.get('id') is not None}
            previous = state['children'].get(child)
            if previous is None:
                state['children'][child] = {'seen': sorted(ids), 'count': 0}
            else:
                seen = set(previous['seen'])
                new_ids = ids - seen
                for row in rows:
                    if str(row.get('id')) not in new_ids:
                        continue
                    props = row.get('extendedProps') or {}
                    title = plain_text(row.get('title')) or plain_text(props.get('tipo')) or 'Nuevo evento'
                    name = (self.entry.data['children'].get(child, '').split() or ['Alumno'])[0] if targets else ''
                    for target in targets:
                        key = hashlib.sha256(f'{child}:{row["id"]}:{target}'.encode()).hexdigest()
                        pending[key] = {'target': target, 'message': f'{name} · {title} · {row.get("start", "")}', 'attempts': 0}
                previous['count'] += len(new_ids)
                previous['seen'] = sorted(seen | ids)
        if state != self.state:
            await self.store.async_save(state)
        self.state = state
        for key, item in list(pending.items()):
            if item['target'] not in targets or not item['target'].startswith('mobile_app_'):
                del pending[key]
            else:
                try:
                    await self.hass.services.async_call('notify', item['target'], {
                        'title': 'Colegio · Nuevo evento', 'message': item['message'],
                        'data': {'url': '/colegio', 'clickAction': '/colegio', 'tag': 'casvi-event-' + key, 'group': 'casvi'},
                    }, blocking=True)
                except HomeAssistantError:
                    item['attempts'] += 1
                    if item['attempts'] >= 3:
                        del pending[key]
                else:
                    del pending[key]
            await self.store.async_save(state)
        return {child: state['children'][child]['count'] for child in agenda}
