
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
import pandas as pd
import seaborn as sns
<<<<<<< HEAD
import plotly.express as px
=======
>>>>>>> 095245efcdabaab9e9be0fc50667eb2891a5613a

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


<<<<<<< HEAD
st.header("Les tendances sur plusieurs pays - source Spotify :globe_with_meridians:")


col1, col2, col3 = st.columns(3)

with col1:
  # ajouter la possibilité de sélectionner l'europe
  selected_country2 = st.sidebar.multiselect(
      "Choisir un ou plusieurs pays",
      list(df_countries_chart["country_name"].sort_values(ascending=True).unique()),
      default=None
  )


# define the data with selected country
if selected_country2:
  country_name = selected_country2
  data = df_countries_chart[df_countries_chart["country_name"].isin(selected_country2)]
=======
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
>>>>>>> 095245efcdabaab9e9be0fc50667eb2891a5613a
else:
  data = df_countries_chart
  country_name = "Tous les pays"

<<<<<<< HEAD
#Choose category
selected_genre = st.sidebar.multiselect(
      "Sélectionner une catégorie",
      list(data["genre"].sort_values(ascending=True).unique()),
      placeholder="Sélectionner une catégorie",
      default=None
      )

# Define data
if selected_genre:
  category = selected_genre
  data = data[data["genre"].isin(selected_genre)]
else:
  data = data

# choose artist
selected_artist = st.sidebar.selectbox(
  "Nom artiste",
  list(data["name"].sort_values(ascending=True).unique()),
  index=None,
  placeholder="Sélectionner un artiste"
)

# Define the data
if selected_artist:
  artiste_name = selected_artist
  data = data[data["name"] == artiste_name]
else:
  data = data

tab1, tab2, tab3, tab4 = st.tabs(["Chart :top:", "Catégories musicales :guitar:", "Artistes :studio_microphone:", "Stream :headphones:"])

with tab1:
  # Les Tops a travers le monde
  col1, col2 = st.columns(2)
  with col1:
    with st.container():
      selected_position = st.selectbox(
          "Classer par ordre",
          ["Croissant", "Décroissant"],
      )

      if selected_position =="Croissant":
          order_asc = True
      else:
          order_asc = False

      # Table charts
      df_chart_by_country = data[["position", "name", "title", "streams", "code_country"]].sort_values("position", ascending=order_asc)
      df_chart_by_country = df_chart_by_country.drop_duplicates()
      st.dataframe(df_chart_by_country)

    with col2:
      with st.container():
        df_artistes_pop = data.groupby("name")["popularity"].mean().sort_values(ascending=False).reset_index()[0:15]
        st.bar_chart(data=df_artistes_pop, x="name", y="popularity", x_label="SPI indice", y_label="Artistes", color=None, horizontal=True, stack=None, width=None, height=None, use_container_width=True)

        with st.expander(":green[Qu'est ce que le SPI ?]"):
          st.write('''
              L'Indice de popularité de Spotify (SPI) est une mesure de performance rare que Spotify montre aux artistes.
              Le SPI est une échelle de 0 à 100,
              qui aide l'équipe Spotify à mieux comparer et classer les chansons sur la platform
              '''
            )

with tab2:
  col1, col2 = st.columns(2)

  with col1:
    with st.container():

        # afficher les genres predominants
        st.markdown("#### Les catégories qui prédominent :guitar:")

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

  with col2:
    with st.container():
      # les contenu explicit
      st.markdown("#### Les contenus explicites :underage:")

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

  with st.container():
      # graph secteur pour les genres
      st.markdown("#### Répartition en pourcentage :cd:")
      count_genres = data.value_counts("genre").reset_index()[0:15]

      dict_for_secteur = {}
      for col, value in count_genres.iterrows():
        dict_for_secteur[value["genre"]] = value["count"]

      fig_secteur_genres, ax = plt.subplots(figsize=(6, 6))
      ax.pie(dict_for_secteur.values(), labels=dict_for_secteur.keys(), autopct='%1.1f%%', startangle=90)

      ax.axis('equal')
      sns.set_palette("pastel")
      plt.title("Répartition des genres")

      # Afficher le graphique
      st.pyplot(fig_secteur_genres)



with tab3:
  col1, col2 = st.columns(2)
  with col1:

      # les artist qui ressortent le plus sur ces charts
      st.markdown("#### Les plus présents")

      df_artiste_pred = data.value_counts("name").reset_index()[0:15]
      st.bar_chart(data=df_artiste_pred, x="name", y="count", x_label="Total", y_label="Artistes", color=None, horizontal=True, stack=None, width=None, height=None, use_container_width=True)


  with col2:
    st.markdown("#### :green_heart: Les streams")

    df_artistes_stream = data.groupby("name")["streams"].mean().sort_values(ascending=False).reset_index()[0:15]
    st.bar_chart(data=df_artistes_stream, x="name", y="streams", x_label="Moyenne des streams", y_label="Artistes", horizontal=True)

with tab4:
  # carte repartition des streams
  st.markdown("#### :globe_with_meridians: Répartition géographique ")

  df_streams = data.groupby(["code_country", "longitude", "latitude"])["streams"].sum().reset_index()
  df_streams["streams"] = df_streams["streams"].apply(lambda x: x/100)
  st.map(data=df_streams, latitude="latitude", longitude="longitude", color="#ffaa00", size="streams", zoom=None, use_container_width=True, width=None, height=None)



=======
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
>>>>>>> 095245efcdabaab9e9be0fc50667eb2891a5613a

