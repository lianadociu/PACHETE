import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype

st.set_page_config(page_title="Analiza vânzărilor Adidas", layout="wide")
st.title("📊 Proiect Pachete Software – Analiza activității unei organizații")

st.markdown("""
### Definirea problemei
Se analizează datele unei companii de articole sportive pentru a înțelege comportamentul vânzărilor, metodele de distribuție și produsele cele mai profitabile. Se oferă și sugestii de optimizare bazate pe statistici.

### Informații necesare pentru rezolvare
- Setul de date `adidas_us_sales.csv`
- Pachetele Python: `pandas`, `matplotlib`, `streamlit`
- Cunoștințe de agregare, filtrare, curățare și vizualizare a datelor

---
""")

# Încărcare și tratare date
df = pd.read_csv("adidas_us_sales.csv", index_col=1)

def nan_replace_t(t):
    assert isinstance(t, pd.DataFrame)
    for v in t.columns:
        if any(t[v].isna()):
            if is_numeric_dtype(t[v]):
                t[v].fillna(t[v].mean(), inplace=True)
            else:
                t[v].fillna(t[v].mode()[0], inplace=True)

nan_replace_t(df)

st.subheader("1. Tratarea valorilor lipsă")
st.write("Valorile lipsă sunt completate fie cu media (numeric), fie cu moda (câmpuri categorice).")
st.dataframe(df.head())

st.subheader("2. Curățare și sortare produse")
lista = list(df["Product"])
lista_strip = sorted([i.strip() for i in lista])
st.write(sorted(set(lista_strip)))

st.subheader("3. Număr comenzi pe produs")
dict_aparitii = {i: lista_strip.count(i) for i in set(lista_strip)}
st.json(dict_aparitii)

st.subheader("4. Vânzări pe metodă de vânzare")
dict_vanzari = df.groupby("Sales Method").sum(numeric_only=True)["Units Sold"].to_dict()
st.json(dict_vanzari)

st.subheader("5. Aplicare reduceri")
def f_discount(preturi):
    for i in range(len(preturi)):
        if 55 <= preturi[i] < 65:
            preturi[i] *= 0.95
        elif 65 <= preturi[i] <= 75:
            preturi[i] *= 0.9
        else:
            preturi[i] *= 0.85
    return preturi

preturi = df['Price per Unit'].tolist()
preturiNoi = f_discount(preturi.copy())
st.write(preturiNoi[:10])

st.subheader("6. Filtrare tranzacții după criterii multiple")
st.dataframe(df.loc[(df['Sales Method'] == 'In-store') & (df['Retailer'] == 'West Gear')])

st.subheader("7. Eliminare produse Apparel")
df2 = pd.read_csv("adidas_us_sales.csv")
nan_replace_t(df2)
lista_randuri_de_sters = df2.loc[df2['Product'].isin(["Men's Apparel", "Women's Apparel"])].index.values
df2 = df2.drop(lista_randuri_de_sters, axis=0)
st.dataframe(df2.head())

st.subheader("8. Extracție și prelucrare date calendaristice")
date_tranzactii = []
for x in range(0, len(df)):
    y = df.iloc[x, 1]
    zi = f"0{y[0]}" if y[1] == "/" else y[0:2]
    date_tranzactii.append(zi)
st.write(date_tranzactii[:10])

st.subheader("9. Preț mediu și profit per categorie")
st.dataframe(df.groupby('Product')['Total Sales'].mean())
st.dataframe(df.groupby('Sales Method')['Operating Profit'].sum())

st.subheader("10. Agregare vânzări per retailer și produs")
st.dataframe(df.groupby(['Retailer', 'Product'])['Units Sold'].sum())

st.subheader("11. Statistici agregate și extreme")
data_stats = df.groupby(['Sales Method', 'Retailer']).agg({'Units Sold': sum, 'Total Sales': "mean", 'Operating Profit': "mean"})
st.dataframe(data_stats)
st.dataframe(df.groupby(['Product']).agg({'Operating Profit': [min, max]}))

st.subheader("12. Statistici multiple pe Retailer")
st.dataframe(df.groupby(['Retailer']).agg({"Price per Unit": [sum, min, max, "count"]}))

st.subheader("13. Număr comenzi per ID de retailer")
produse_grupate = df.groupby(['Retailer ID']).groups
for id_retailer, produse in produse_grupate.items():
    st.write(f"Retailer ID {id_retailer}: {len(produse)} comenzi")

st.subheader("14. Reprezentare grafică: Profit vs Cantitate vândută")
df_plot = df[df['Units Sold'] > 700]
fig, ax = plt.subplots()
df_plot.plot(kind='bar', y=['Operating Profit', 'Units Sold'], ax=ax)
st.pyplot(fig)

st.subheader("15. Modificare valori înregistrate")
df_nou = df.copy()
df_nou.loc[(df_nou['Invoice Date'] == '1/2/2021'), 'Sales Method'] = 'In-store'
st.dataframe(df_nou[['Retailer', 'Invoice Date', 'Sales Method']])

st.markdown("""
---
### Interpretare economică
Rezultatele obținute permit identificarea produselor profitabile, evaluarea metodelor de distribuție și aplicarea reducerilor strategice. Eliminarea produselor neprofitabile și ajustarea canalelor de vânzare pot contribui la creșterea profitabilității companiei.
""")
