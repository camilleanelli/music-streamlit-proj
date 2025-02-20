
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
import pandas as pd
import seaborn as sns
import altair as alt
import plotly.express as px
import base64

st.session_state["_page"] = "World"

st.set_page_config(
    page_title="Monde",
    page_icon="🌏",
    layout="wide"
)

# imgade de fond animée
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        base64_str = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{base64_str}"  

st.markdown(
    f"""
    <style>
        @keyframes moveBackground {{
            0% {{ background-position: 0% 0%; }}
            50% {{ background-position: 100% 100%; }}
            100% {{ background-position: 0% 0%; }}
        }}

        .stApp {{
            background-image: url("{get_base64_image("img/background.jpg") }");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-color: rgba(0, 0, 0, 0.5);
            background-blend-mode: overlay;
            animation: moveBackground 40s ease-in-out infinite;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Mettre la sidebar semi-transparent
st.markdown(
    """
    <style>
        /* Sélectionne la sidebar entière */
        section[data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.6); /* Modifie entre 0.3 et 0.8 selon le niveau de transparence voulu */
        }

        /* Applique la couleur blanche aux textes pour garantir une bonne lisibilité */
        section[data-testid="stSidebar"] * {color: white;
        }

        div[data-testid]="stHeading"] {
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

animation_html = """
<style>
@keyframes slide {
    0% { transform: translateX(20vw); }  
    50% { transform: translateX(50vw); }  
    100% { transform: translateX(20vw); }  
}
.music-container {
    position: relative;
    width: 100%;
    height: 120px;  /* Ajustez la hauteur au besoin */
    overflow: hidden;
}
.music-note {
    width: 50px;
    position: absolute;
    top: 30px; /* Ajuste la hauteur de la note */
    animation: slide 3s linear infinite; /* Durée et répétition */
}
</style>
<div class="music-container">
    <img class="music-note" src="https://img.icons8.com/fluency/48/000000/musical-notes.png" alt="Music Note">
</div>
"""

DATABASE_URL = "postgresql://postgres:hWWCWtvKQODqEErOleTnHmTcuKWaRAgd@monorail.proxy.rlwy.net:59179/railway"
engine = create_engine(DATABASE_URL)

if "World" in st.session_state.get("_page", ""):

  @st.cache_data(show_spinner=False)
  def load_data():
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
        return pd.DataFrame(results)

  # Ajout du titre principal du dashboard
  st.markdown("<h1 style='text-align: center; color: white;'> Top artistes et musiques à l'international </h1>", unsafe_allow_html=True)
  
  loading_container = st.empty()
  loading_container.markdown(animation_html, unsafe_allow_html=True)
  df_countries_chart = load_data()
  loading_container.empty()
  
  # ajouter la possibilité de sélectionner l'europe
  # Sidebar - Filtres
  st.sidebar.header("Filtres")
  selected_country2 = st.sidebar.multiselect(
        "🌐 Localisation",
        list(df_countries_chart["country_name"].sort_values(ascending=True).unique()),
        default="Global",
        placeholder="Tous"
    )

  # define the data with selected country
  if selected_country2:
    data = df_countries_chart[df_countries_chart["country_name"].isin(selected_country2)]
  else:
    data = df_countries_chart

  #Choose category
  selected_genre = st.sidebar.multiselect(
        ":top: Catégorie musicale",
        list(data["genre"].sort_values(ascending=True).unique()),
        placeholder="Tous",
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
    "🎤 Artiste",
    list(data["name"].sort_values(ascending=True).unique()),
    index=None,
    placeholder="Tous"
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
    # col1, col2 = st.columns(2)

    # with col1:
      with st.container():
          st.subheader(f"_Top 50 {" ".join(selected_country2)}_")
          col1, col2, col3 = st.columns(3)
          with col1:
            selected_position = st.selectbox(
                    "Classer par ordre",
                    ["Croissant", "Décroissant"],
                )

          if selected_position =="Croissant":
                order_asc = True
          else:
                order_asc = False

          # Table charts
          df_chart_by_country = data[["position", "name", "title", "streams", "country_name"]].sort_values("position", ascending=order_asc)
          df_chart_by_country = df_chart_by_country.drop_duplicates()

          # Configurer l'affichage des images
          styled_df = (df_chart_by_country.style.format({
            "streams": "{:,.0f}"
            })).background_gradient(subset=["streams"], cmap="RdYlGn")

          # Affichage avec configuration des colonnes
          st.dataframe(
              styled_df,
              column_config={
                  "position": st.column_config.NumberColumn("Position", width="stretch"),
                  "name": st.column_config.TextColumn("Nom", width="stretch"),
                  "title": st.column_config.TextColumn("Titre", width="stretch"),
                  "streams": st.column_config.NumberColumn("Streams", width="stretch"),
                  "country_name": st.column_config.TextColumn("Pays", width="stretch"),
              },
              hide_index=True,
              use_container_width=True
          )

    # with col2:
      st.divider()
      with st.container():
        st.subheader("_Indice de popularité_")
        with st.expander("Qu'est ce que le SPI ?"):
          st.write('''
              L'Indice de popularité de Spotify (SPI) est une mesure de performance rare que Spotify montre aux artistes.
              Le SPI est une échelle de 0 à 100,
              qui aide l'équipe Spotify à mieux comparer et classer les chansons sur la platform
              '''
            )
        df_artistes_pop = data.groupby("title")["popularity"].mean().reset_index()[0:15]
        df_artistes_pop = df_artistes_pop.sort_values(by="popularity", ascending=True)
        fig_popularity = px.bar(
          df_artistes_pop,
          x="popularity", y="title",
          orientation="h",
          labels={'genre':'Catégories', 'count': 'Total'},
          height=400
          )

        fig_popularity.update_layout(
                plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
                paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
                legend=dict(
                    bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
                    font=dict(color="white")  # Texte blanc pour la lisibilité
                ),
                margin=dict(t=50, b=50, l=50, r=50),
            )

        st.plotly_chart(fig_popularity, use_container_width=True)


  with tab2:
    col1, col2 = st.columns(2)

    with col1:
      with st.container():
          # afficher les genres predominants
          st.subheader("_Les catégories préférées_")

          df_genres_pred = data.value_counts('genre').reset_index()[0:15]
          df_genres_pred = df_genres_pred.sort_values(by="count", ascending=False)
          with st.container():
            fig_genres = px.bar(
            df_genres_pred,
            x="count",
            y="genre",
            orientation="h",
            labels={'genre':'Catégories', 'count': 'Total'},
            color="genre",
            height=400,
            opacity=1
            )

            fig_genres.update_layout(
                plot_bgcolor="rgba(0, 0, 0, 0.)",  # Fond semi-transparent pour la zone de traçage
                paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
                legend=dict(
                    bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
                    font=dict(color="white")  # Texte blanc pour la lisibilité
                ),
                margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
            )

            st.plotly_chart(fig_genres)

    with col2:
      with st.container():
        # les contenu explicit
        st.subheader("_Les contenus explicites_")

        df_explicit = data.value_counts("explicit").reset_index()

        fig_explicit = px.pie(
        df_explicit,
        names="explicit",
        values="count",
        color="explicit",  # Assurer la correspondance des couleurs
        color_discrete_sequence=px.colors.qualitative.Set2,
        height=400
        )

        fig_explicit.update_layout(
              plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
              paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
              legend=dict(
                  bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
                  font=dict(color="white")  # Texte blanc pour la lisibilité
              ),
              margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
          )
        st.plotly_chart(fig_explicit, use_container_width=True)

    with st.container():
        # graph secteur pour les genres
        st.subheader("_Répartition en pourcentage_")
        count_genres = data.value_counts("genre").reset_index()[0:15]

        fig_secteur_genres = px.pie(
        count_genres,
        names="genre",
        values="count",
        color="genre",  # Assurer la correspondance des couleurs
        color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig_secteur_genres.update_layout(
              plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
              paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
              legend=dict(
                  bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
                  font=dict(color="white")  # Texte blanc pour la lisibilité
              ),
              margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
          )

        st.plotly_chart(fig_secteur_genres, use_container_width=True)

  with tab3:
    col1, col2 = st.columns(2)
    with col1:
        # les artist qui ressortent le plus sur ces charts
        st.subheader("_Les plus présents_")

        df_artiste_pred = data.value_counts("name").reset_index()[0:15]
        df_artiste_pred = df_artiste_pred.sort_values(by=["count"], ascending=True)
        fig_artistes = px.bar(
          df_artiste_pred,
          x="count", y="name",
          orientation="h",
          labels={'name':'Artistes', 'count': 'Total'},
          height=400
          )

        fig_artistes.update_layout(
              plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
              paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
              legend=dict(
                  bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
                  font=dict(color="white")  # Texte blanc pour la lisibilité
              ),
              margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
          )

        st.plotly_chart(fig_artistes)

    with col2:
      st.subheader("_Les streams_")

      df_artistes_stream = data.groupby("name")["streams"].mean().reset_index()[0:15]
      df_artistes_stream = df_artistes_stream.sort_values(by=["streams"], ascending=True)
      fig_streams = px.bar(
          df_artistes_stream,
          x="streams", y="name",
          orientation="h",
          labels={'name':'Tracks', 'streams': 'Nombre de streams'},
          height=400
          )

      fig_streams.update_layout(
          plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
          paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
          legend=dict(
            bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
            font=dict(color="white")  # Texte blanc pour la lisibilité
            ),
          margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
        )
      st.plotly_chart(fig_streams)
  with tab4:
    # carte repartition des streams
    st.subheader("_Répartition géographique_")

    if "Global" in selected_country2 or len(selected_country2) == 1:
      df_streams = df_countries_chart[(df_countries_chart["code_country"] != "GLOBAL")]
      if selected_artist:
        df_streams = df_streams[df_streams["name"] == selected_artist].groupby(["code_country", "longitude", "latitude"])["streams"].mean().reset_index()
      else:
        df_streams = df_streams.groupby(["code_country", "longitude", "latitude"])["streams"].mean().reset_index()
    else:
      df_streams = data.groupby(["code_country", "longitude", "latitude"])["streams"].mean().reset_index()

    st.map(data=df_streams, latitude="latitude", longitude="longitude", color="#763436", size="streams", use_container_width=True, width=None, height=None)




