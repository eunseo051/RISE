import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =========================
# 데이터 로드
# =========================
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results_path = os.path.join(base_path, "results.csv")

df = pd.read_csv(results_path, encoding="utf-8-sig")

st.title("📊 ESG 기반 AI 투자지원 대시보드")
st.markdown("Demo version - made by B.B.BIC")
st.write("")

# =========================
# 1) 사이드바 필터 (기업 선택)
# =========================
st.sidebar.header("⚙️ 필터")

company = st.sidebar.selectbox("기업 선택", df["company"].unique())
company_data = df[df["company"] == company].sort_values("year")
latest = company_data.iloc[-1]

# =========================
# 2) Top 5 ESG 기업
# =========================
st.subheader("🏆 Top 5 ESG 기업")
top5 = (
    df.groupby("company", as_index=False)["esg_avg"]
      .mean()
      .nlargest(5, "esg_avg")
)
st.bar_chart(top5.set_index("company")["esg_avg"])

# =========================
# 3) 기업 상세 정보
# =========================
st.subheader(f"📌 기업 정보 : {company}")

col1, col2 = st.columns(2)
if "market_cap" in df.columns:
    col1.metric("시가총액 (단위: 조원)", f"{latest['market_cap']}")
if "debt" in df.columns:
    col2.metric("부채비율 (%)", f"{latest['debt']}")

st.subheader(f"📊 {company} 연도별 재무 지표")
st.dataframe(company_data[["year", "market_cap", "debt"]])

col1, col2 = st.columns(2)
with col1:
    st.line_chart(company_data.set_index("year")["market_cap"], height=300)
    st.caption("시가총액 추이")
with col2:
    st.line_chart(company_data.set_index("year")["debt"], height=300)
    st.caption("부채비율 추이")

# =========================
# 4) ESG 세부 점수
# =========================
st.subheader("🌱 ESG 세부 점수")
col1, col2, col3 = st.columns(3)
col1.metric("환경 (E)", round(latest["esg_env"], 2))
col2.metric("사회 (S)", round(latest["esg_soc"], 2))
col3.metric("지배구조 (G)", round(latest["esg_gov"], 2))

st.line_chart(company_data.set_index("year")[["esg_env","esg_soc","esg_gov"]])
st.caption("연도별 ESG 세부 점수 추이")

# =========================
# 5) ESG 점수 & 주가 추이
# =========================
st.subheader(f"📈 {company} ESG & 주가 추이")
col1, col2 = st.columns(2)
with col1:
    esg_trend = company_data.groupby("year")["esg_last"].mean()
    st.line_chart(esg_trend)
    st.caption("ESG 점수 추이")
with col2:
    stock_trend = company_data.groupby("year")["stock_price"].mean()
    st.line_chart(stock_trend)
    st.caption("주가 추이")

# =========================
# 6) 감성 분석 결과
# =========================
st.subheader("📰 최근 ESG 뉴스 감성 분석")
if "sentiment_pos" in latest and "sentiment_neg" in latest:
    st.write(f"긍정 {latest['sentiment_pos']:.1f}% | 부정 {latest['sentiment_neg']:.1f}%")

# =========================
# 7) 그린워싱 탐지
# =========================
st.subheader("⚠️ 그린워싱 탐지 결과")
if "greenwash_flag" in latest:
    if latest["greenwash_flag"] == 1:
        st.error("⚠️ ESG 발표와 실제 뉴스가 불일치 → 그린워싱 의심")
    else:
        st.success("✅ ESG 발표와 실제 뉴스가 일치")

# =========================
# 8) 기업 비교 (Radar Chart)
# =========================
st.subheader("📊 기업 비교 (Radar)")

companies = df["company"].unique().tolist()
if len(companies) >= 2:
    cmpA = st.sidebar.selectbox("비교 기업 A", companies, index=0, key="cmpA")
    cmpB = st.sidebar.selectbox("비교 기업 B", companies, index=1, key="cmpB")

    cats = ["ESG 평균", "ESG 최신", "문서 수"]

    def stats(c):
        return [
            df[df["company"] == c]["esg_avg"].mean(),
            df[df["company"] == c]["esg_last"].mean(),
            df[df["company"] == c]["n_docs"].mean()
        ]

    valsA = stats(cmpA)
    valsB = stats(cmpB)
    df_radar = pd.DataFrame({"Category": cats, cmpA: valsA, cmpB: valsB})

    fig = px.line_polar(df_radar, r=cmpA, theta="Category", line_close=True)
    fig.update_traces(name=cmpA, showlegend=True)
    fig.add_scatterpolar(r=df_radar[cmpB], theta=df_radar["Category"],
                         name=cmpB, line=dict(shape="linear"))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("비교할 기업이 2개 이상일 때 레이다 차트를 표시합니다.")

# =========================
# 9) 추천 기업
# =========================
st.subheader("✅ 추천 기업")
col1, col2, col3 = st.columns(3)
top_companies = df.groupby("company")["esg_avg"].mean().nlargest(3).reset_index()

for i, col in enumerate([col1, col2, col3]):
    if i < len(top_companies):
        c = top_companies.iloc[i]
        reason = ""
        if "recommend_reason" in c:
            reason = c["recommend_reason"]
        else:
            # 간단한 자동 설명 예시
            reason = "ESG 상승 추세 & 안정적 재무 구조"
        with col:
            st.metric(c["company"], round(c["esg_avg"], 2), reason)

import streamlit as st
import pandas as pd
import os

# Plotly 임포트 → 설치 안 되어 있을 경우 대비
try:
    import plotly.express as px
except ImportError:
    st.warning("⚠️ Plotly 라이브러리가 설치되어 있지 않습니다. "
               "requirements.txt에 plotly를 추가하고 'pip install -r requirements.txt'로 설치하세요.")

# =========================
# 데이터 로드
# =========================
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results_path = os.path.join(base_path, "results.csv")

df = pd.read_csv(results_path, encoding="utf-8-sig")

# =========================
# ESG 세부 점수
# =========================
st.subheader("🌱 ESG 세부 점수")
st.dataframe(df[["year", "company", "esg_env", "esg_soc", "esg_gov"]].head())

company = st.sidebar.selectbox("기업 선택", df["company"].unique())
company_data = df[df["company"] == company].sort_values("year")
latest = company_data.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("환경 (E)", round(latest["esg_env"], 2))
col2.metric("사회 (S)", round(latest["esg_soc"], 2))
col3.metric("지배구조 (G)", round(latest["esg_gov"], 2))

# =========================
# 뉴스 감성분석
# =========================
st.subheader("📰 최근 ESG 뉴스 감성 분석")
if "sentiment_pos" in latest and "sentiment_neg" in latest:
    pos = latest["sentiment_pos"]
    neg = latest["sentiment_neg"]
    st.write(f"긍정 {pos:.1f}% | 부정 {neg:.1f}%")
else:
    st.info("뉴스 감성분석 데이터가 없습니다.")

# =========================
# 그린워싱 탐지
# =========================
st.subheader("⚠️ 그린워싱 탐지")
if "greenwash_flag" in latest:
    if latest["greenwash_flag"] == 1:
        st.error("⚠️ ESG 발표와 실제 뉴스 내용 불일치 (그린워싱 의심)")
    else:
        st.success("✅ ESG 발표와 실제 뉴스 내용 일치")
else:
    st.info("그린워싱 탐지 데이터가 없습니다.")

# =========================
# 추천 기업 근거
# =========================
st.subheader("✅ 추천 기업")
top_companies = (
    df.groupby("company")["esg_avg"].mean().nlargest(3).reset_index()
)

for _, row in top_companies.iterrows():
    reason = row["recommend_reason"] if "recommend_reason" in row else "ESG 상승 추세 & 안정적 재무 구조"
    st.metric(row["company"], round(row["esg_avg"], 2), reason)



