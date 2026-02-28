import streamlit as st
import pandas as pd
import random

st.title("Zero-Knowledge Proof Fintech Demo")

df = pd.read_csv("creditcard_sample.csv")
selected = st.number_input("Select transaction index:", min_value=0, max_value=len(df)-1, value=0)
txn = df.iloc[[selected]]
st.write("Selected Transaction:")
st.dataframe(txn)

g = 2
x = random.randint(1, 100)
y = g ** x

r = random.randint(1, 100)
commitment = g ** r
challenge = random.randint(1, 100)
response = r + challenge * x
check = (g ** response) == (commitment * (y ** challenge))

st.write(f"ZKP Result: {'Approved' if check else 'Denied'}")
