import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="아파트 현장 통합 생산성 분석 툴", page_icon="🏗️", layout="wide")

st.title("🏗️ 아파트 건설현장 스마트 생산성 분석 툴")
st.markdown("건축, 토목, 전기, 기계 공종의 일일 투입 자원과 실적을 기록하고 생산성을 모니터링합니다.")

if 'df_logs' not in st.session_state:
    st.session_state.df_logs = pd.DataFrame(columns=[
        "날짜", "공종", "동/구역", "세부 작업명", "계획 물량", "실제 물량", "투입 공수(MD)", "장비 대기시간(h)"
    ])

with st.form("productivity_form"):
    st.subheader("📝 일일 작업 실적 입력")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        work_date = st.date_input("작업 일자", datetime.date.today())
        major_trade = st.selectbox("주력 공종", ["건축공사", "토목공사", "전기공사", "기계공사"])
    with col2:
        zone = st.text_input("동 / 구역 명", placeholder="예: 101동 지상 3층")
        detail_task = st.text_input("세부 작업명", placeholder="예: 케이블 포설 / 거푸집 설치")
    with col3:
        target_qty = st.number_input("계획 물량", min_value=0.0, value=50.0)
        actual_qty = st.number_input("실제 시공 물량", min_value=0.0, value=45.0)

    col4, col5 = st.columns(2)
    with col4:
        man_power = st.number_input("투입 공수 (Man-Day)", min_value=1.0, value=10.0)
    with col5:
        equip_delay = st.number_input("장비 대기/고장 시간 (시간)", min_value=0.0, value=0.0)
        
    submitted = st.form_submit_button("데이터 등록 및 분석 반영")
    
    if submitted:
        new_data = pd.DataFrame({
            "날짜": [work_date],
            "공종": [major_trade],
            "동/구역": [zone],
            "세부 작업명": [detail_task],
            "계획 물량": [target_qty],
            "실제 물량": [actual_qty],
            "투입 공수(MD)": [man_power],
            "장비 대기시간(h)": [equip_delay]
        })
        st.session_state.df_logs = pd.concat([st.session_state.df_logs, new_data], ignore_index=True)
        st.success("데이터가 성공적으로 기록되었습니다!")

st.divider()
st.subheader("📊 현장 종합 생산성 대시보드")

if not st.session_state.df_logs.empty:
    df = st.session_state.df_logs.copy()
    df["목표 달성률(%)"] = (df["실제 물량"] / df["계획 물량"]) * 100
    df["1인당 생산성"] = df["실제 물량"] / df["투입 공수(MD)"]
    
    total_target = df["계획 물량"].sum()
    total_actual = df["실제 물량"].sum()
    avg_achievement = (total_actual / total_target * 100) if total_target > 0 else 0
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("누적 계획 대비 달성률", f"{avg_achievement:.1f}%")
    kpi2.metric("총 투입 공수", f"{df['투입 공수(MD)'].sum():,.1f} MD")
    kpi3.metric("총 장비 대기 손실", f"{df['장비 대기시간(h)'].sum():,.1f} 시간")
    
    st.markdown("### 📋 전체 입력 데이터")
    st.dataframe(df, use_container_width=True)
    
    st.markdown("### 🔍 공종별 효율성 비교")
    trade_summary = df.groupby("공종")[["계획 물량", "실제 물량", "투입 공수(MD)", "장비 대기시간(h)"]].sum()
    trade_summary["공종별 달성률(%)"] = (trade_summary["실제 물량"] / trade_summary["계획 물량"]) * 100
    trade_summary["공종별 1인당 생산성"] = trade_summary["실제 물량"] / trade_summary["투입 공수(MD)"]
    st.dataframe(trade_summary, use_container_width=True)
else:
    st.info("💡 위 폼을 통해 첫 번째 작업 일일 실적을 입력해보세요.")
