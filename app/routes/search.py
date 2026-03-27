import os
import traceback
from flask import Blueprint, render_template, request, current_app

bp = Blueprint('search', __name__, url_prefix='/search')


def get_logs_path():
    """Get logs path from app config"""
    return current_app.config.get('LOGS_PATH', './logs')


@bp.route("/<chatroom>/")
def search_chatroom(chatroom):
    """Search messages in a chatroom"""
    logs_path = get_logs_path()
    chatroom_dir = os.path.join(logs_path, chatroom)

    if not os.path.isdir(chatroom_dir):
        return render_template('error.html', message="Chatroom not found"), 404

    query = request.args.get("q", "").strip()
    normalized_query = query.lower()

    if normalized_query == "":
        return render_template('error.html', message="No search query provided"), 400

    results = []
    error_files = []

    for year_dir in sorted(
            d for d in os.listdir(chatroom_dir)
            if os.path.isdir(os.path.join(chatroom_dir, d))
    ):
        for month_dir in sorted(
                d for d in os.listdir(os.path.join(chatroom_dir, year_dir))
                if os.path.isdir(os.path.join(chatroom_dir, year_dir, d))
        ):
            for day_file in sorted(
                    f for f in os.listdir(os.path.join(chatroom_dir, year_dir, month_dir))
                    if os.path.isfile(os.path.join(chatroom_dir, year_dir, month_dir, f))
                    and f.endswith(".txt")
            ):
                day = day_file[:-4]
                log_file_path = os.path.join(
                    chatroom_dir, year_dir, month_dir, day_file)

                try:
                    with open(log_file_path, "r", encoding="utf-8") as log_file:
                        for i, line in enumerate(log_file):
                            parts = line.strip().split("\t", 2)
                            if len(parts) >= 2:
                                datetimestring = parts[0]
                                user = parts[1]
                                message = parts[2] if len(parts) > 2 else ""
                                if normalized_query in message.lower():
                                    from datetime import datetime
                                    datetimeobject = datetime.strptime(
                                        datetimestring, r'%Y-%m-%dT%H:%M:%S.%f%z')
                                    results.append(
                                        (year_dir, month_dir, day, i + 1, datetimeobject, user, message))
                except Exception:
                    error_files.append(log_file_path)
                    print("Error in parsing log file", log_file_path, ":")
                    print(traceback.format_exc())

    # Highlight matching text in results
    highlighted_results = []
    for year, month, day, line_number, datetimeobject, user, message in results:
        display_message = ""
        message_pointer = 0
        while True:
            match_index = message.lower().find(normalized_query, message_pointer)
            if match_index == -1:
                display_message += message[message_pointer:]
                break
            display_message += message[message_pointer:match_index]
            display_message += f"<mark>{message[match_index:match_index + len(normalized_query)]}</mark>"
            message_pointer = match_index + len(normalized_query)

        time = datetimeobject.strftime(r'%H:%M:%S')
        highlighted_results.append({
            'year': year,
            'month': month,
            'day': day,
            'line_number': line_number,
            'time': time,
            'user': user,
            'message': display_message
        })

    return render_template(
        'search.html',
        chatroom=chatroom,
        query=query,
        results=highlighted_results,
        error_files=error_files
    )
