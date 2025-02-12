import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import seaborn as sns
from pathlib import Path
import base64

import plotly.graph_objects as go
# 1️⃣ Connexion à la base PostgreSQL
conn = psycopg2.connect(
    dbname="railway",
    user="postgres",
    password="hWWCWtvKQODqEErOleTnHmTcuKWaRAgd",
    host="monorail.proxy.rlwy.net",
    port="59179"
)
cursor = conn.cursor()
st.set_page_config(page_title="Platforms", page_icon="🎤", layout="wide")
# Définissez le chemin de votre image
image_path =r"C:\Users\nemri\Desktop\projet3\BJ2gNMU.webp"  # Remplacez par le chemin de votre image

# Lire l'image et la convertir en base64
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

# CSS pour intégrer l'image comme fond d'écran
page_bg_css = f"""
<style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
</style>
"""

# Injectez le CSS dans Streamlit
st.markdown(page_bg_css, unsafe_allow_html=True)
# Personnalisation des titres avec CSS
title_css = """
<style>
    h1, h2, h3, h4, h5, h6 {
        font-size: 24px !important; /* Remplacez par la taille souhaitée */
        font-family: 'Arial', sans-serif; /* Police personnalisée */
        color: #333333; /* Couleur des titres */
        text-align: center; /* Centrer les titres */
        margin-bottom: 16px; /* Espacement sous les titres */
    }
</style>
"""
# Injectez le CSS dans l'application Streamlit
st.markdown(title_css, unsafe_allow_html=True)

# Configuration de la page Streamlit

st.markdown("""
    <style>
    .title {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    <div class="title">🎵 Analyse et Comparaison des Plateformes Musicales : Tendances et Insights 🎧</div>
""", unsafe_allow_html=True)

# 2️⃣ Récupération des données depuis la base
query = """
    SELECT "track", "album_name", "artist", "release_date", "track_score",
           "spotify_streams", "spotify_playlist_count", "spotify_playlist_reach",
           "spotify_popularity", "youtube_views", "youtube_likes", "tiktok_posts",
           "tiktok_likes", "tiktok_views", "youtube_playlist_reach",
           "apple_music_playlist_count", "deezer_playlist_count",
           "deezer_playlist_reach", "amazon_playlist_count", "shazam_counts"
    FROM most_streamed;
"""
cursor.execute(query)
data = cursor.fetchall()

# Fermer la connexion après récupération des données
conn.close()

# Définition des colonnes pour le DataFrame
columns = [
    "track", "album_name", "artist", "release_date", "track_score",
    "spotify_streams", "spotify_playlist_count", "spotify_playlist_reach",
    "spotify_popularity", "youtube_views", "youtube_likes", "tiktok_posts",
    "tiktok_likes", "tiktok_views", "youtube_playlist_reach",
    "apple_music_playlist_count", "deezer_playlist_count",
    "deezer_playlist_reach", "amazon_playlist_count", "shazam_counts"
]

# Création du DataFrame
df = pd.DataFrame(data, columns=columns)

# 3️⃣ Préparation des données
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
df.dropna(subset=["release_date"], inplace=True)

# Sélection de la plage de dates
min_date = df["release_date"].min().date()
max_date = df["release_date"].max().date()
selected_date_range = st.sidebar.slider(
    "Date de sortie de l'album",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

df_filtered = df[
    (df["release_date"] >= pd.Timestamp(selected_date_range[0])) & 
    (df["release_date"] <= pd.Timestamp(selected_date_range[1]))
]

# 5️⃣ Filtrage par album
album_list = df_filtered["album_name"].unique()
selected_album = st.sidebar.selectbox("Sélectionner un album", ["Tous"] + list(album_list))

if selected_album != "Tous":
    df_filtered = df_filtered[df_filtered["album_name"] == selected_album]

# 6️⃣ Filtrage par artiste
artist_list = df_filtered["artist"].unique()
selected_artist = st.sidebar.selectbox("Sélectionner un artiste", ["Tous"] + list(artist_list))

if selected_artist != "Tous":
    df_filtered = df_filtered[df_filtered["artist"] == selected_artist]
if st.sidebar.button("🔄 Réinitialiser les filtres"):
    st.session_state.selected_album = "Tous"
    st.session_state.selected_artist = "Tous"
    st.experimental_rerun()  # Recharge l'application

# Données de comparaison
platforms = ['spotify_streams', 'youtube_views', 'tiktok_views']
platform_comparaison = df_filtered[platforms].sum()

# Création du graphique
fig = px.bar(
    x=platform_comparaison.index,  # Plateformes sur l'axe X
    y=platform_comparaison.values,  # Total des streams sur l'axe Y
    labels={'x': 'Plateformes', 'y': 'Total des Streams'},
    title="Comparaison des plateformes de streaming",
    text=platform_comparaison.values,  # Affiche les valeurs sur les barres
    template='plotly_dark'  # Style sombre
)

# Personnalisation des couleurs
fig.update_traces(
    textposition='outside',  # Texte à l'extérieur des barres
    texttemplate='%{text:.0f}',  # Texte arrondi
    marker=dict(
        color=["#0077B5",'#636EFA', '#69C9D0'],  # Spotify en vert, YouTube en rouge, TikTok en turquoise
        line=dict(width=0.2, color='DarkSlateGrey')  # Bordures des barres
    )
)

# Mise en page et ajustements
fig.update_layout(
    title_font_size=24,
    title_font_family="Arial, sans-serif",
    xaxis_title_font_size=18,
    yaxis_title_font_size=18,
    xaxis_title="Plateformes",
    yaxis_title="Total des Streams",
    xaxis_tickangle=-45,  # Incline les noms des plateformes
    yaxis_tickformat='.0f',  # Format des nombres sur l'axe Y
    margin=dict(l=40, r=40, t=40, b=40),
    bargap=0.2,  # Ajuste l'espacement entre les barres
    width=600,  # Largeur du graphique
    height=400  # Hauteur du graphique
)

# Afficher le graphique dans Streamlit
st.plotly_chart(fig)
# Fonction pour récupérer les top 10 titres par plateforme
def top_tracks_by_platform(df, platform):
    # Récupération des 10 meilleurs titres pour une plateforme
    top_tracks = df[['track', 'artist', platform]].sort_values(by=platform, ascending=False).head(10)
    return top_tracks

# Sélection de la plateforme via un selectbox
platform_choice = st.selectbox("Choisissez une plateforme", platforms)

# Affichage des meilleurs titres pour la plateforme choisie
st.write(f"Top 10 des titres pour {platform_choice}")
top_tracks = top_tracks_by_platform(df, platform_choice)

# Création du graphique camembert (pie chart)
fig2 = px.pie(
    top_tracks, 
    names='track',  # Les titres des morceaux
    values=platform_choice,  # Les valeurs correspondant à la popularité
    color='track',  # Les couleurs seront différenciées par titre
    title=f"Répartition de la popularité des 10 meilleurs titres sur {platform_choice}"
)

# Ajustement du layout
fig2.update_traces(
    textinfo='percent+label',  # Affiche les pourcentages et le label
    hoverinfo='label+value+percent'  # Info au survol
)

fig2.update_layout(
    title_font_size=24,
    margin=dict(l=40, r=40, t=40, b=40),  # Marges du graphique
    width=600,  # Largeur du graphique
    height=400  # Hauteur du graphique
)

# Affichage du graphique dans Streamlit
st.plotly_chart(fig2)

# Comparaison de la portée des playlists par plateforme


# Calcul de la portée totale des playlists par plateforme
playlist_reach_comparison = df_filtered[
    ["spotify_playlist_reach", "youtube_playlist_reach", "deezer_playlist_reach"]
].sum()

# Création du graphique
fig_reach = px.bar(
    x=playlist_reach_comparison.index,
    y=playlist_reach_comparison.values,
    labels={'x': 'Plateformes', 'y': 'Portée totale des playlists'},
    title="Comparaison de la portée des playlists par plateforme",
    text_auto=True,
    width=600,  # Largeur du graphique
    height=400  
)

# Personnalisation
fig_reach.update_traces(
    marker_color=["#0077B5", '#636EFA', '#FFD700'],  # Spotify (bleu), YouTube (bleu clair), Deezer (jaune)
    width=0.2,  # Ajuste la largeur des barres
    textfont_size=14,  # Taille du texte
    textposition="outside"  # Texte en dehors des barres
)

# Personnalisation de la mise en page
fig_reach.update_layout(
    title_font=dict(size=22, family="Arial", color="white"),  # Style du titre
    xaxis_title_font=dict(size=16),
    yaxis_title_font=dict(size=16),
    margin=dict(t=50, b=50, l=50, r=50),  # Ajouter des marges pour éviter que les éléments soient coupés
    xaxis=dict(tickangle=45),  # Rotation des étiquettes sur l'axe X
    yaxis=dict(tickformat=".2s"),
  # Hauteur du graphique
    # Format des valeurs de l'axe Y (en millions, milliards, etc.)
)

# Affichage du graphique dans Streamlit
st.plotly_chart(fig_reach)

# Comparaison du nombre de playlists contenant les chansons
playlist_count_comparison = df_filtered[
    ["spotify_playlist_count", "apple_music_playlist_count", "deezer_playlist_count", "amazon_playlist_count"]
].sum()

# Création du graphique
fig_playlist_count = px.bar(
    x=playlist_count_comparison.index,
    y=playlist_count_comparison.values,
    labels={'x': 'Plateformes', 'y': 'Nombre total de playlists'},
    title="Comparaison du nombre de playlists contenant les chansons",
    text_auto=True,
    width=600,  # Largeur du graphique
    height=400  # Hauteur du graphique
)

# Afficher avec Streamlit
st.plotly_chart(fig_playlist_count)

# Calcul des ratios d'engagement
df_filtered["youtube_engagement"] = df_filtered["youtube_likes"] / df_filtered["youtube_views"]
df_filtered["tiktok_engagement"] = df_filtered["tiktok_likes"] / df_filtered["tiktok_views"]

# Moyenne par plateforme
engagement_metrics = df_filtered[["youtube_engagement", "tiktok_engagement"]].mean()

# Création du graphique
fig_engagement = px.bar(
    x=engagement_metrics.index,
    y=engagement_metrics.values,
    labels={'x': 'Plateforme', 'y': 'Ratio Likes / Vues'},
    title="Engagement des utilisateurs sur YouTube vs TikTok",
    text_auto=True,
    width=600,  # Largeur du graphique
    height=400  
    
)

# Ajustements visuels
fig_engagement.update_traces(
    width=0.2,  # Largeur des barres (ajustée pour un meilleur équilibre visuel)
    marker_color=['#636EFA', '#FFD700'],  # Couleurs personnalisées pour YouTube et TikTok
    textfont_size=14,  # Taille des chiffres sur les barres
    textposition='outside'  # Positionnement du texte en dehors des barres
)

# Mise à jour de l'apparence globale
fig_engagement.update_layout(
    font=dict(size=16),  # Taille globale de la police
    title_font_size=18,  # Taille du titre
    title_x=0.1,  # Centrer le titre
    xaxis_title="Plateforme",
    yaxis_title="Ratio Likes / Vues",
    yaxis=dict(
        tickformat=".1%"  # Format en pourcentage pour l'axe Y
    ),
    margin=dict(l=50, r=50, t=50, b=50)  # Ajustements des marges
)

# Afficher avec Streamlit
st.plotly_chart(fig_engagement)

# Calcul des streams totaux par artiste
top_artists = df_filtered.groupby("artist")[
    ["spotify_streams", "youtube_views", "tiktok_views", "shazam_counts"]
].sum().sum(axis=1).sort_values(ascending=False).head(10)

# Création du graphique
fig_top_artists = px.bar(
    x=top_artists.index,
    y=top_artists.values,
    labels={'x': 'Artistes', 'y': 'Total des streams'},
    title="Top 10 des artistes les plus streamés",
    text_auto=True,
    width=600,  # Largeur du graphique
    height=400  # Hauteur du graphique
)

# Ajustement de l'espacement entre les barres
fig_top_artists.update_layout(
    bargap=0.2  # Espacement entre les barres (0.0 pour collées, 1.0 pour très espacées)
)

# Affichage du graphique avec Streamlit
st.plotly_chart(fig_top_artists)

# Grouper par année de sortie et calculer les streams totaux
df_filtered["release_year"] = df_filtered["release_date"].dt.year
streams_by_year = df_filtered.groupby("release_year")[
    ["spotify_streams", "youtube_views", "tiktok_views", "shazam_counts"]
].sum().reset_index()

# Graphique interactif
fig_time_series = px.line(
    streams_by_year,
    x="release_year",
    y=["spotify_streams", "youtube_views", "tiktok_views", "shazam_counts"],
    labels={"release_year": "Année de sortie", "value": "Nombre total de streams"},
    title="Évolution du nombre de streams en fonction de l'année de sortie"
)

st.plotly_chart(fig_time_series)

# Trier les chansons les plus populaires
top_tracks = df.nlargest(10, "spotify_popularity")

# Renommer les colonnes pour des noms plus clairs
top_tracks_renamed = top_tracks.rename(
    columns={
        "spotify_streams": "Écoutes Spotify",
        "youtube_views": "Vues YouTube",
        "tiktok_views": "Vues TikTok",
        "shazam_counts": "Identifications Shazam"
    }
)

# Création du graphique en barres empilées
fig_stacked = px.bar(
    top_tracks_renamed, 
    x="track", 
    y=["Écoutes Spotify", "Vues YouTube", "Vues TikTok", "Identifications Shazam"],
    title="Répartition des écoutes par plateforme pour les chansons les plus populaires",
    labels={"value": "Nombre d’écoutes", "track": "Titre du morceau"},
    barmode="stack"
)

# Affichage du graphique avec Streamlit
st.plotly_chart(fig_stacked)

