# Copyright (c) PagerDuty.
# See LICENSE for details.
try:
    import ujson as json
except ImportError:
    import json

from .entity import Entity
from .log_entry import LogEntry
from .note import Note
from ..errors import MissingFromEmail


class Incident(Entity):
    logEntryFactory = LogEntry
    noteFactory = Note

    def resolve(self, from_email, resolution=None):
        """Resolve an incident using a valid email address."""

        if from_email is None or not isinstance(from_email, basestring):
            raise MissingFromEmail(from_email)

        endpoint = '/'.join((self.endpoint, self.id,))
        add_headers = {'from': from_email, }
        data = {
            'incident': {
                'type': 'incident',
                'status': 'resolved',
            }
        }

        if resolution is not None:
            data['resolution'] = resolution

        result = self.request('PUT',
                              endpoint=endpoint,
                              add_headers=add_headers,
                              data=data,)
        return result

    def acknowledge(self, from_email):
        """Resolve an incident using a valid email address."""
        endpoint = '/'.join((self.endpoint, self.id,))

        if from_email is None or not isinstance(from_email, basestring):
            raise MissingFromEmail(from_email)

        add_headers = {'from': from_email, }
        data = {
            'incident': {
                'type': 'incident',
                'status': 'acknowledged',
            }
        }

        result = self.request('PUT',
                              endpoint=endpoint,
                              add_headers=add_headers,
                              data=data,)
        return result

    def log_entries(self, time_zone='UTC', is_overview=False,
                    include=None, fetch_all=True):
        """Query for log entries on an incident instance."""
        endpoint = '/'.join((self.endpoint, self.id, 'log_entries'))

        query_params = {
            'time_zone': time_zone,
            'is_overview': json.dumps(is_overview),
        }

        if include:
            query_params['include'] = include

        result = self.logEntryFactory.find(
            endpoint=endpoint,
            api_key=self.api_key,
            fetch_all=fetch_all,
            **query_params
        )

        return result

    def update(self, *args, **kwargs):
        """Update this incident."""
        raise NotImplemented

    def notes(self):
        """Query for notes attached to this incident."""
        endpoint = '/'.join((self.endpoint, self.id, 'notes'))
        return self.noteFactory.find(
            endpoint=endpoint,
            api_key=self.api_key,
        )

    def create_note(self, from_email, content):
        """Create a note for this incident."""
        if from_email is None or not isinstance(from_email, basestring):
            raise MissingFromEmail(from_email)

        endpoint = '/'.join((self.endpoint, self.id, 'notes'))
        add_headers = {'from': from_email, }

        return self.noteFactory.create(
            endpoint=endpoint,
            api_key=self.api_key,
            add_headers=add_headers,
            data={'note': {'content': content}},
        )

    def snooze(self, from_email, duration):
        """Snooze this incident for `duration` seconds."""
        if from_email is None or not isinstance(from_email, basestring):
            raise MissingFromEmail(from_email)

        endpoint = '/'.join((self.endpoint, self.id, 'snooze'))
        add_headers = {'from': from_email, }

        return self.__class__.create(
            endpoint=endpoint,
            api_key=self.api_key,
            add_headers=add_headers,
            data={'duration': duration, },
        )
