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

st.title("📊 ESG 기업 분석 대시보드")
st.markdown("데모 버전 made by 비비빅")
st.write("")

# =========================
# 1) 사이드바 필터 (기업 선택)
# =========================
st.sidebar.header("⚙️ 필터")

company = st.sidebar.selectbox("기업 선택", df["company"].unique())
# 선택한 기업의 데이터
company_data = df[df["company"] == company].sort_values("year")
latest = company_data.iloc[-1]


# =========================
# 3) Top 5 ESG 기업
# =========================
st.subheader("🏆 Top 5 ESG 기업")
top5 = (
    df.groupby("company", as_index=False)["esg_avg"]
      .mean()
      .nlargest(5, "esg_avg")
)
st.bar_chart(top5.set_index("company")["esg_avg"])


# =========================
# 2) Company Details (본문)
# =========================
st.subheader(f"📌 기업 정보 : {company}")

if "market_cap" in df.columns:
    st.metric("시가총액 (단위: 조원)", f"{latest['market_cap']}")
if "debt" in df.columns:
    st.metric("부채비율 (%)", f"{latest['debt']}")

# 연도별 시가총액 & 부채비율
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
# 3) ESG 점수 & 주가 추이 (나란히)
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
# 4) Comparison (Radar Chart)
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
# 5) 추천 기업
# =========================
st.subheader("✅ 추천 기업")
col1, col2, col3 = st.columns(3)
top_companies = df.groupby("company")["esg_avg"].mean().nlargest(3).reset_index()

for i, col in enumerate([col1, col2, col3]):
    if i < len(top_companies):
        c = top_companies.iloc[i]
        with col:
            st.metric(c["company"], round(c["esg_avg"], 2), "ESG 평균 점수")
