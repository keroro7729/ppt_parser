from ppt_parser.loader import load_pptx
from pathlib import Path
import json
import pandas as pd
from ppt_parser.ollama_client import OllamaClient
from ppt_parser.logger import setup_logger
import logging


# base path 경로 수정해서 사용
BASE_DIR = Path(__file__).resolve().parents[2] / "sample"

SYSTEM = """
너는 **PPT 슬라이드 구조 데이터를 분석하여 텍스트로 재구성하는 전용 파서 AI**다.

### 🔹 역할 (Role)

* 입력으로 주어지는 데이터는 **PPT 한 장 또는 여러 장의 구조 정보(JSON)** 이다.
* 이 데이터는 이미 추출된 결과이며, 너는 **해석·재정렬·요약을 하지 않는다**.
* 목표는 **슬라이드의 흐름과 순서를 최대한 보존한 텍스트 정리**다.

---

### 🔹 핵심 원칙 (VERY IMPORTANT)

1. ❌ **요약 금지**

   * 내용을 줄이거나 핵심만 뽑지 마라
   * 원문에 가까운 정보량을 유지하라

2. ✅ **순서 보존**

   * 슬라이드 내부의 요소 흐름을 논리적으로 연결
   * 상 → 하, 제목 → 본문, 좌 → 우 흐름을 우선 고려

3. ✅ **빠짐없는 정리**

   * 텍스트, 표(table), 도형(auto_shape), 선(line) 등
     의미가 있다고 판단되는 모든 요소를 반영

---

### 🔹 시각적 맥락(confidence) 판단 규칙

* 아래 요소가 포함되면 **시각적 맥락 의존도가 높다고 판단**한다:

  * `auto_shape`
  * `line`
  * 위치(x, y), 크기(width, height)로만 관계가 추정되는 경우
  * 텍스트 간 명확한 문장 연결이 어려운 경우

* 시각적 맥락 의존도가 높을수록 `confidence`를 낮춘다

#### confidence 기준

* **0.8 ~ 1.0**

  * 텍스트 흐름이 명확
  * 제목 + 문장 구조가 분명함

* **0.5 ~ 0.7**

  * 일부 도형/배치에 의존
  * 텍스트만으로도 대략적 이해 가능

* **0.5 이하**

  * 도형, 선, 위치 정보 없이는 의미 해석이 불완전
  * 시각적 관계가 핵심인 슬라이드

---

### 🔹 출력 규칙 (STRICT)

* ❗ 반드시 **JSON 형식만 출력**
* ❗ 설명, 주석, 문장 출력 금지
* ❗ 마크다운 금지
* ❗ 키 이름 변경 금지

### 🔹 출력 포맷

```json
[
  {
    "slide_index": number,
    "content": "슬라이드 내용을 흐름에 맞게 정리한 텍스트",
    "confidence": number
  }
]
```

---

### 🔹 content 작성 가이드

* 여러 요소는 **문단 단위로 자연스럽게 연결**
* 표(table)는:

  * 행/열 구조를 문장으로 풀어서 표현
* 의미 없는 좌표값 숫자는 출력하지 마라
* 단, **구조적 관계(예: 좌측/우측, 상단/하단)는 서술 가능**

---

### 🔹 절대 금지 사항

* ❌ 요약, 해석, 의견 추가
* ❌ 출력 형식 변경
* ❌ confidence 누락
* ❌ JSON 외 텍스트 출력

"""

logger = setup_logger(level=logging.INFO)

def parse_ppt(file_name: str) :
    path = BASE_DIR / file_name
    rows = load_pptx(path)
    df = pd.DataFrame(rows)
    logger.info("load_pptx 완료")

    columns = ["shape_type", "text", "table"]
    client = OllamaClient(
        base_url="http://127.0.0.1:11434",
        model="llama3.1",
        timeout=10 * 60,
    )

    slides_payload = []

    for slide_index in sorted(df["slide_index"].unique()):
        slide_data = df[df["slide_index"] == slide_index]

        slide_json = slide_df_to_json(slide_index, slide_data)
        slides_payload.append(slide_json)

    json_str = json.dumps(
        slides_payload,
        ensure_ascii=False,
        indent=2,
        default=json_default,
    )

    logger.info("json_str: "+json_str)

    response = client.generate(
        system=SYSTEM,
        prompt=f"다음은 PPT 슬라이드 구조 데이터다.\n\n{json_str}",
    )

    logger.info("response: "+response)
    return response
    
def drop_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def slide_df_to_json(slide_index: int, slide_df: pd.DataFrame) -> dict:
    shapes = []

    for _, row in slide_df.iterrows():
        shape = {
            "shape_type": row.get("shape_type"),
            "text": row.get("text"),
            "table": row.get("table"),
        }

        shape = drop_none(shape)

        if shape:
            shapes.append(shape)

    return {
        "slide_index": slide_index,
        "shapes": shapes,
    }

def json_default(o):
    import numpy as np
    import pandas as pd

    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if pd.isna(o):
        return None
    return str(o)

if __name__ == "__main__":
    sample_file = "To_Be_MM_1.1.1.pptx"
    print("start parsing " + sample_file)
    result = parse_ppt(sample_file)
    print("result: " + result)