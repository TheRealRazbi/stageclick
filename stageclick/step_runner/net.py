# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ["MessageReceiver", "create_send_message", "send_message", "start_server", "receive_message"]

import shlex
import socket
import threading
from typing import Callable, Optional, Any


class MessageReceiver:
    def __init__(
            self,
            port: int,
            command: str,
            process_result: Callable[[str], None],
            is_valid: Optional[Callable[[str], bool]] = None,
    ):
        self.port = port
        self.command = command
        self.process_result = process_result
        self.is_valid = is_valid or (lambda x: True)
        self.command_successful = False
        self._stop_server = None

    def _handle_message(self, message: str):
        try:
            parts = shlex.split(message)
            if len(parts) >= 2 and parts[0] == self.command:
                param = parts[1]
                if self.is_valid(param):
                    self.process_result(param)
                    self.command_successful = True
        except Exception as e:
            print(f"Error handling message '{message}': {e}")

    def __enter__(self):
        self._stop_server = start_server(self.port, self._handle_message)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._stop_server:
            self._stop_server()


def create_send_message(port: int):
    return lambda message: send_message(port, message)


def send_message(port: int, message: str):
    """Sends a message to another procedure.

    Might require tweaks if many messages are send as this restarts the connection each time
    """
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', port))
        client.sendall(message.encode())
        client.close()
    except ConnectionRefusedError:
        pass


def start_server(port: int, callback: Callable[[str], Optional[Any]]) -> Callable[[], None]:
    """Starts a threaded TCP server for local interprocess communication.

    Returns a stop function to shut down the server cleanly.
    """
    stop_event = threading.Event()

    def handle_client(conn: socket.socket):
        with conn:
            while not stop_event.is_set():
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    callback(data.decode())
                except Exception:
                    break  # Handle client disconnects gracefully

    def server_loop():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", port))
        server.listen()

        server.settimeout(1.0)  # Periodically check for stop_event
        while not stop_event.is_set():
            try:
                conn, _ = server.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn,), daemon=True)
                client_thread.start()
            except socket.timeout:
                continue
        server.close()

    thread = threading.Thread(target=server_loop, daemon=True)
    thread.start()

    # Return a function to stop the server
    def stop():
        stop_event.set()
        thread.join()

    return stop


def receive_message(
        port: int,
        command: str,
        process_result: Callable[[str], None],
        is_valid: Optional[Callable[[str], bool]] = None,
) -> MessageReceiver:
    """ Context manager to temporarily set a server and a command to listen to """
    return MessageReceiver(port, command, process_result, is_valid)
