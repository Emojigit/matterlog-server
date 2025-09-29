import os
from datetime import datetime, date, timedelta

from flask import Flask, Response, request
from markupsafe import escape as e, Markup as M

app = Flask(__name__)

if "MATTERLOGSERVER_PROXY_LEVEL" in os.environ:
    proxy_level = int(os.environ["MATTERLOGSERVER_PROXY_LEVEL"])
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=proxy_level, x_proto=proxy_level,
        x_host=proxy_level, x_prefix=proxy_level
    )

logs_path = os.environ.get("MATTERLOGSERVER_LOGS_PATH", "./logs")
logs_base_url = os.environ.get("MATTERLOGSERVER_LOGS_BASE_URL", "")

common_footer = M("""<hr />
<footer>Logs collected by <a href="https://github.com/Emojigit/matterlog">Matterlog</a> | 
Powered by <a href="https://github.com/Emojigit/matterlog-server">Matterlog Server</a>
</footer>""")


def list_chatrooms():
    try:
        return sorted(
            d for d in os.listdir(logs_path)
            if os.path.isdir(os.path.join(logs_path, d))
        )
    except FileNotFoundError:
        return []


@app.route("/")
def index():
    responce = """
    <!DOCTYPE HTML>
    <html lang="en">
    <head>
    <title>List of chatrooms - Matterlog</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
    <h1>List of chatrooms</h1>
    <ul>
    """

    for chatroom in list_chatrooms():
        responce += f'<li><a href="/chat/{e(chatroom)}/">{e(chatroom)}</a></li>\n'

    responce += f"""
    </ul>
    {common_footer}
    </body>
    </html>
    """

    return Response(responce, mimetype="text/html")


@app.route("/chat/<chatroom>/")
def chatroom_index(chatroom):
    chatroom_dir = os.path.join(logs_path, chatroom)
    if not os.path.isdir(chatroom_dir):
        return Response("Chatroom not found", status=404, mimetype="text/plain")

    responce = f"""
    <!DOCTYPE HTML>
    <html lang="en">
    <head>
    <title>Chatroom {e(chatroom)} - Matterlog</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
    <h1>Chatroom {e(chatroom)}</h1>
    """
    if logs_base_url != "":
        responce += f'<p><a href="{e(logs_base_url)}/{e(chatroom)}/">Browse raw logs</a></p>'
    responce += "<ul>"

    for year_dir in sorted(
            (d for d in os.listdir(chatroom_dir)
             if os.path.isdir(os.path.join(chatroom_dir, d))),
            reverse=True
    ):
        for month_dir in sorted(
                (d for d in os.listdir(os.path.join(chatroom_dir, year_dir))
                 if os.path.isdir(os.path.join(chatroom_dir, year_dir, d))),
                reverse=True
        ):
            responce += f"<li>{e(year_dir)}-{e(month_dir)}: "
            for day_file in sorted(
                    f for f in os.listdir(os.path.join(chatroom_dir, year_dir, month_dir))
                    if os.path.isfile(os.path.join(chatroom_dir, year_dir, month_dir, f))
                    and f.endswith(".txt")
            ):
                day = day_file[:-4]
                responce += f'<a href="/chat/{e(chatroom)}/{e(year_dir)}/{e(month_dir)}/{e(day)}/">'
                responce += f"{e(day)}</a> "
            responce += "</li>\n"
    responce += f"""
    </ul>
    <form method="get" action="../../search/{e(chatroom)}/">
    <label for="q">Search in this chatroom:</label>
    <input type="text" id="q" name="q" required />
    <input type="submit" value="Search" />
    </form>
    <p><a href="../../">Back to chatrooms list</a></p>
    {common_footer}
    </body>
    </html>
    """

    return Response(responce, mimetype="text/html")


@app.route("/search/<chatroom>/")
def search_chatroom(chatroom):
    chatroom_dir = os.path.join(logs_path, chatroom)
    if not os.path.isdir(chatroom_dir):
        return Response("Chatroom not found", status=404, mimetype="text/plain")

    query = request.args.get("q", "").strip().lower()
    if query == "":
        return Response("No search query provided", status=400, mimetype="text/plain")

    results = []

    for year_dir in sorted(
            (d for d in os.listdir(chatroom_dir)
             if os.path.isdir(os.path.join(chatroom_dir, d))),
            reverse=True
    ):
        for month_dir in sorted(
                (d for d in os.listdir(os.path.join(chatroom_dir, year_dir))
                 if os.path.isdir(os.path.join(chatroom_dir, year_dir, d))),
            reverse=True
        ):
            for day_file in sorted(
                    f for f in os.listdir(os.path.join(chatroom_dir, year_dir, month_dir))
                    if os.path.isfile(os.path.join(chatroom_dir, year_dir, month_dir, f))
                    and f.endswith(".txt")
            ):
                day = day_file[:-4]
                log_file_path = os.path.join(
                    chatroom_dir, year_dir, month_dir, day_file)
                with open(log_file_path, "r", encoding="utf-8") as log_file:
                    for i, line in enumerate(log_file):
                        datetimestring, user, message = line.strip().split("\t", 2)
                        if query in message.lower():
                            datetimeobject = datetime.strptime(
                                datetimestring, r'%Y-%m-%dT%H:%M:%S.%f%z')
                            results.append(
                                (year_dir, month_dir, day, i + 1, datetimeobject, user, message))

    responce = f"""
    <!DOCTYPE HTML>
    <html lang="en">
    <head>
    <title>Search results for "{e(query)}" in {e(chatroom)} - Matterlog</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="../../static/style.css" />
    </head>
    <body>
    <h1>Search results for "{e(query)}" in {e(chatroom)}</h1>
    <p>{len(results)} result{"s" if len(results) != 1 else ""} found.</p>
    """

    if len(results) > 0:
        responce += """
        <table id="chatlog">
        <tr>
        <th>Date</th>
        <th>#</th>
        <th>time</th>
        <th>User</th>
        <th>Message</th>
        </tr>
        """
        for year, month, day, line_number, datetimeobject, user, message in reversed(results):
            display_message = ""
            message_pointer = 0
            while True:
                match_index = message.lower().find(query, message_pointer)
                if match_index == -1:
                    display_message += e(message[message_pointer:])
                    break
                display_message += e(message[message_pointer:match_index])
                display_message += M(
                    f"<mark>{e(message[match_index:match_index + len(query)])}</mark>")
                message_pointer = match_index + len(query)

            time = datetimeobject.strftime(r'%H:%M:%S')
            responce += "<tr>"
            responce += f"<td class=\"chatlog-date\">{e(year)}-{e(month)}-{e(day)}</td>"
            responce += f"<td class=\"chatlog-lineid\"><a href=\"/chat/{e(chatroom)}/{e(year)}/{e(month)}/{e(day)}/#L{e(line_number)}\">{e(line_number)}</a></td>"
            responce += f"<td class=\"chatlog-time\">{e(time)}</td>"
            responce += f"<td class=\"chatlog-user\">{e(user)}</td>"
            responce += f"<td class=\"chatlog-message\">{display_message}</td></tr>"
        responce += "</table>"

    responce += f"""
    <form method="get" action=".">
    <label for="q">Search in this chatroom:</label>
    <input type="text" id="q" name="q" value="{e(query)}" required />
    <input type="submit" value="Search" />
    </form>
    <p><a href="/chat/{e(chatroom)}/">Back to chatroom index</a></p>
    <p><a href="../../">Back to chatrooms list</a></p>
    {common_footer}
    </body>
    </html>
    """

    return Response(responce, mimetype="text/html")


@app.route("/chat/<chatroom>/<year>/<month>/<day>/")
def chat_log(chatroom, year, month, day):
    log_file_path = os.path.join(
        logs_path, chatroom, year, month, f"{day}.txt")
    if not os.path.isfile(log_file_path):
        return Response("Log file not found", status=404, mimetype="text/plain")

    responce = f"""
    <!DOCTYPE HTML>
    <html lang="en">
    <head>
    <title>Chat log for {e(chatroom)} on {e(year)}-{e(month)}-{e(day)} - Matterlog</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="../../../../../static/style.css" />
    </head>
    <body>
    <h1>Chat log for {e(chatroom)} on {e(year)}-{e(month)}-{e(day)}</h1>
    """

    if logs_base_url != "":
        responce += f'<p><a href="{e(logs_base_url)}/{e(chatroom)}/{e(year)}/{e(month)}/{e(day)}.txt">View raw logs</a></p>'

    responce += """
    <table id="chatlog">
    <tr><th>#</th><th>Time</th><th>User</th><th>Message</th></tr>
    """

    with open(log_file_path, "r", encoding="utf-8") as log_file:
        for i, line in enumerate(log_file):
            datetimestring, user, message = line.strip().split("\t", 2)
            datetimeobject = datetime.strptime(
                datetimestring, r'%Y-%m-%dT%H:%M:%S.%f%z')
            time = datetimeobject.strftime(r'%H:%M:%S')
            responce += f"<tr id=\"L{e(i + 1)}\">"
            responce += f"<td class=\"chatlog-lineid\"><a href=\"#L{e(i + 1)}\">{e(i + 1)}</td>"
            responce += f"<td class=\"chatlog-time\">{e(time)}</td>"
            responce += f"<td class=\"chatlog-user\">{e(user)}</td>"
            responce += f"<td class=\"chatlog-message\">{e(message)}</td></tr>"

    responce += "</table>"

    this_day = date(int(year), int(month), int(day))
    prev_day = this_day - timedelta(days=1)
    next_day = this_day + timedelta(days=1)

    if os.path.isfile(os.path.join(
            logs_path, chatroom,
            f"{prev_day.year:04d}", f"{prev_day.month:02d}", f"{prev_day.day:02d}.txt")):
        responce += f"""
        <p><a href="/chat/{e(chatroom)}/{prev_day.year:04d}/{prev_day.month:02d}/{prev_day.day:02d}/">
        &lt; Previous day ({e(prev_day)})</a></p>
        """

    if os.path.isfile(os.path.join(
            logs_path, chatroom,
            f"{next_day.year:04d}", f"{next_day.month:02d}", f"{next_day.day:02d}.txt")):
        responce += f"""
        <p><a href="/chat/{e(chatroom)}/{next_day.year:04d}/{next_day.month:02d}/{next_day.day:02d}/">
        Next day ({e(next_day)}) &gt;</a></p>
        """

    responce += f"""
    <p><a href="../../../">Back to chatroom index</a></p>
    <p><a href="../../../../../">Back to chatrooms list</a></p>
    {common_footer}
    </body>
    </html>
    """

    return Response(responce, mimetype="text/html")
