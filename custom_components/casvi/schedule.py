"""Read supported weekly PDF tables locally, without OCR or remote services."""
from datetime import date
from io import BytesIO
import re
import unicodedata
import pdfplumber
from homeassistant.helpers.storage import Store


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFD', value or '') if not unicodedata.combining(c)).lower()


def parse_schedule(pdf):
    with pdfplumber.open(BytesIO(pdf)) as document:
        for page in document.pages[:3]:
            for table in page.extract_tables():
                if not table or len(table[0]) != 6:
                    continue
                if [normalized(c).strip() for c in table[0][1:]] != ['lunes','martes','miercoles','jueves','viernes']:
                    continue
                rows = []
                for cells in table[1:]:
                    if len(cells) != 6:
                        raise ValueError('Unsupported schedule row')
                    times = re.findall(r'(\d{1,2})\s*:\s*(\d{2})', cells[0] or '')
                    if not times and not any(c and c.strip() for c in cells[1:]):
                        continue
                    if len(times) != 2:
                        raise ValueError('Unsupported schedule times')
                    start, end = [int(h)*60+int(m) for h,m in times]
                    if not 0 <= start < end < 1440 or (rows and start < rows[-1]['end_minutes']):
                        raise ValueError('Invalid schedule interval')
                    subjects = [' '.join(line.strip() for line in (cell or '').splitlines()
                                         if line.strip() and line == line.upper()) for cell in cells[1:]]
                    if not all(subjects):
                        raise ValueError('Unsupported subject cell')
                    rows.append({'start':f'{start//60:02}:{start%60:02}', 'end':f'{end//60:02}:{end%60:02}',
                                 'end_minutes':end, 'subjects':subjects})
                if not 3 <= len(rows) <= 16:
                    raise ValueError('Unsupported schedule length')
                return rows
    raise ValueError('No readable weekly table')


def activity_today(rows, today: date, activity):
    if today.weekday() >= 5:
        return False
    subjects = [normalized(row['subjects'][today.weekday()]) for row in rows]
    pattern = r'natacion|piscina' if activity == 'pool' else r'e\.?\s*fisica|educacion fisica|psicomotricidad'
    if any(re.search(pattern, subject) for subject in subjects):
        return True
    if any(re.search(r'\bef\s*/\s*nat\b', subject) for subject in subjects):
        return None
    return False


class ScheduleReader:
    """Refresh once per school day; retry failed reads on the next poll."""
    def __init__(self, hass, client, entry_id=None, profiles=None):
        self.hass, self.client = hass, client
        self.profiles = profiles
        self.cache = {}
        self.store = Store(hass, 1, f"casvi.schedules.{entry_id}") if entry_id else None
        self.loaded = False
        self.force = set()

    async def refresh(self, children):
        self.force.update(children)

    async def read(self, child, today):
        if not self.loaded:
            if self.store:
                self.cache = await self.store.async_load() or {}
            self.loaded = True
        try:
            return await self._read(child, today)
        except Exception:
            if child in self.cache:
                return self.cache[child]
            raise


    async def _read(self, child, today):
        cached = self.cache.get(child)
        if cached and cached['checked'] == today.isoformat() and child not in self.force:
            return cached
        profile = await self.profiles.read(child, today) if self.profiles else await self.client.child_profile(child)
        group = profile['group']
        document = next((d for d in group.get('documentos', []) if re.search(r'\bhorario\b', normalized(d.get('titulo')))), None)
        if document is None:
            raise ValueError('No group schedule')
        identity = f"{group['idGrupo']}:{document['id']}:{document.get('fechaModif', '')}:{today.year if today.month >= 9 else today.year-1}"
        if cached and cached.get('identity') == identity and child not in self.force:
            cached['checked'] = today.isoformat()
            if self.store:
                await self.store.async_save(self.cache)
            return cached
        pdf = await self.client.read_document(child, {'id':str(document['id']), 'kind':'documentoGrupo', 'group':str(group['idGrupo'])})
        rows = await self.hass.async_add_executor_job(parse_schedule, pdf)
        result = {'rows':rows, 'checked':today.isoformat(), 'document_id':str(document['id']), 'identity':identity}
        self.cache[child] = result
        if self.store:
            await self.store.async_save(self.cache)
        self.force.discard(child)
        return result
