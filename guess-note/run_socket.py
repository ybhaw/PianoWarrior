from __future__ import annotations

import asyncio
import random
from time import sleep

import mido
import websockets

# Store connected clients
connected_clients = set()

note_mapping = {
    "c0": 60,
    "d0": 62,
    "e0": 64,
    "f0": 65,
    "g0": 67,
    "a1": 69,
    "b1": 71,
    "c1": 72,
    "d1": 74,
    "e1": 76,
    "f1": 77,
    "g1": 79,
    "a2": 81,
}


class MidoRunner:
    def __init__(self):
        self._random_note: str = self._get_random_note()
        self._in_port = None
        self._out_port = None
        self._client = None

    def wait_for_connection(self):
        while mido.get_input_names() == [] or mido.get_output_names() == []:
            print("Waiting for connecting MIDI devices...")
            sleep(1)
        self._out_port = mido.open_output(mido.get_output_names()[0])

    def _get_random_note(self) -> str:
        return random.choice(list(note_mapping.keys()))

    async def initialize_in_port(self, client):
        def _send_socket(note):
            if self.check_note(note):
                asyncio.run(self.send(self._random_note))

        self._client = client
        if self._in_port:
            self._in_port.close()

        self._in_port = mido.open_input(
            mido.get_input_names()[0], callback=_send_socket
        )
        print("Initialized input port")
        await self.send(self._random_note)
        print(f"Sent first note: {self._random_note}")

    async def send(self, note):
        await self._client.send(note)

    def check_note(self, note) -> bool:
        if note.type != "note_on":
            return
        if note.velocity == 0:
            return
        expected_note = note_mapping[self._random_note]
        if note.note != expected_note:
            self.be_attentive()
            print(f"Check failed for note {note.note} against {expected_note}")
            return False
        self._random_note = self._get_random_note()
        print(f"New random note: {self._random_note}")
        return True

    def be_attentive(self):
        self._out_port.send(mido.Message("note_on", note=96))
        sleep(0.2)
        self._out_port.send(mido.Message("note_on", note=96, velocity=0))
        asyncio.run(self.send("wrong"))


def get_mido_runner():
    runner = MidoRunner()
    runner.wait_for_connection()
    return runner


mido_runner: MidoRunner = get_mido_runner()


async def handle_client(websocket):
    # Add client to the set
    print(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    await mido_runner.initialize_in_port(websocket)

    try:
        # Keep the connection open
        while True:
            # Wait for any incoming messages (optional)
            # This example doesn't require client messages, but this keeps the connection alive
            message = await websocket.recv()
            print(f"Received message: {message}")
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    finally:
        # Remove client when disconnected
        connected_clients.remove(websocket)


async def main():
    # Start the WebSocket server
    server = await websockets.serve(handle_client, "localhost", 8080)
    print("WebSocket server started on ws://localhost:8080")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
