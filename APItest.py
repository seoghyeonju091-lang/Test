import json
import re

import streamlit as st
from openai import OpenAI


# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="AI 색 조합 생성기",
    page_icon="🎨",
    layout="centered",
)

st.title("🎨 AI 색 조합 생성기")
st.caption("원하는 분위기를 입력하면 AI가 어울리는 색 조합을 만들어줍니다.")


# -----------------------------
# OpenAI API
# -----------------------------
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error(
        "OPENAI_API_KEY가 설정되지 않았습니다. "
        "Streamlit Cloud의 Secrets에 API Key를 등록해주세요."
    )
    st.stop()

client = OpenAI(api_key=api_key)


# -----------------------------
# 입력 UI
# -----------------------------
with st.form("color_form"):
    mood = st.text_input(
        "원하는 분위기",
        placeholder="예: 따뜻하고 고급스러운 느낌",
    )

    color_count = st.slider(
        "색상 개수",
        min_value=3,
        max_value=8,
        value=5,
    )

    base_color = st.color_picker(
        "기준 색상 (선택)",
        "#4A90E2",
    )

    generate = st.form_submit_button(
        "🎨 색 조합 생성",
        use_container_width=True,
    )


# -----------------------------
# 색상 생성
# -----------------------------
if generate:
    if not mood.strip():
        st.warning("원하는 분위기를 입력해주세요.")
        st.stop()

    prompt = f"""
너는 전문 컬러 디자이너다.

사용자가 원하는 분위기:
{mood}

기준 색상:
{base_color}

필요한 색상 개수:
{color_count}

위 조건을 바탕으로 서로 조화로운 컬러 팔레트를 만들어라.

반드시 아래 JSON 형식으로만 답변하라.

{{
  "palette_name": "팔레트 이름",
  "description": "팔레트에 대한 짧은 설명",
  "colors": [
    {{
      "name": "색상 이름",
      "hex": "#000000",
      "role": "primary"
    }}
  ]
}}

규칙:
- colors에는 정확히 {color_count}개의 색상을 넣는다.
- hex 값은 반드시 #RRGGBB 형식이다.
- 실제 디자인에 사용할 수 있도록 색상 간 대비와 조화를 고려한다.
- role은 primary, secondary, accent, background, text 중 하나를 사용한다.
- JSON 이외의 설명은 출력하지 않는다.
"""

    try:
        with st.spinner("AI가 색 조합을 만들고 있습니다..."):
            response = client.responses.create(
                model="gpt-5.4-nano",
                input=prompt,
            )

        result_text = response.output_text.strip()

        # 혹시 ```json ... ``` 형태로 반환되는 경우 제거
        result_text = re.sub(
            r"^```json\s*|\s*```$",
            "",
            result_text,
            flags=re.IGNORECASE,
        ).strip()

        result = json.loads(result_text)

    except json.JSONDecodeError:
        st.error("AI가 올바른 JSON 형식으로 응답하지 않았습니다.")
        st.code(result_text if "result_text" in locals() else "")
        st.stop()

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        st.stop()


    # -----------------------------
    # 결과 출력
    # -----------------------------
    st.divider()

    st.subheader(f"🎨 {result['palette_name']}")
    st.write(result["description"])

    colors = result.get("colors", [])

    # 컬러 카드
    for color in colors:
        hex_code = color["hex"]

        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:16px;
                padding:14px;
                margin:8px 0;
                border-radius:12px;
                border:1px solid #ddd;
                background:#ffffff;
            ">
                <div style="
                    width:70px;
                    height:70px;
                    border-radius:10px;
                    background:{hex_code};
                    border:1px solid rgba(0,0,0,0.15);
                "></div>

                <div>
                    <div style="
                        font-size:18px;
                        font-weight:700;
                    ">
                        {color["name"]}
                    </div>

                    <div style="
                        font-family:monospace;
                        font-size:16px;
                        margin-top:4px;
                    ">
                        {hex_code}
                    </div>

                    <div style="
                        color:#666;
                        font-size:13px;
                        margin-top:4px;
                    ">
                        {color["role"]}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------
    # HEX 복사용 텍스트
    # -----------------------------
    st.subheader("📋 HEX 코드")

    hex_codes = "\n".join(
        color["hex"] for color in colors
    )

    st.code(hex_codes, language="text")

    # JSON 다운로드
    st.download_button(
        label="⬇️ 팔레트 JSON 다운로드",
        data=json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        ),
        file_name="color_palette.json",
        mime="application/json",
        use_container_width=True,
    )
