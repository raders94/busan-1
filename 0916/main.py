'''
title
header
subheader
text
write
caption
markdown


'''


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.markdown('''
### 매출 분석 결과

이번달 주요 지표

* 총 주문수 : **1000건**
- 총 매출 : 350000만원
- 평균 주문 금액: 28000원

매출은 지난달보다 2% 증가


---
''')
scores= [75,85,65,63,85]


avg = sum(scores)/len(scores)


st.subheader('학생 평균')
st.markdown(f'현재 학생들의 평균점수는 **{avg:.2f}**')
st.markdown('---')

ex_sql = '''
SELECT
    category, tag, price
FROM
    orders
GROUP BY
    category


'''

st.code(ex_sql, language='sql')
st.markdown('---')



sales = pd.DataFrame({

    '월' : [
        '1월',
        '1월',
        '1월',
        '1월',
        '1월',
    ],
    '가격' : [
        1200,
        1500,
        1340,
        1500,
        1200
    ],
    '판매량':[
        3,
        4,
        6,
        7,
        6,
    ]
})

sales['매출']=sales['가격']*sales['판매량']

st.title('월별매출')
st.dataframe(sales, hide_index=True)
st.markdown('---')
st.table(sales)
st.markdown('---')

image= np.zeros((
    200,400,3),
    dtype=np.uint8

    )

image[:,:200]=[80,140,220]
image[:,200:]=[1,200,150]

st.image(image, caption='넘파이로 그린 그림')
st.caption('numpy배열로 그린 그림')

st.markdown('---')

st.image('pic.jpg',
         width=200,

         )

st.markdown('---')
st.title('수식')
st.latex(r'p=3.141592\2')   #raw

st.latex(r'''
\bar{x}=\frac{1}{n}
\sum_{i-1}^{n} x_i
''')

st.markdown('---')

st.title('코드 실행 과정 확인')

with st.echo():               #문자열이 아닌 실제 코드 =>연산가능
    numbers = [10,20,30]
    total = sum(numbers)
    st.write(f'합계: {total}')

st.markdown('---')

st.info("데이터는 매일 오전 9시에 갱신")
st.success("데이터는 매일 오전 9시에 갱신")
st.warning("데이터는 매일 오전 9시에 갱신")
st.error("데이터는 매일 오전 9시에 갱신")

st.markdown('---')
score = 85
st.title('성적 확인')

st.write(f'wjatn: {score}')

if score >=90:
    st.success('good')
elif score >= 80:
    st.info('not bad')

else:
    st.warning('horrible')



    