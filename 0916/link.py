import streamlit as st
import pandas as pd
import numpy as np

from views.port1 import port_1
from views.port2 import port_2

st.set_page_config(
    page_title='운영 대시보드',
    layout='wide',
    initial_sidebar_state='expanded',

)



with st.sidebar:
    st.title('메뉴')
    menu = st.radio(
        '대시보드 선택',
        options=['북항','신항1','신항2']
    )

if menu == '북항':
    port_1()
elif menu == '신항1':
    port_2()


elif menu == '신항2':
    with st.container():
        st.title('신항2 대시보드')
        st.write('신항2 kpi')



with st.container():
    st.write(f'선택된 메뉴: {menu}')