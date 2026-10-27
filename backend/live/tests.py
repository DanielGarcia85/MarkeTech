# backend/live/tests.py

"""
Live tests — the WebSocket and its signals
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the real time of the site from both ends. The WebSocket, through the
whole ASGI application as Daphne calls it: a logged-in user connects and
receives the signals of their group, never those of another; a visitor, a
blocked account and a page of another site are refused. Then the signals,
through the API as the pages use it: each event tells both people of the
application, once the change is saved; a reading tells only when it marks
messages read; a failure to send never breaks the action.

Why two kinds of test case
──────────────────────────
The WebSocket tests read the session and the account in another thread,
which sees only what is really written: they need TransactionTestCase.
They are coroutines, since a connection lives in one event loop. The
signal tests stay in TestCase, faster, and catch the signals in the
channel layer of the tests (in memory, dev.py) instead of a browser.
"""

import asyncio
import json
import shutil
import tempfile
from datetime import timedelta
from unittest import mock

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.utils import timezone

from accounts.models import User
from applications.models import JobApplication
from config.asgi import application as asgi_application
from offers.models import JobOffer
from profiles.models import CandidateProfile, EmployerProfile

from . import notify
from .consumers import group_of

PASSWORD = "Correct-horse-9"

# Files land here during the tests, never in the media folder of the project
MEDIA = tempfile.mkdtemp(prefix="marketech-tests-")

# The page that opens the WebSocket, as the browser says it (dev.py allows
# localhost)
ORIGIN = b"http://localhost:5173"


def session_cookie(user):
    """The session cookie of a logged-in user, as a browser would send it."""
    client = Client()
    client.force_login(user)
    return f"sessionid={client.cookies['sessionid'].value}".encode()


class WebSocketTests(TransactionTestCase):
    """Who may open the WebSocket, and what reaches it."""

    def setUp(self):
        self.user = User.objects.create_user(email="lea@example.com", password=PASSWORD)
        self.cookie = session_cookie(self.user)

    async def connect(self, cookie=b"", origin=ORIGIN):
        """Open the WebSocket through the whole application: the origin, the
        session, the route, the consumer. Returns the communicator and
        whether the connection was accepted."""
        headers = [(b"origin", origin)]
        if cookie:
            headers.append((b"cookie", cookie))
        communicator = WebsocketCommunicator(asgi_application, "/ws/", headers=headers)
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_a_logged_in_user_connects_and_receives_the_signals_of_their_group(self):
        communicator, connected = await self.connect(self.cookie)
        self.assertTrue(connected)
        layer = get_channel_layer()
        event = {"type": "news", "kind": "messages", "application": 12}
        # Another user's group: nothing arrives
        await layer.group_send(group_of(self.user.pk + 1), event)
        self.assertTrue(await communicator.receive_nothing())
        # Their own group: the kind and the application, nothing else
        await layer.group_send(group_of(self.user.pk), event)
        self.assertEqual(
            await communicator.receive_json_from(), {"type": "messages", "application": 12}
        )
        await communicator.disconnect()

    async def test_a_visitor_a_blocked_account_and_another_site_are_refused(self):
        # No session: a visitor
        _, connected = await self.connect()
        self.assertFalse(connected)
        # A page of another site, with a valid session: refused by the origin
        _, connected = await self.connect(self.cookie, origin=b"https://evil.example")
        self.assertFalse(connected)
        # The session of a blocked account: Django no longer counts it as
        # logged in
        await User.objects.filter(pk=self.user.pk).aupdate(is_active=False)
        _, connected = await self.connect(self.cookie)
        self.assertFalse(connected)


@override_settings(MEDIA_ROOT=MEDIA)
class SignalTests(TestCase):
    """The signals the views send, caught in the channel layer."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.candidate = User.objects.create_user(
            email="lea@example.com", password=PASSWORD, role="candidate"
        )
        self.employer = User.objects.create_user(
            email="marc@example.com", password=PASSWORD, role="employer"
        )
        profile = CandidateProfile.objects.create(user=self.candidate)
        company = EmployerProfile.objects.create(user=self.employer, company_name="Acme")
        offer = JobOffer.objects.create(
            employer=company,
            status="published",
            title="Python developer",
            description="Django and Vue.",
            city="Geneva",
            country="CH",
            contract="permanent",
        )
        cv = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 fake", content_type="application/pdf")
        self.application = JobApplication.objects.create(
            offer=offer, candidate=profile, cv=cv, status="in_progress"
        )
        # One channel listening to each group, as a tab of each would
        self.layer = get_channel_layer()
        self.tabs = {}
        for user in (self.candidate, self.employer):
            channel = async_to_sync(self.layer.new_channel)()
            async_to_sync(self.layer.group_add)(group_of(user.pk), channel)
            self.tabs[user.pk] = channel

    def tearDown(self):
        # The channel layer lives as long as the process: emptied for the
        # next test, whose accounts may have the same numbers
        async_to_sync(self.layer.flush)()

    # ── Helpers ───────────────────────────────────────────────────────

    def login(self, user):
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/_allauth/browser/v1/auth/session")
        client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
        return client

    def post(self, client, url, data):
        return client.post(url, data=json.dumps(data), content_type="application/json")

    def received(self, user):
        """The kinds the tab of a user received, in order, emptied."""
        kinds = []
        while True:
            # receive waits for a message: a short wait without one says
            # there is none left
            try:
                message = async_to_sync(asyncio.wait_for)(
                    self.layer.receive(self.tabs[user.pk]), timeout=0.1
                )
            except TimeoutError:
                return kinds
            self.assertEqual(message["application"], self.application.pk)
            kinds.append(message["kind"])

    def signalled(self, action):
        """Run the action, its transaction committed, and return the kinds
        each side received: (candidate, employer)."""
        with self.captureOnCommitCallbacks(execute=True):
            action()
        return self.received(self.candidate), self.received(self.employer)

    # ── The tests ─────────────────────────────────────────────────────

    def test_a_message_tells_both_sides_and_a_reading_only_when_it_marks(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        url = f"/api/applications/{self.application.pk}/messages/"
        sent = self.signalled(lambda: self.post(candidate, url, {"body": "Hello"}))
        self.assertEqual(sent, (["messages"], ["messages"]))
        # The employer reads: the message turns read, both are told
        self.assertEqual(self.signalled(lambda: employer.get(url)), (["messages"], ["messages"]))
        # Read again: nothing new turned read, no signal (no endless loop)
        self.assertEqual(self.signalled(lambda: employer.get(url)), ([], []))

    def test_a_move_tells_both_sides_and_a_second_time_with_a_message(self):
        client = self.login(self.employer)
        url = f"/api/applications/{self.application.pk}/status/"
        move = {"status": "accepted", "message": "Welcome"}
        sent = self.signalled(lambda: self.post(client, url, move))
        self.assertEqual(sent, (["applications", "messages"], ["applications", "messages"]))

    def test_an_appointment_proposed_tells_both_sides(self):
        client = self.login(self.employer)
        when = timezone.now() + timedelta(days=3)
        while timezone.localtime(when).weekday() >= 5:
            when += timedelta(days=1)
        url = f"/api/applications/{self.application.pk}/appointments/"
        data = {"starts_at": when.replace(microsecond=0).isoformat(), "place": "Online"}
        sent = self.signalled(lambda: self.post(client, url, data))
        self.assertEqual(sent, (["appointments"], ["appointments"]))

    def test_a_withdrawal_still_tells_once_the_application_is_gone(self):
        JobApplication.objects.filter(pk=self.application.pk).update(status="received")
        client = self.login(self.candidate)
        sent = self.signalled(lambda: client.delete(f"/api/applications/{self.application.pk}/"))
        self.assertEqual(sent, (["applications"], ["applications"]))
        self.assertFalse(JobApplication.objects.exists())

    def test_nothing_leaves_for_a_change_rolled_back(self):
        # Called, but the transaction is never committed
        notify.news(self.application, notify.MESSAGES)
        self.assertEqual((self.received(self.candidate), self.received(self.employer)), ([], []))

    def test_a_failure_to_send_never_breaks_the_action(self):
        client = self.login(self.candidate)
        url = f"/api/applications/{self.application.pk}/messages/"
        # A channel layer that cannot reach Redis
        broken = mock.Mock(group_send=mock.AsyncMock(side_effect=OSError("refused")))
        with (
            mock.patch("live.notify.get_channel_layer", return_value=broken),
            self.assertLogs("live.notify", level="WARNING") as logs,
        ):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.post(client, url, {"body": "Hello"})
        self.assertEqual(response.status_code, 201)
        # Both sides tried, each failure written with its account, no address
        self.assertEqual(len(logs.output), 2)
        expected = f"Live signal messages to user {self.candidate.pk} not sent (OSError)"
        self.assertIn(expected, logs.output[0])
        self.assertNotIn("example.com", "".join(logs.output))
