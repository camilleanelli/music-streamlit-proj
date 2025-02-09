import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
import pandas as pd
import plotly.express as px
import seaborn as sns

st.set_page_config(
    page_title="Home",
    page_icon="👋",

)
DATABASE_URL = "postgresql://postgres:hWWCWtvKQODqEErOleTnHmTcuKWaRAgd@monorail.proxy.rlwy.net:59179/railway"
engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    results = session.execute(text("SELECT * FROM countrychart"))
    df_countries_chart = pd.DataFrame(results)

df_countries_chart["streams"] = df_countries_chart["streams"].astype("float")

st.header(":orange[Les tendances à travers le monde (source Spotify)]:globe_with_meridians:")

print(df_countries_chart)
# selection du pays
country = st.selectbox(
    "Choisir le pays",
    list(df_countries_chart["chart_country"].unique()),
    index=None,
    placeholder="Select country",
)


# define the data with selected country
if country:
  country_name = country
  data = df_countries_chart[df_countries_chart["chart_country"] == country_name]
else:
  data = df_countries_chart
  country_name = "Tous les pays"

st.subheader(":orange[Les charts]	:top:")
selected_position = st.selectbox(
    "Choisir les derniers ou les premiers",
    ["Premiere position", "Derniere position"],
)

if selected_position =="Premiere position":
    order_asc = True
else:
    order_asc = False

df_chart_by_country = data[["_position", "_name", "title", "streams", "chart_country"]].sort_values("_position", ascending=order_asc)
df_chart_by_country = df_chart_by_country.drop_duplicates()

st.dataframe(df_chart_by_country)

# afficher les genres predominants
st.subheader(":green[Les genres qui prédominent] :guitar:")

df_genres_pred = data.value_counts('genre').reset_index()[0:15]

st.bar_chart(data=df_genres_pred, x="genre", y="count", x_label="Total", y_label="Genres", color=None, horizontal=True, stack=None, width=None, height=None, use_container_width=True)


list_genres = list(data.value_counts('genre').reset_index()["genre"][0:15])
df_genres_pred = data[data["genre"].isin(list_genres)]


# graph secteur pour les genres
st.subheader(":green[Leurs répartition en pourcentage] :cd:")
count_genres = df_genres_pred.value_counts("genre").reset_index()

dict_for_secteur = {}
for col, value in count_genres.iterrows():
  dict_for_secteur[value["genre"]] = value["count"]

fig_1, ax = plt.subplots(figsize=(6, 6))
ax.pie(dict_for_secteur.values(), labels=dict_for_secteur.keys(), autopct='%1.1f%%', startangle=90)

ax.axis('equal')

# Afficher le graphique avec Seaborn (tu peux personnaliser les couleurs avec Seaborn)
sns.set_palette("pastel")
plt.title(f"Répartition des genres pour {country_name}")

# Afficher le graphique
st.pyplot(fig_1)

# on peut ajouter un selecteur d'artiste parmis ceux qui sont dans ls chart
# on peut ajouter un selecteur de genre

# créer une map avec la répartition des genres
# les artist qui ressortent le plus sur ces charts
st.subheader(f":blue[Les artistes les plus présents: {country_name}] :studio_microphone:")

# les 15 artistes les plus présents dans les charts
df_artiste_pred = data.value_counts("_name").reset_index()[0:15]
st.bar_chart(data=df_artiste_pred, x="_name", y="count", x_label="Total", y_label="Artistes", color=None, horizontal=True, stack=None, width=None, height=None, use_container_width=True)
# vs
# evaluer leur popularité

# fig_artistes_plus_presents = plt.figure(figsize=(10, 10))
# sns.countplot(data = df_artiste_pred, y='_name')
# plt.ylabel("Artistes")
# plt.xlabel("Total")
# st.pyplot(fig_artistes_plus_presents)


# les contenu explicit
st.subheader(f":red[Les contenus explicites pour {country_name}] :underage:")

df_explicit = data.value_counts("explicit").reset_index()
dict_exp = {}
for index, value in df_explicit.iterrows():
  key = "Oui" if value["explicit"] == True else "Non"
  dict_exp[key] = value["count"]

fig_explicit, ax = plt.subplots(figsize=(6, 6))
ax.pie(dict_exp.values(), labels=dict_exp.keys(), autopct='%1.1f%%', startangle=90)

ax.axis('equal')

# Afficher le graphique avec Seaborn (tu peux personnaliser les couleurs avec Seaborn)
sns.set_palette("pastel")

st.pyplot(fig_explicit)
# tableau ou graph pour chaque chart

# carte repartition des streams

# carte repartition des genres
st.subheader(":green[Répartition géographique des genres] :globe_with_meridians:")
list_genres = list(df_countries_chart.value_counts('genre').reset_index()["genre"][0:15])

df_streams = df_countries_chart.groupby(["chart_country", "country_long", "country_lat"])["streams"].sum().reset_index()
df_streams["streams"] = df_streams["streams"].apply(lambda x: x/100)
st.map(data=df_streams, latitude="country_lat", longitude="country_long", color="#ffaa00", size="streams", zoom=None, use_container_width=True, width=None, height=None)
print(df_streams.info())
print(df_streams)

