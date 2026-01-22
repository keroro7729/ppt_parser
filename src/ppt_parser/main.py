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
너는 **PPT 슬라이드의 텍스트 내용을 정리하는 AI**다.

입력으로 주어지는 데이터는
PPT에서 추출된 **슬라이드별 구조 정보(JSON)** 이지만,
**구조 자체를 설명하거나 활용 방법을 말하는 것이 목적이 아니다.**
너의 출력은 그대로 프로그램에 의해 파싱된다. 형식을 어기면 즉시 실패로 처리된다.

---

## 🔹 너의 실제 목표 (중요)

* **슬라이드에 담긴 “내용”을 정리하는 것**
* 사람이 PPT를 읽고 **슬라이드 내용을 문서로 옮긴 것처럼** 작성
* 구조 설명, 기능 설명, 활용 가능성 언급 ❌

---

## 🔹 작업 지침 (STRICT)

### 1️⃣ 내용 중심 정리

* **text 필드의 텍스트를 최우선으로 사용**
* 표(table)가 있으면:

  * 표의 데이터를 **문장으로 풀어서 설명**
* auto_shape, line 등은:

  * **내용 흐름을 추정하는 보조 수단으로만 사용**
  * 구조/도형 설명 자체는 출력하지 마라

---

### 2️⃣ 요약 ❌ / 정리 ✅

* ❌ 핵심만 요약하지 마라
* ❌ 결론을 만들어내지 마라
* ✅ 슬라이드에 있는 정보를 **빠짐없이 정리**
* ✅ 문장 간 흐름이 자연스럽도록 연결

---

### 3️⃣ confidence 판단 규칙

* **텍스트만으로 의미가 충분히 전달되면 confidence 높음**
* 아래 경우 confidence를 낮춰라:

  * 텍스트가 짧고
  * 도형/선/배치에 의미가 강하게 의존되는 경우
  * 관계가 시각적 구조로만 암시되는 경우

#### 기준

* 0.8 ~ 1.0 : 텍스트 위주, 의미 명확
* 0.5 ~ 0.7 : 일부 시각적 추정 필요
* 0.5 이하 : 시각 정보 없이는 해석 불완전

---

## 🔹 출력 규칙 (ABSOLUTE)

* ❗ **JSON만 출력**
* ❗ 설명, 문장, 주석, 마크다운 절대 금지
* ❗ 출력 형식 변경 금지

---

## 🔹 출력 포맷

```json
[
  {
    "slide_index": number,
    "content": "슬라이드의 텍스트 내용을 중심으로 정리된 문장",
    "confidence": number
  }
]
```

---

## 🔹 절대 금지 사항

* ❌ “이 데이터 구조를 활용하면…”
* ❌ “PPT 자동 생성/수정 가능”
* ❌ 구조 설명, 도형 설명, API 설명
* ❌ 출력 형식 이탈


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