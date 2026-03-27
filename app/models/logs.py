import os
import re
from urllib.parse import quote as urlquote
from datetime import datetime
from markupsafe import Markup


def list_chatrooms(logs_path):
    """List all chatroom directories"""
    try:
        return sorted(
            d for d in os.listdir(logs_path)
            if os.path.isdir(os.path.join(logs_path, d))
        )
    except FileNotFoundError:
        return []


def parse_log_file(filepath):
    """Parse a log file and yield entries"""
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            parts = line.strip().split('\t', 2)
            if len(parts) >= 2:
                datetimestring = parts[0]
                user = parts[1]
                message = parts[2] if len(parts) > 2 else ""
                try:
                    datetimeobject = datetime.strptime(
                        datetimestring, r'%Y-%m-%dT%H:%M:%S.%f%z')
                    yield {
                        'line_number': i + 1,
                        'datetime': datetimeobject,
                        'time': datetimeobject.strftime(r'%H:%M:%S'),
                        'user': user,
                        'message': message
                    }
                except ValueError:
                    pass  # Skip malformed entries


class MessageLink:
    link: str

    def __init__(self, link: str):
        self.link = link

    def get_link_quotes(self):
        link = self.link

        # Either http:// or https:// is passed in
        delimiter_index = link.find(
            "/", 8 if link.startswith("https://") else 7)
        part_to_be_quoted = link[delimiter_index:]

        return link[:delimiter_index] + urlquote(part_to_be_quoted)

    def __html__(self):
        link_quoted_escaped = Markup.escape(self.get_link_quotes())
        link_display_escaped = Markup.escape(self.link)
        return f"<a rel=\"nofollow\" href=\"{link_quoted_escaped}\">{link_display_escaped}</a>"


PARSE_MESSAGE_URL_REGEX = re.compile(r"(https?://[^\s'\";]*[^\s'\";,\.])")


def parse_message(message_text: str, search_key: str = None):
    # Find all links, according to Luanti's method
    messages_split = re.split(PARSE_MESSAGE_URL_REGEX, message_text)
    message_text = ""
    for part in messages_split:
        if part.startswith("https://") or part.startswith("http://"):
            message_text += Markup(MessageLink(part))
        else:
            message_text += Markup.escape(part)
    return message_text
