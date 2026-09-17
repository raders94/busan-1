import streamlit as st
import pandas as pd

st.title('버튼 실습')

clicked = st.button('집에 가고 싶다')
st.write(f'버튼상태:{clicked}')


if st.button('분석시작'):
    st.success('데이터 분석 시작')


st.title('체크박스')

checked= st.checkbox(
        '상세정보 표시'
    )

st.write(f'체크박스선택 : {checked}')

st.title('슬라이더 실습')

score= st.slider(label='점수를 선택', min_value=0, max_value=100, step=10, value=50)

st.write(f'선택된 점수: {score}')

scorerange =st.slider(label='점수 범위', min_value=0, max_value=100, step=10, value=(60,90))

st.write(f'점수 최소값: {scorerange[0]}')
st.write(f'점수 최대값: {scorerange[1]}')

st.title('Number Input')

age= st.number_input(label='나이를 입력',
                min_value=0, max_value=120,step=2,value=20)

st.write(f'선택된 나이 : {age}')

st.title('Text Input')
name = st.text_input('input your name')

st.write(f'신규 고객: {name}')


port = st.text_input('항만 터미널 검색', placeholder='예시: 신항-제1터미널')

st.write(f'결과: {port}')

st.subheader('스마트 항만 로그인')
st.text_input('ID', placeholder='예시: 신항-제1터미널')
st.text_input('PW', type='password')


items= pd.DataFrame({
    '항만':['감만항', '신항', '덕포항', '포항항', '북항'],
    '환적수':[190_000,1000,170,2,5]
})

st.title('항만 검색 대시보드')
terminal_name = st.text_input('항만 검색')

if terminal_name:
    result = items[items['항만'].str.contains(terminal_name)]
else:
    result = items


st.dataframe(result)