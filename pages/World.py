
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
import pandas as pd
import seaborn as sns

st.set_page_config(
    page_title="World",
    page_icon="🌏",
)

DATABASE_URL = "postgresql://postgres:hWWCWtvKQODqEErOleTnHmTcuKWaRAgd@monorail.proxy.rlwy.net:59179/railway"
engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    results = session.execute(text("""
                                   SELECT
                                    _position as position,
                                    _name as name,
                                    title,
                                    streams,
                                    chart_country as code_country,
                                    explicit,
                                    popularity,
                                    genre,
                                    country_name,
                                    latitude,
                                    longitude
                                   FROM
                                    worldchart
                                   """
                                   )
                              )
    df_countries_chart = pd.DataFrame(results)


# we should not need this

st.header(":orange[Les tendances à travers le monde (source Spotify)]:globe_with_meridians:")

# selection du pays
selected_country = st.selectbox(
    "Sélectionner le pays",
    list(df_countries_chart["country_name"].sort_values(ascending=True).unique()),
    index=None,
    placeholder="Select country",
)

# define the data with selected country
if selected_country:
  country_name = selected_country
  data = df_countries_chart[df_countries_chart["country_name"] == selected_country]
else:
  data = df_countries_chart
  country_name = "Tous les pays"

# Les Tops a travers le monde
st.subheader(":orange[Les charts]	:top:")
selected_position = st.selectbox(
    "Choisir les derniers ou les premiers",
    ["Premiere position", "Derniere position"],
)

if selected_position =="Premiere position":
    order_asc = True
else:
    order_asc = False

# Table charts
df_chart_by_country = data[["position", "name", "title", "streams", "code_country"]].sort_values("position", ascending=order_asc)
df_chart_by_country = df_chart_by_country.drop_duplicates()

st.dataframe(df_chart_by_country)

# afficher les genres predominants
st.subheader(":green[Les genres qui prédominent] :guitar:")

df_genres_pred = data.value_counts('genre').reset_index()[0:15]
st.bar_chart(data=df_genres_pred,
             x="genre",
             y="count",
             x_label="Total",
             y_label="Genres",
             color=None,
             horizontal=True,
             stack=None,
             width=None,
             height=None,
             use_container_width=True
             )

list_genres = list(data.value_counts('genre').reset_index()["genre"][0:15])
df_genres_pred = data[data["genre"].isin(list_genres)]


# graph secteur pour les genres
st.subheader(":green[Leurs répartition en pourcentage] :cd:")
count_genres = df_genres_pred.value_counts("genre").reset_index()

dict_for_secteur = {}
for col, value in count_genres.iterrows():
  dict_for_secteur[value["genre"]] = value["count"]

fig_secteur_genres, ax = plt.subplots(figsize=(6, 6))
ax.pie(dict_for_secteur.values(), labels=dict_for_secteur.keys(), autopct='%1.1f%%', startangle=90)

ax.axis('equal')
sns.set_palette("pastel")
plt.title(f"Répartition des genres pour {country_name}")

# Afficher le graphique
st.pyplot(fig_secteur_genres)

# on peut ajouter un selecteur d'artiste parmis ceux qui sont dans ls chart

# les artist qui ressortent le plus sur ces charts
st.subheader(f":blue[Les artistes les plus présents: {country_name}] :studio_microphone:")

df_artiste_pred = data.value_counts("name").reset_index()[0:15]
st.bar_chart(data=df_artiste_pred, x="name", y="count", x_label="Total", y_label="Artistes", color=None, horizontal=True, stack=None, width=None, height=None, use_container_width=True)
# vs leur popularité
st.subheader(f":blue[Leur popularité:] :blue_heart:")
df_artistes_pop = data.groupby("name")["popularity"].sum().sort_values(ascending=False).reset_index()[0:15]
st.bar_chart(data=df_artistes_pop, x="name", y="popularity", x_label="Notes (popularité)", y_label="Artistes", color=None, horizontal=True, stack=None, width=None, height=None, use_container_width=True)

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

sns.set_palette("pastel")
st.pyplot(fig_explicit)

# carte repartition des streams
st.subheader(":green[Répartition géographique des streams] :globe_with_meridians:")
list_genres = list(df_countries_chart.value_counts('genre').reset_index()["genre"][0:15])

df_streams = df_countries_chart.groupby(["code_country", "longitude", "latitude"])["streams"].sum().reset_index()
df_streams["streams"] = df_streams["streams"].apply(lambda x: x/100)
st.map(data=df_streams, latitude="latitude", longitude="longitude", color="#ffaa00", size="streams", zoom=None, use_container_width=True, width=None, height=None)
print(df_streams.info())
print(df_streams)

# faire un selecteur pour le genre et voir sa répartition

