"""WebSocket接続管理"""

import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        """初期化"""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """新しいWebSocket接続を追加"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"新しいWebSocket接続が登録されました。総数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """指定WebSocket接続を削除"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket接続が切断されました。総数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """特定のクライアントにメッセージを送信"""
        try:
            await websocket.send_text(message)
        except Exception:
            # 接続が切断されている場合は削除
            self.disconnect(websocket)

    async def broadcast(self, message: str, exclude_websocket: WebSocket | None = None):
        """
        全ての接続中のクライアントにメッセージをブロードキャスト

        接続状態の管理:
        1. 接続リストのコピーを作成して、イテレート中の変更を防ぐ
        2. 各接続の状態を事前にチェックし、切断済みの接続をマーク
        3. メッセージ送信に失敗した接続もマーク
        4. 最後に切断された接続をリストから削除

        この方式により、ネットワーク障害や予期しない切断に対して
        堅牢な接続管理を実現している
        """
        connections_to_remove = []
        for connection in self.active_connections.copy():  # リストのコピーを作成して安全にイテレート
            try:
                # 除外対象のWebSocketをスキップ
                if exclude_websocket and connection == exclude_websocket:
                    continue

                # WebSocket接続状態を厳密にチェック
                # client_stateがDISCONNECTEDの場合は既に切断済み
                if connection.client_state.name == "DISCONNECTED":
                    connections_to_remove.append(connection)
                    continue
                # メッセージ送信を試行
                await connection.send_text(message)
            except Exception:
                # 送信に失敗した場合は接続が切断されているとみなす
                connections_to_remove.append(connection)

        # 切断された接続をアクティブリストから削除
        for conn in connections_to_remove:
            self.disconnect(conn)


manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """ConnectionManagerのインスタンスを取得（テスト用）"""
    return manager
