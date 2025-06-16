import asyncio
import json
from datetime import datetime

import websockets


async def test_websocket():
    uri = "ws://localhost:8000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            # テストメッセージを送信
            test_message = {
                "type": "message:send",
                "data": {
                    "id": f"test_{int(datetime.now().timestamp())}",
                    "channel_id": "1",
                    "user_id": "user",
                    "user_name": "テストユーザー",
                    "content": "WebSocketテストメッセージ",
                    "timestamp": datetime.now().isoformat() + "Z",
                    "is_own_message": True,
                },
            }

            await websocket.send(json.dumps(test_message))
            print(f"Sent: {test_message}")

            # レスポンスを受信
            response = await websocket.recv()
            print(f"Received: {response}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
