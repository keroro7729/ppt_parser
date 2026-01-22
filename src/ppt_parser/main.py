from ppt_parser.loader import load_pptx
from pathlib import Path
import json
import pandas as pd
from ppt_parser.ollama_client import OllamaClient


# base path 경로 수정해서 사용
BASE_DIR = Path(__file__).resolve().parents[2] / "sample"

def parse_ppt(file_name: str) :
    path = BASE_DIR / file_name
    rows = load_pptx(path)
    df = pd.DataFrame(rows)

    columns = ["shape_type", "text", "table"]
    client = OllamaClient(model="llama3.1")

    for i in range(0, 6):
        slide_index = i
        slide_data = df[df["slide_index"] == slide_index]

        slide_json = slide_df_to_json(slide_index, slide_data)

        json_str = json.dumps(
            slide_json,
            ensure_ascii=False,
            indent=2,
        )

        response = client.generate(
            system="너는 PPT 슬라이드 구조를 이해하고 요약하는 AI야.",
            prompt=(
                "다음은 PPT 한 장의 구조 데이터야.\n"
                "의미를 해석해서 핵심 내용만 요약해줘.\n\n"
                f"{json_str}"
            ),
        )

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

if __name__ == "__main__":
    sample_file = "To_Be_MM_1.1.1.pptx"
    print("start parsing " + sample_file)
    result = parse_ppt(sample_file)
    print("result: " + result)