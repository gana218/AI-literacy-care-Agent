import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_TRACE_DIR = Path("reports/traces")


def save_local_trace(
    event_name: str,
    payload: Dict[str, Any],
    output: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    trace_dir: Path = DEFAULT_TRACE_DIR,
) -> Path:
    """
    LangSmith 미연결 환경에서 사용하는 로컬 JSON Trace 저장 함수.

    실제 LangSmith 클라우드 전송 대신
    입력, 출력, 오류 및 시각 정보를 JSON 파일로 기록한다.
    """

    trace_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(timezone.utc)
    timestamp_for_filename = timestamp.strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    trace_data = {
        "trace_provider": "local_json",
        "langsmith_enabled": False,
        "event_name": event_name,
        "timestamp": timestamp.isoformat(),
        "input": payload,
        "output": output,
        "error": error,
        "success": error is None,
        "note": (
            "실제 LangSmith가 아닌 로컬 JSON Trace입니다."
        ),
    }

    output_path = (
        trace_dir
        / f"{timestamp_for_filename}_{event_name}.json"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            trace_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return output_path