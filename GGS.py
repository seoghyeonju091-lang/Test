import re
import requests
import pandas as pd
import streamlit as st

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="경기도 학교 분포",
    page_icon="🏫",
    layout="wide",
)

NEIS_URL = "https://open.neis.go.kr/hub/schoolInfo"
ATPT_OFCDC_SC_CODE = "J10"  # 경기도교육청


# =========================================================
# NEIS API
# =========================================================

@st.cache_data(ttl=60 * 60)
def get_schools(api_key: str) -> pd.DataFrame:
    """
    NEIS 학교기본정보 API에서 경기도 학교 전체를 가져온다.
    """

    all_rows = []
    page = 1
    page_size = 1000

    while True:
        params = {
            "KEY": api_key,
            "Type": "json",
            "pIndex": page,
            "pSize": page_size,
            "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        }

        response = requests.get(
            NEIS_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        # API 응답에서 schoolInfo 찾기
        if "schoolInfo" not in data:
            break

        school_info = data["schoolInfo"]

        if len(school_info) < 2:
            break

        rows = school_info[1].get("row", [])

        if not rows:
            break

        all_rows.extend(rows)

        # 마지막 페이지
        if len(rows) < page_size:
            break

        page += 1

        # 혹시 모를 무한 요청 방지
        if page > 100:
            break

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)

    return df


# =========================================================
# 데이터 전처리
# =========================================================

def extract_city(address: str) -> str:
    """
    도로명 주소에서 경기도 시/군 단위를 추출한다.
    예:
    경기도 수원시 영통구 ...
    -> 수원시

    경기도 양평군 ...
    -> 양평군
    """

    if pd.isna(address):
        return "미상"

    address = str(address)

    # 경기도 + 시
    match = re.search(
        r"경기도\s+([가-힣]+시)",
        address
    )

    if match:
        return match.group(1)

    # 경기도 + 군
    match = re.search(
        r"경기도\s+([가-힣]+군)",
        address
    )

    if match:
        return match.group(1)

    return "미상"


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # 필요한 컬럼이 없더라도 오류가 나지 않도록 처리
    for col in [
        "SCHUL_NM",
        "SCHUL_KND_SC_NM",
        "ORG_RDNMA",
        "ORG_RDNZC",
        "SD_SCHUL_CODE",
        "FOND_SC_NM",
        "HMPG_ADRES",
        "ORG_TELNO",
        "HS_SC_NM",
    ]:
        if col not in df.columns:
            df[col] = ""

    df["시군"] = df["ORG_RDNMA"].apply(extract_city)

    return df


# =========================================================
# 학교 유형 색상용 분류
# =========================================================

def normalize_school_type(value):
    if pd.isna(value):
        return "기타"

    value = str(value)

    if "유치원" in value:
        return "유치원"
    if "초등학교" in value:
        return "초등학교"
    if "중학교" in value:
        return "중학교"
    if "고등학교" in value:
        return "고등학교"
    if "특수학교" in value:
        return "특수학교"

    return value


# =========================================================
# 화면
# =========================================================

st.title("🏫 경기도 학교 분포 정보")
st.caption("NEIS 학교기본정보 API · 경기도교육청 표준코드 J10")

# ---------------------------------------------------------
# API KEY
# ---------------------------------------------------------

try:
    API_KEY = st.secrets["NEIS_API_KEY"]
except Exception:
    API_KEY = ""

if not API_KEY:
    st.error(
        "NEIS API 인증키가 설정되지 않았습니다. "
        "Streamlit Secrets에 NEIS_API_KEY를 등록하세요."
    )

    st.code(
        """
NEIS_API_KEY = "발급받은_NEIS_API_KEY"
""",
        language="toml",
    )

    st.stop()


# ---------------------------------------------------------
# 데이터 가져오기
# ---------------------------------------------------------

with st.spinner("NEIS에서 경기도 학교 정보를 가져오는 중입니다..."):
    try:
        schools = get_schools(API_KEY)
        schools = prepare_dataframe(schools)
    except Exception as e:
        st.error(f"NEIS API 호출 중 오류가 발생했습니다: {e}")
        st.stop()


if schools.empty:
    st.warning("조회된 학교 데이터가 없습니다.")
    st.stop()


# ---------------------------------------------------------
# 사이드바
# ---------------------------------------------------------

st.sidebar.header("🔎 검색 조건")

school_types = sorted(
    schools["SCHUL_KND_SC_NM"]
    .dropna()
    .astype(str)
    .unique()
)

selected_types = st.sidebar.multiselect(
    "학교 유형",
    options=school_types,
    default=school_types,
)

cities = sorted(
    schools["시군"]
    .dropna()
    .astype(str)
    .unique()
)

selected_cities = st.sidebar.multiselect(
    "시·군",
    options=cities,
    default=[],
)

keyword = st.sidebar.text_input(
    "학교명 검색",
    placeholder="예: 수원, 경기고..."
)


# ---------------------------------------------------------
# 필터링
# ---------------------------------------------------------

filtered = schools.copy()

if selected_types:
    filtered = filtered[
        filtered["SCHUL_KND_SC_NM"].isin(selected_types)
    ]

if selected_cities:
    filtered = filtered[
        filtered["시군"].isin(selected_cities)
    ]

if keyword.strip():
    keyword = keyword.strip()

    filtered = filtered[
        filtered["SCHUL_NM"]
        .astype(str)
        .str.contains(keyword, case=False, na=False)
    ]


# =========================================================
# KPI
# =========================================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "경기도 전체 학교",
    f"{len(schools):,}개"
)

col2.metric(
    "현재 검색 결과",
    f"{len(filtered):,}개"
)

col3.metric(
    "시·군",
    f"{schools['시군'].nunique():,}곳"
)


st.divider()


# =========================================================
# 탭
# =========================================================

tab1, tab2, tab3 = st.tabs(
    ["📊 지역별 분포", "🏫 학교 목록", "🗺️ 지도"]
)


# =========================================================
# TAB 1
# =========================================================

with tab1:

    st.subheader("시·군별 학교 수")

    city_count = (
        filtered
        .groupby("시군")
        .size()
        .sort_values(ascending=False)
        .rename("학교 수")
        .to_frame()
    )

    st.bar_chart(city_count)

    st.subheader("학교 유형별 분포")

    type_count = (
        filtered
        .groupby("SCHUL_KND_SC_NM")
        .size()
        .sort_values(ascending=False)
        .rename("학교 수")
        .to_frame()
    )

    st.bar_chart(type_count)

    st.subheader("시·군 × 학교 유형")

    cross_table = pd.crosstab(
        filtered["시군"],
        filtered["SCHUL_KND_SC_NM"],
    )

    st.dataframe(
        cross_table,
        use_container_width=True,
    )


# =========================================================
# TAB 2
# =========================================================

with tab2:

    st.subheader(
        f"검색된 학교 {len(filtered):,}개"
    )

    display_columns = [
        "SCHUL_NM",
        "SCHUL_KND_SC_NM",
        "시군",
        "ORG_RDNMA",
        "ORG_TELNO",
        "HMPG_ADRES",
        "SD_SCHUL_CODE",
    ]

    display_columns = [
        col for col in display_columns
        if col in filtered.columns
    ]

    result = filtered[display_columns].copy()

    result = result.rename(
        columns={
            "SCHUL_NM": "학교명",
            "SCHUL_KND_SC_NM": "학교종류",
            "시군": "시·군",
            "ORG_RDNMA": "주소",
            "ORG_TELNO": "전화번호",
            "HMPG_ADRES": "홈페이지",
            "SD_SCHUL_CODE": "학교코드",
        }
    )

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True,
    )

    # CSV 다운로드
    csv = result.to_csv(
        index=False,
        encoding="utf-8-sig",
    )

    st.download_button(
        label="📥 검색 결과 CSV 다운로드",
        data=csv,
        file_name="gyeonggi_schools.csv",
        mime="text/csv",
    )


# =========================================================
# TAB 3
# =========================================================

with tab3:

    st.subheader("학교 위치")

    # NEIS 학교기본정보의 위도/경도 컬럼을 이용
    latitude_candidates = [
        "LAT",
        "LATITUDE",
        "LATITUDE_VALUE",
    ]

    longitude_candidates = [
        "LNG",
        "LONGITUDE",
        "LONGITUDE_VALUE",
    ]

    lat_col = next(
        (
            col for col in latitude_candidates
            if col in filtered.columns
        ),
        None,
    )

    lon_col = next(
        (
            col for col in longitude_candidates
            if col in filtered.columns
        ),
        None,
    )

    if lat_col and lon_col:

        map_df = filtered[
            [lat_col, lon_col]
        ].copy()

        map_df[lat_col] = pd.to_numeric(
            map_df[lat_col],
            errors="coerce",
        )

        map_df[lon_col] = pd.to_numeric(
            map_df[lon_col],
            errors="coerce",
        )

        map_df = map_df.dropna()

        map_df = map_df.rename(
            columns={
                lat_col: "lat",
                lon_col: "lon",
            }
        )

        st.map(map_df)

    else:
        st.info(
            "현재 NEIS 응답에 지도 좌표 컬럼이 없어 "
            "지도 표시를 생략했습니다."
        )

        st.write(
            "주소 기반 지도 표시가 필요하다면 "
            "주소 → 좌표 변환 API를 추가할 수 있습니다."
        )


# =========================================================
# 데이터 정보
# =========================================================

st.divider()

st.caption(
    f"데이터 출처: 교육부/나이스 교육정보 개방 포털 · "
    f"교육청 코드: {ATPT_OFCDC_SC_CODE} · "
    f"조회 학교 수: {len(schools):,}개"
)
