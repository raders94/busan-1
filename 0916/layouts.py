import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title='부산항만',
    page_icon='🎶',
    layout='wide',   #wide,centered
    initial_sidebar_state='expanded'  #locked,expanded
)

df_area = st.container(border=True)
with df_area:
    sales_df = pd.DataFrame({
        '지역':['서울', '서울', '부산', '부산', '대전', '대전'],
        '상품':['노트북','모니터','노트북','키보드','모니터','키보드'],
        '매출':[4_500_000,3_500_000,2_500_000,1_500_000,2_500_000,5_500_000,]
    })

st.dataframe(sales_df, hide_index=True)



with st.sidebar:
    st.sidebar.title('설정')
    st.sidebar.title('북항')
    st.write('북항 대시보드')
    st.sidebar.title('신항')
    st.write('신항 대시보드')
    selected_port =st.selectbox(
        label= '부두를 선택',
        options=['신항1부두', '신항2부두', '신항3부두']
    )
st.write(f'선택된 부두: {selected_port}')

st.header('조회조건')
region = st.selectbox(
    label='지역선택',
    options=['전체', '서울', '부산','대전'],
    )
if region== '전체':
    filtered=sales_df.copy()
    




st.title('스마트 항만 대시보드', )

data = pd.DataFrame({
    '상품': [
        '노트북','모니터','키보드','마우스'
    ],
    '판매량': [
        15,53,25,14
    ]
})

#st.dataframe(data)
#fig, ax
col1, col2 = st.columns(2)

with col1:

    st.write('왼쪽')
with col2:
    st.write('오른쪽')

sales_kpi, orders_kpi, cs_kpi = st.columns(3)

with sales_kpi:
    st.metric(
        label= '총 매출',
        value= '35000000원'
    )
with orders_kpi:
    st.metric(
        label= '주문수',
        value= '1250건'
    )
with cs_kpi:
    st.metric(
        label= '누적 고객수',
        value= '874명'
    )
left, right = st.columns([2,1])

with left:
    st.subheader('넓은 영역')
    st.write("상대적으로 넓게")

with right:
    st.subheader('좁은 영역')
    st.write("상대적으로 좁게")

st.write('컨테이너 밖')

container1 = st.container()

with container1:
    st.subheader('매출정보')
    st.write('총매출: 3500000원')
    st.write('1250건')

st.write('컨테이너 밖')


result_area=st.container(border=True)

result_area.subheader('분석결과')
result_area.metric(label='분석결과', value='평균매출: 1520건')

with st.expander('자세히 보기', expanded=True):
    st.subheader('평균 계산')
    st.write('super detailed description')


