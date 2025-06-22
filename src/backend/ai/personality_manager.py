"""AI人格管理モジュール."""

import logging
import random
import threading
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AIPersonality:
    """AI人格データクラス."""

    file_name: str
    name: str
    prompt_content: str
    user_id: str


class PersonalityManager:
    """AI人格管理クラス."""

    def __init__(self, personalities_dir: Path | None = None):
        """
        初期化.

        Args:
            personalities_dir: 人格ファイルが格納されているディレクトリのパス
        """
        self.personalities_dir = personalities_dir or self._find_personalities_dir()
        self.personalities: dict[str, AIPersonality] = {}
        self._load_personalities()

    def _find_personalities_dir(self) -> Path:
        """人格ディレクトリを検索."""
        current = Path(__file__).parent
        while current != current.parent:
            people_dir = current / "prompts" / "people"
            if people_dir.exists():
                return people_dir
            current = current.parent

        raise FileNotFoundError("prompts/people ディレクトリが見つかりません")

    def _extract_name_from_filename(self, filename: str) -> str:
        """
        ファイル名から名前を抽出.

        例: "001_レン.md" -> "レン"
        """
        # .mdを削除し、_で分割して2番目の要素を取得
        name_part = filename.replace(".md", "")
        if "_" in name_part:
            return name_part.split("_", 1)[1]
        return name_part

    def _generate_user_id_from_filename(self, filename: str) -> str:
        """
        ファイル名からuser_idを生成.

        例: "001_レン.md" -> "ai_001"
        """
        # .mdを削除し、_で分割して1番目の要素（番号）を取得
        name_part = filename.replace(".md", "")
        if "_" in name_part:
            number_part = name_part.split("_", 1)[0]
            return f"ai_{number_part}"
        # フォールバック: ファイル名全体を使用
        return f"ai_{name_part}"

    def _load_personalities(self) -> None:
        """人格ファイルを読み込み."""
        if not self.personalities_dir.exists():
            logger.error(f"人格ディレクトリが存在しません: {self.personalities_dir}")
            return

        md_files = list(self.personalities_dir.glob("*.md"))
        logger.info(f"人格ファイル検出: {len(md_files)}件")

        for file_path in md_files:
            try:
                # ファイル名から名前を抽出
                name = self._extract_name_from_filename(file_path.name)
                user_id = self._generate_user_id_from_filename(file_path.name)

                # ファイル内容を読み込み
                with open(file_path, encoding="utf-8") as f:
                    prompt_content = f.read()

                personality = AIPersonality(
                    file_name=file_path.name, name=name, prompt_content=prompt_content, user_id=user_id
                )

                self.personalities[name] = personality
                logger.info(f"人格読み込み成功: {name} (file: {file_path.name}, user_id: {user_id})")

            except Exception as e:
                logger.error(f"人格ファイル読み込みエラー: {file_path.name} - {str(e)}")

    def get_random_personality(self) -> AIPersonality | None:
        """ランダムに人格を選択."""
        if not self.personalities:
            logger.warning("利用可能な人格がありません")
            return None

        selected_name = random.choice(list(self.personalities.keys()))
        personality = self.personalities[selected_name]
        logger.debug(f"ランダム人格選択: {personality.name}")
        return personality

    def get_personality_by_name(self, name: str) -> AIPersonality | None:
        """名前で人格を取得."""
        return self.personalities.get(name)

    def list_available_personalities(self) -> list[str]:
        """利用可能な人格名のリストを取得."""
        return list(self.personalities.keys())

    def reload_personalities(self) -> None:
        """人格を再読み込み."""
        self.personalities.clear()
        self._load_personalities()


# グローバルインスタンス
_personality_manager: PersonalityManager | None = None
_lock = threading.Lock()


def get_personality_manager() -> PersonalityManager:
    """PersonalityManagerのシングルトンインスタンスを取得."""
    global _personality_manager
    if _personality_manager is None:
        with _lock:
            # ダブルチェックロッキング
            if _personality_manager is None:
                _personality_manager = PersonalityManager()
    return _personality_manager
