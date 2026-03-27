import os
import hashlib
from datetime import date, timedelta
from flask import Blueprint, render_template, request, current_app
from ..models import logs

bp = Blueprint('chat', __name__)


def get_logs_path():
    """Get logs path from app config"""
    return current_app.config.get('LOGS_PATH', './logs')


def check_day_exists(chatroom, year, month, day):
    """Check if a log file exists for a given day"""
    log_file_path = os.path.join(
        get_logs_path(), chatroom, year, month, f"{day}.txt")
    return os.path.isfile(log_file_path)


@bp.route("/chat/<chatroom>/<int:year>/<int(fixed_digits=2):month>/<int(fixed_digits=2):day>/")
def log_day(chatroom, year, month, day):
    """Display chat log for a specific day"""
    log_file_path = os.path.join(
        get_logs_path(), chatroom, f"{year:04d}", f"{month:02d}", f"{day:02d}.txt")

    if not os.path.isfile(log_file_path):
        return render_template('error.html', message="Log file not found"), 404

    this_day = date(year, month, day)
    prev_day = this_day - timedelta(days=1)
    next_day = this_day + timedelta(days=1)

    yesterday_exist = check_day_exists(
        chatroom,
        f"{prev_day.year:04d}",
        f"{prev_day.month:02d}",
        f"{prev_day.day:02d}"
    )
    tomorrow_exist = check_day_exists(
        chatroom,
        f"{next_day.year:04d}",
        f"{next_day.month:02d}",
        f"{next_day.day:02d}"
    )

    # Calculate ETag
    with open(log_file_path, "rb") as log_file:
        file_hash = hashlib.file_digest(log_file, "sha256")
        file_hash_digest = file_hash.hexdigest()
        etag = f'"{file_hash_digest}:{"Y" if yesterday_exist else ""}{"T" if tomorrow_exist else ""}"'
        if request.headers.get("If-None-Match") == etag:
            return render_template('notmodified.html'), 304

    # Parse log file
    entries = tuple(line for line in logs.parse_log_file(log_file_path))

    return render_template(
        'log_day.html',
        chatroom=chatroom,
        year=year,
        month=month,
        day=day,
        entries=entries,
        yesterday_exist=yesterday_exist,
        tomorrow_exist=tomorrow_exist,
        prev_day=prev_day,
        next_day=next_day
    )
