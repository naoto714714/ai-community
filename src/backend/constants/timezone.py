"""タイムゾーン定数定義."""

from datetime import timedelta, timezone

# タイムゾーン定数（将来的な拡張性を考慮）
JST = timezone(timedelta(hours=9))
