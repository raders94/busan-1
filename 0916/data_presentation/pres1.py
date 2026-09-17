import streamlit as st
import pandas as pd
import numpy as np

data= pd.DataFrame({
    'num': range(1,51),
    'score': range(1,51),
    'price': range(1,51),
    'count': range(1,51),
    'export': range(1,51),
    'import': range(1,51),
    
})

display_df = data[
    ['count',
     'export',
     'import']
]



st.dataframe(display_df,
             height=300)

products = pd.DataFrame({
    '상품':[
        '노트북','모니터','키보드'
    ],
    '단가':[
        150_000_000,
        350_000,
        1_020_000
    ]
})

st.dataframe(
    products,
    column_config={
        '단가': st.column_config.NumberColumn(
            '단가(원)',
            format='%,d원'           #데이터 원본 유지, 보기만 변경
        )
    }
    )
achive_data= pd.DataFrame({
    '부서':[
        '영업팀',
        '개발팀',
        '마케팅팀'
    ],
    '달성률':[
        82,48,76
    ],


})
st.dataframe(achive_data, column_config={'달성률':st.column_config.NumberColumn(label='목표달성률', format='%d%%'
)})



progress_data= pd.DataFrame({
    '기술명':[
        'python',
        'java',
        '[php]'
    ],
    '진행률':[
        82,48,76
    ],})

st.dataframe(progress_data, column_config={
    '진행률':st.column_config.ProgressColumn(
        label='학습진행률',max_value=100, min_value=0, format='%d%%'
)},
hide_index=True)

st.metric(
    label='총매출', value='3,000,000원',delta='20,000원'
)

current_sales = 35_000_000
previous_sales = 32_500_000

groth_rate=(current_sales - previous_sales)/ previous_sales * 100
st.metric(
    label='이번달 매출', value=f'{current_sales:,}원',delta=f'{groth_rate:.2f}%'
)

st.metric(
    label='일일 평균 환적 처리 시간',
    value='8.2시간',
    delta='-0.8시간',
    delta_color='inverse'
)