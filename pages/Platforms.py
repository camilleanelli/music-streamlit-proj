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
#une image background depuis une URL en utilisant CSS
st.markdown(
    f"""
    <style>
        .stApp {{
            background-image: url("https://img.freepik.com/free-vector/wavy-colorful-background-style_23-2148497521.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-color: rgba(0,0,0, 0.5); 
            background-blend-mode: overlay; 
        }}
    </style>
    """,
    unsafe_allow_html=True
)

#Rendre la sidebar de Streamlit semi-transparente afin qu'on puisse voir le background
st.markdown(
    """
    <style>
        /* Personnalisation de la barre latérale */
        section[data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.6); /* Fond noir transparent */
            color: white; /* Texte en blanc */
        }
        /* Style pour le texte dans la sidebar */
        section[data-testid="stSidebar"] * {
            color: white; /* Applique le blanc à tous les éléments enfants */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Définissez le chemin de votre image
image_path =r"C:\Users\nemri\Desktop\projet3\BJ2gNMU.webp"  # Remplacez par le chemin de votre image

# Lire l'image et la convertir en base64
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()


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
# Dictionnaire pour renommer les plateformes
platforms = ['spotify_streams', 'youtube_views', 'tiktok_views']
platform_comparaison = df_filtered[platforms].sum()

rename_dict = {
    'spotify_streams': 'Écoutes Spotify',
    'youtube_views': 'Vues YouTube',
    'tiktok_views': 'Vues TikTok'
}

# Renommer les index pour les afficher correctement
platform_comparaison.index = platform_comparaison.index.map(rename_dict)
st.write(f"Comparaison des plateformes de streaming")
# Création du graphique
fig = px.bar(
    x=platform_comparaison.index,  # Plateformes sur l'axe X (renommées)
    y=platform_comparaison.values,  # Total des streams sur l'axe Y
    labels={'x': 'Plateformes', 'y': 'Total des Streams'},
    text=platform_comparaison.values,  # Affiche les valeurs sur les barres
    template='plotly_dark'  # Style sombre
)

# Personnalisation des couleurs
fig.update_traces(
    textposition='outside',  # Texte à l'extérieur des barres
    texttemplate='%{text:.0f}',  # Texte arrondi
    marker=dict(
        color=["#0077B5", '#636EFA', '#69C9D0'],  # Spotify en bleu, YouTube en violet, TikTok en turquoise
        line=dict(width=0.2, color='DarkSlateGrey')  # Bordures des barres
    )
)

# Mise en page et ajustements
fig.update_layout(
    xaxis_title_font_size=18,
    yaxis_title_font_size=18,
    xaxis_title="Plateformes",
    yaxis_title="Total des Streams",
    xaxis_tickangle=-45,  # Incline les noms des plateformes
    yaxis_tickformat='.0f',  # Format des nombres sur l'axe Y
    margin=dict(l=40, r=40, t=40, b=40),
    bargap=0.2,  # Ajuste l'espacement entre les barres
    width=600,  # Largeur du graphique
    height=400,  # Hauteur du graphique
    # Modifier le layout pour supprimer le fond
    plot_bgcolor="rgba(0,0,0,0)",  # Zone centrale transparente
    paper_bgcolor="rgba(0,0,0,0)"  # Fond global transparent


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
    color='track'  # Les couleurs seront différenciées par titre
    
)

# Ajustement du layout
fig2.update_traces(
    textinfo='percent+label',  # Affiche les pourcentages et le label
    hoverinfo='label+value+percent'  # Info au survol
)

fig2.update_layout(
    margin=dict(l=40, r=40, t=40, b=40),  # Marges du graphique
    width=600,  # Largeur du graphique
    height=400,
    plot_bgcolor="rgba(0,0,0,0)",  # Zone centrale transparente
    paper_bgcolor="rgba(0,0,0,0)"  # Fond global transparent
# Hauteur du graphique
)

# Affichage du graphique dans Streamlit
st.plotly_chart(fig2)

# Comparaison de la portée des playlists par plateforme


# Étape 1 : Calcul de la portée totale des playlists par plateforme
playlist_reach_comparison = df_filtered[
    ["spotify_playlist_reach", "youtube_playlist_reach", "deezer_playlist_reach"]
].sum()
st.write(f"Comparaison du nombre de playlists contenant les chansons")
# Étape 2 : Renommer les index pour des noms plus compréhensibles
playlist_reach_comparison.index = ["Portée Spotify", "Portée YouTube", "Portée Deezer"]

# Étape 3 : Création du graphque
fig_reach = px.bar(
    x=playlist_reach_comparison.index,  # Plateformes sur l'axe X
    y=playlist_reach_comparison.values,  # Portée totale sur l'axe Y
    labels={'x': 'Plateformes', 'y': 'Portée totale des playlists'}, # Étiquettes des axes
    text_auto=True,  # Affichei les valeurs directement sur les barres
    width=600,
    height=500
    
)

# Étape 4 : Personnalisation des couleurs et de l'apparence
fig_reach.update_traces(
    marker_color=["#0077B5", '#636EFA', '#FFD700'],  # Couleurs des barres
    width=0.2,  # Largeur des barres
    textfont_size=14,  # Taille du texte des valeurs
    textposition="outside"  # Position du texte des valeurs
)

# Personnalisation de la mise en page
fig_reach.update_layout(
     # Style du titre
    xaxis_title_font=dict(size=16),
    yaxis_title_font=dict(size=16),
    margin=dict(t=50, b=50, l=50, r=50),  # Ajuster les marges
    xaxis=dict(tickangle=45),  # Rotation des étiquettes sur l'axe X
    yaxis=dict(tickformat=".2s") ,
    plot_bgcolor="rgba(0,0,0,0)",  # Zone centrale transparente
    paper_bgcolor="rgba(0,0,0,0)"  # Fond global transparent
# Format des nombres sur l'axe Y
)

# Étape 5 : Affichage du graphique dans Streamlit
st.plotly_chart(fig_reach)

# Comparaison du nombre de playlists contenant les chansons
playlist_count_total = df_filtered[
    ["spotify_playlist_count", "apple_music_playlist_count", "deezer_playlist_count", "amazon_playlist_count"]
].sum()

# Dictionnaire pour renommer les plateformes
platform_labels = {
    "spotify_playlist_count": "Spotify playlist count",
    "apple_music_playlist_count": "Apple Music playlist count",
    "deezer_playlist_count": "Deezer playlist count",
    "amazon_playlist_count": "Amazon Music playlist count"
}
st.write(f"Répartition des playlists par plateforme de streaming")
# Renommer les index
playlist_count_total = playlist_count_total.rename(platform_labels)

# Création du graphique
fig_playlist_comparison = px.bar(
    x=playlist_count_total.index,
    y=playlist_count_total.values,
    labels={'x': 'Plateformes de streaming', 'y': 'Nombre de playlists contenant les chansons'},
    text_auto=True,
    width=600,  # Largeur du graphique
    height=400  # Hauteur du graphique
)
fig_playlist_comparison.update_layout(
     # Style du titre
    xaxis_title_font=dict(size=16),
    yaxis_title_font=dict(size=16),
    margin=dict(t=50, b=50, l=50, r=50),  # Ajuster les marges
    xaxis=dict(tickangle=45),  # Rotation des étiquettes sur l'axe X
    yaxis=dict(tickformat=".2s") ,
    plot_bgcolor="rgba(0,0,0,0)",  # Zone centrale transparente
    paper_bgcolor="rgba(0,0,0,0)"  )
# Afficher avec Streamlit
st.plotly_chart(fig_playlist_comparison)

# Calcul des ratios d'engagement
df_filtered["youtube_engagement"] = df_filtered["youtube_likes"] / df_filtered["youtube_views"]
df_filtered["tiktok_engagement"] = df_filtered["tiktok_likes"] / df_filtered["tiktok_views"]

# Moyenne par plateforme
engagement_metrics = df_filtered[["youtube_engagement", "tiktok_engagement"]].mean()
st.write(f"Engagement des utilisateurs sur YouTube vs TikTok")
# Création du graphique
fig_engagement = px.bar(
    x=engagement_metrics.index,
    y=engagement_metrics.values,
    labels={'x': 'Plateforme', 'y': 'Ratio Likes / Vues'},

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
 # Taille du titre
 # Centrer le titre
    xaxis_title="Plateforme",
    yaxis_title="Ratio Likes / Vues",
    yaxis=dict(
        tickformat=".1%"  # Format en pourcentage pour l'axe Y
    ),
    margin=dict(l=50, r=50, t=50, b=50),
    plot_bgcolor="rgba(0,0,0,0)",  # Zone centrale transparente
    paper_bgcolor="rgba(0,0,0,0)"# Ajustements des marges
)

# Afficher avec Streamlit
st.plotly_chart(fig_engagement)

# Calcul des streams totaux par artiste
top_artists = df_filtered.groupby("artist")[
    ["spotify_streams", "youtube_views", "tiktok_views", "shazam_counts"]
].sum().sum(axis=1).sort_values(ascending=False).head(10)
st.write(f"Top 10 des artistes les plus streamés",)
# Création du graphique
fig_top_artists = px.bar(
    x=top_artists.index,
    y=top_artists.values,
    labels={'x': 'Artistes', 'y': 'Total des streams'},
    text_auto=True,
    width=600,  # Largeur du graphique
    height=400  # Hauteur du graphique
)

# Ajustement de l'espacement entre les barres
fig_top_artists.update_layout(
    bargap=0.2 ,
    plot_bgcolor="rgba(0,0,0,0)",  # Zone centrale transparente
    paper_bgcolor="rgba(0,0,0,0)",# Espacement entre les barres (0.0 pour collées, 1.0 pour très espacées)
)

# Affichage du graphique avec Streamlit
st.plotly_chart(fig_top_artists)

# Grouper par année de sortie et calculer les streams totaux
df_filtered["release_year"] = df_filtered["release_date"].dt.year
streams_by_year = df_filtered.groupby("release_year")[
    ["spotify_streams", "youtube_views", "tiktok_views", "shazam_counts"]
].sum().reset_index()
st.write(f"Évolution du nombre de streams en fonction de l'année de sortie")
# Graphique interactif
fig_time_series = px.line(
    streams_by_year,
    x="release_year",
    y=["spotify_streams", "youtube_views", "tiktok_views", "shazam_counts"],
    labels={"release_year": "Année de sortie", "value": "Nombre total de streams"},
    width=600,  # Largeur du graphique
    height=400  
)
fig_time_series.update_layout(
    
    plot_bgcolor="rgba(0,0,0,0)",  # Zone centrale transparente
    paper_bgcolor="rgba(0,0,0,0)"# Espacement entre les barres (0.0 pour collées, 1.0 pour très espacées)
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
st.write(f"Répartition des écoutes par plateforme pour les chansons les plus populaires")
# Création du graphique en barres empilées
fig_stacked = px.bar(
    top_tracks_renamed, 
    x="track", 
    y=["Écoutes Spotify", "Vues YouTube", "Vues TikTok", "Identifications Shazam"],
    labels={"value": "Nombre d’écoutes", "track": "Titre du morceau"},
    barmode="stack",
    width=600,  # Largeur du graphique
    height=400  
)
fig_stacked.update_layout(
    
    plot_bgcolor="rgba(0,0,0,0)",  # Zone centrale transparente
    paper_bgcolor="rgba(0,0,0,0)"# Espacement entre les barres (0.0 pour collées, 1.0 pour très espacées)
)
# Affichage du graphique avec Streamlit
st.plotly_chart(fig_stacked)

