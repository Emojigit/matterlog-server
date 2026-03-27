from flask import Blueprint, render_template, request, current_app
import os
from app.models.logs import list_chatrooms

bp = Blueprint('main', __name__)


@bp.route("/")
def index():
    """List all chatrooms"""
    chatrooms = list_chatrooms(current_app.config.get('LOGS_PATH', './logs'))
    return render_template('index.html', chatrooms=chatrooms)


@bp.route("/chat/<chatroom>/")
def chatroom_index(chatroom):
    """Index of log dates for a chatroom"""
    logs_path = current_app.config.get('LOGS_PATH', './logs')
    logs_base_url = current_app.config.get('LOGS_BASE_URL', '')
    chatroom_dir = os.path.join(logs_path, chatroom)

    if not os.path.isdir(chatroom_dir):
        return render_template('error.html', message="Chatroom not found"), 404

    # Get year/month directories
    years_months = []
    if os.path.isdir(chatroom_dir):
        for year_dir in sorted(
                (d for d in os.listdir(chatroom_dir)
                 if os.path.isdir(os.path.join(chatroom_dir, d))),
                reverse=True
        ):
            months = []
            for month_dir in sorted(
                    (d for d in os.listdir(os.path.join(chatroom_dir, year_dir))
                     if os.path.isdir(os.path.join(chatroom_dir, year_dir, d))),
                    reverse=True
            ):
                days = []
                for day_file in sorted(
                        f for f in os.listdir(os.path.join(chatroom_dir, year_dir, month_dir))
                        if os.path.isfile(os.path.join(chatroom_dir, year_dir, month_dir, f))
                        and f.endswith(".txt")
                ):
                    days.append(day_file[:-4])
                months.append((month_dir, days))
            years_months.append((year_dir, months))

    return render_template(
        'chatroom.html',
        chatroom=chatroom,
        years_months=years_months,
        logs_base_url=logs_base_url
    )
