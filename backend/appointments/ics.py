# backend/appointments/ics.py

"""
Calendar file — an appointment as an iCalendar file (.ics)
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Write one appointment as a calendar file that any agenda opens (Outlook,
Google Calendar, Apple Calendar): one event, its start and its end in UTC,
the offer and the other participant as its title, the place, the note,
and an identifier that stays the same, so that importing the file twice
updates the event instead of copying it (decisions of 22.10.2026). Written
by hand, the format being simple for one event: RFC 5545, lines ended by
CRLF, the characters , ; \\ and the line breaks escaped in a text, and every
line longer than 75 bytes folded (cut, the rest on the next line after a
space). Who may download which appointment is decided by the view.

What is not here
────────────────
A subscription (a feed the agenda reads again by itself): a file is a
copy, and a cancellation made afterwards does not reach it.
"""

from datetime import UTC

from django.utils import timezone

# Who wrote the file, as the format asks for
PRODUCT = "-//MarkeTech//Appointments//EN"
# The longest line, in bytes, before it is folded
WIDTH = 75


def text(value):
    """A text of the event, its special characters escaped."""
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def utc(moment):
    """20261026T080000Z: a time in UTC, as the format writes it."""
    return moment.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def fold(line):
    """The line cut every 75 bytes, never inside a character: the rest
    goes on lines that start with a space, which counts in their 75."""
    parts, current, size = [], "", 0
    for character in line:
        length = len(character.encode("utf-8"))
        limit = WIDTH if not parts else WIDTH - 1
        if size + length > limit:
            parts.append(current)
            current, size = "", 0
        current += character
        size += length
    parts.append(current)
    return "\r\n ".join(parts)


def to_ics(appointment, title, domain):
    """The calendar file of an appointment, as text: one event, titled
    title, its identifier made with the domain of the site."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PRODUCT}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:appointment-{appointment.pk}@{domain}",
        f"DTSTAMP:{utc(timezone.now())}",
        f"DTSTART:{utc(appointment.starts_at)}",
        f"DTEND:{utc(appointment.ends_at)}",
        f"SUMMARY:{text(title)}",
        f"LOCATION:{text(appointment.place)}",
    ]
    if appointment.note:
        lines.append(f"DESCRIPTION:{text(appointment.note)}")
    lines += ["END:VEVENT", "END:VCALENDAR"]
    return "".join(fold(line) + "\r\n" for line in lines)
