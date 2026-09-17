import streamlit as st
#streamlit  run <파일명>.py
#ctrl+c 끄기
st.title('쇼핑몰 운영 대시보드')   #마크다운 #
st.header('매출현황')          #마크다운 ##
st.subheader('금일 매출 현황')        #마크다운 ###
st.write('금일 발생 주문 매출')  #일반적인 글
st.subheader('월간 매출')
st.write('이번달 누적 매출')
st.header('고객현황')
st.subheader('신규 가입자')
st.write('금일 가입한 신규 가입자')  #마크다운 문법 적용
st.write('**판매량**: 120개')                           
st.text('**매출액**: 3500000')                           #그냥 텍스트


st.caption('매출 데이터는 매일 오전 9시에 갱신')
st.caption('기준일: 26-09-15')


st.markdown('''
### 매출 분석 결과
이번달 주요 지표입니다.
- 총 주문수 : 30건
- 총 매출 : 10만원
- 평균 주문 금액 : 3만원

접자
'''
)

st.code(               #자바 코드 수정 방지
    '''
'''
)