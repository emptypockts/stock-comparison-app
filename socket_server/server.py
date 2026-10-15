from gevent import monkey
monkey.patch_all()

from app_constants import REDIS_SERVER_URI
from datetime import datetime
from flask_socketio import SocketIO, join_room
from flask import Flask, request
from eacsa_logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

app = Flask(__name__)
ws_server = SocketIO(
    app,
    cors_allowed_origins="*",
    message_queue=REDIS_SERVER_URI,
    async_mode="gevent",
)
name_space = "/ai"


@ws_server.on("connect", namespace=name_space)
def handle_connect(auth: dict | None) -> None:
    """
    Handles a new WebSocket client connection on the /ai namespace.

    Extracts the user_id from the auth payload and joins the client
    to their dedicated room (user:<user_id>). If no user_id is provided,
    the connection is accepted but the client is not assigned to any room.

    Args:
        auth (dict | None): Authentication payload sent by the client on connect.
            Expected to contain a 'user_id' key.
    """
    logger.info(f"Client connected to /ai — sid: {request.sid}")
    user_id = None
    if auth:
        user_id = auth.get("user_id")
    if not user_id:
        logger.warning(f"No user_id provided — sid: {request.sid} not joined to any room.")
        return

    room_name = f"user:{user_id}"
    join_room(room_name)
    logger.info(f"Joined sid: {request.sid} to room: {room_name}")


@ws_server.on("disconnect", namespace=name_space)
def handle_disconnect() -> None:
    """
    Handles a WebSocket client disconnection on the /ai namespace.

    Logs the disconnection event with a timestamp and the client's session id.
    """
    logger.info(f"Client disconnected at {datetime.now()} — sid: {request.sid}")


@ws_server.on("join_room", namespace=name_space)
def handle_join(data: dict | None) -> None:
    """
    Handles an explicit room join request from a connected client.

    Allows a client to join or re-join their user room after the initial
    connection, useful for reconnection flows.

    Args:
        data (dict | None): Payload from the client. Expected to contain
            a 'user_id' key used to derive the room name (user:<user_id>).
    """
    if not data:
        logger.warning(f"join_room called with no data — sid: {request.sid}")
        return

    user_id = data.get("user_id", "")
    room_name = f"user:{user_id}"
    join_room(room_name)
    logger.info(f"Socket sid: {request.sid} joined room: {room_name}")


def notify_user(user_id: str, event_name: str, name_space: str, payload: dict | None = None) -> None:
    """
    Emits a WebSocket event to a specific user's room.

    Used server-side to push notifications to a connected client
    identified by their user_id, regardless of which worker process
    handles the request.

    Args:
        user_id (str): The target user's identifier. Used to derive the
            room name as 'user:<user_id>'.
        event_name (str): The WebSocket event name to emit.
        name_space (str): The SocketIO namespace to emit on (e.g. '/ai').
        payload (dict | None): Optional data payload to send with the event.
            Defaults to an empty dict if not provided.
    """
    logger.info(f"Notifying user: {user_id} — event: {event_name}")
    room_name = f"user:{user_id}"
    ws_server.emit(
        event_name, payload or {}, room=room_name, namespace=name_space
    )


if __name__ == "__main__":
    port = "5009"
    logger.info(f"Starting WebSocket server on port {port}")
    ws_server.run(app, port=port, debug=True)
