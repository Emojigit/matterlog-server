import os

from flask import Flask, Response
from markupsafe import escape as e

app = Flask(__name__)

if "MATTERLOGSERVER_PROXY_LEVEL" in os.environ:
    proxy_level = int(os.environ["MATTERLOGSERVER_PROXY_LEVEL"])
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=proxy_level, x_proto=proxy_level,
        x_host=proxy_level, x_prefix=proxy_level
    )

logs_path = os.environ.get("MATTERLOGSERVER_LOGS_PATH", "./logs")


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

    responce += """
    </ul>
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
    <ul>
    """

    for year_dir in sorted(
            d for d in os.listdir(chatroom_dir)
            if os.path.isdir(os.path.join(chatroom_dir, d))
    ):
        for month_dir in sorted(
                d for d in os.listdir(os.path.join(chatroom_dir, year_dir))
                if os.path.isdir(os.path.join(chatroom_dir, year_dir, d))
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
    responce += """
    </ul>
    <p><a href="../">Back to chatrooms list</a></p>
    <hr />
    <p>Logs collected by <a href="https://github.com/Emojigit/matterlog">Matterlog</a> | 
    Powered by <a href="https://github.com/Emojigit/matterlog-server">Matterlog Server</a>
    </p>
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
    <style>
    #chatlog {{
        width: 100%;
        border: 1px solid black;
        border-collapse: collapse;
    }}
    #chatlog tr td, #chatlog tr th {{
        width: max-content;
        border-bottom: 1px solid black;
        vertical-align: top;
        text-align: left;
    }}
    #chatlog tr td:not(:last-child), #chatlog tr th:not(:last-child) {{
        padding-right: 4px;
    }}
    #chatlog tr:target {{
        background-color: yellow;
    }}
    </style>
    </head>
    <body>
    <h1>Chat log for {e(chatroom)} on {e(year)}-{e(month)}-{e(day)}</h1>
    <table id="chatlog">
    <tr><th>#</th><th>Time</th><th>User</th><th>Message</th></tr>
    """

    with open(log_file_path, "r", encoding="utf-8") as log_file:
        for i, line in enumerate(log_file):
            time, user, message = line.strip().split("\t", 2)
            responce += f"<tr id=\"L{e(i + 1)}\">"
            responce += f"<td><a href=\"#L{e(i + 1)}\">{e(i + 1)}</td>"
            responce += f"<td>{e(time)}</td><td>{e(user)}</td><td>{e(message)}</td></tr>"

    responce += """
    </table>
    <p><a href="../../../">Back to chatroom index</a></p>
    <p><a href="../../../../">Back to chatrooms list</a></p>
    <hr />
    <p>Logs collected by <a href="https://github.com/Emojigit/matterlog">Matterlog</a> | 
    Powered by <a href="https://github.com/Emojigit/matterlog-server">Matterlog Server</a>
    </p>
    </body>
    </html>
    """

    return Response(responce, mimetype="text/html")
