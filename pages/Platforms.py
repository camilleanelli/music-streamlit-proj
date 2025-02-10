import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns

# 1️⃣ Connexion à la base PostgreSQL
conn = psycopg2.connect(
    dbname="my_pg_db",
    user="my_user",
    password="my_password",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Configuration de la page Streamlit
st.set_page_config(page_title="Dashboard", page_icon="🎤", layout="wide")
st.header("🎵 Analyse et Comparaison des Plateformes Musicales : Tendances et Insights 🎧")

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

# 4️⃣ Filtrage par date de sortie
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
# Sélection de l'album
album_list = df_filtered["album_name"].unique()
selected_album = st.sidebar.selectbox("Sélectionner un album", ["Tous"] + list(album_list))

# Filtrer les données selon l'album sélectionné
if selected_album != "Tous":
    df_filtered = df_filtered[df_filtered["album_name"] == selected_album]

# 📊 Graphique : Nombre de vues par plateforme
if selected_album != "Tous":
    platform_views = {
        "Spotify Streams": df_filtered["spotify_streams"].sum(),
        "YouTube Views": df_filtered["youtube_views"].sum(),
        "TikTok Views": df_filtered["tiktok_views"].sum(),
        "Apple Music Playlists": df_filtered["apple_music_playlist_count"].sum(),
        "Deezer Playlists": df_filtered["deezer_playlist_count"].sum(),
        "Amazon Playlists": df_filtered["amazon_playlist_count"].sum(),
        "Shazam Counts": df_filtered["shazam_counts"].sum(),
    }

    # Création du DataFrame pour le graphique
    df_platform = pd.DataFrame(list(platform_views.items()), columns=["Plateforme", "Nombre de vues"])

    # Graphique en barres du nombre de vues par plateforme
    fig_platform = px.bar(
        df_platform, 
        x="Plateforme", 
        y="Nombre de vues",
        title=f"Nombre de vues par plateforme pour l'album : {selected_album}",
        color="Nombre de vues", 
        color_continuous_scale="blues",
        template="plotly_white"
    )
    st.plotly_chart(fig_platform, use_container_width=True)

# 📊 Comparaison des plateformes
platform_summary = {
    "Spotify": df_filtered["spotify_streams"].sum(),
    "YouTube": df_filtered["youtube_views"].sum(),
    "TikTok": df_filtered["tiktok_views"].sum(),
    "Apple Music": df_filtered["apple_music_playlist_count"].sum(),
    "Deezer": df_filtered["deezer_playlist_count"].sum(),
    "Amazon": df_filtered["amazon_playlist_count"].sum(),
    "Shazam": df_filtered["shazam_counts"].sum(),
}

# Création du DataFrame pour la comparaison des plateformes
df_summary = pd.DataFrame(list(platform_summary.items()), columns=["Plateforme", "Total Interactions"])

# Graphique en barres horizontales pour comparer les plateformes
fig_bar = px.bar(
    df_summary, 
    x="Total Interactions", 
    y="Plateforme", 
    orientation="h",
    title="<b>Comparaison des plateformes musicales</b>",
    color="Total Interactions", 
    color_continuous_scale="blues",
    template="plotly_white"
)

st.plotly_chart(fig_bar, use_container_width=True)



# 6️⃣ Graphiques des top artistes et albums les plus streamés sur Spotify
artist_streams = df_filtered.groupby("artist")["spotify_streams"].sum().nlargest(10)
top_albums = df_filtered.groupby("album_name")["spotify_streams"].sum().nlargest(10)

# Création des graphiques côte à côte
left, right = st.columns(2)

with left:
    fig_artist = px.pie(
        artist_streams, 
        names=artist_streams.index, 
        values=artist_streams.values, 
        title="Top 10 artistes les plus streamés sur Spotify"
    )
    st.plotly_chart(fig_artist)

with right:
    fig_albums = px.pie(
        top_albums, 
        names=top_albums.index, 
        values=top_albums.values, 
        title="Top 10 albums les plus streamés sur Spotify"
    )
    st.plotly_chart(fig_albums)

# 7️⃣ Graphique de l'évolution des albums par an
df_filtered["year"] = df_filtered["release_date"].dt.year
album_per_year = df_filtered.groupby("year")["album_name"].count()

fig_years = px.line(
    album_per_year, 
    x=album_per_year.index, 
    y=album_per_year.values, 
    title="Évolution du nombre d'albums sortis par an",
    labels={"x": "Année", "y": "Nombre d'albums"}
)
st.plotly_chart(fig_years)

# Top 10 tracks les plus populaires sur Spotify
top_tracks_spotify = df_filtered.groupby("track")["spotify_streams"].sum().nlargest(10)

# Top 10 tracks les plus populaires sur YouTube
top_tracks_youtube = df_filtered.groupby("track")["youtube_views"].sum().nlargest(10)

# Affichage côte à côte
col1, col2 = st.columns(2)

with col1:
    fig_spotify_top = px.bar(
        top_tracks_spotify, 
        x=top_tracks_spotify.values, 
        y=top_tracks_spotify.index, 
        orientation="h",
        title="Top 10 des morceaux les plus streamés sur Spotify",
        labels={"x": "Nombre de Streams", "y": "Morceaux"},
        color=top_tracks_spotify.values,  # Utiliser les valeurs pour l'intensité de la couleur
        color_continuous_scale="Viridis"  # Dégradé de couleurs
    )
    st.plotly_chart(fig_spotify_top)

with col2:
    fig_youtube_top = px.bar(
        top_tracks_youtube, 
        x=top_tracks_youtube.values, 
        y=top_tracks_youtube.index, 
        orientation="h",
        title="Top 10 des morceaux les plus visionnés sur YouTube",
        labels={"x": "Nombre de Vues", "y": "Morceaux"},
        color=top_tracks_youtube.values,  # Utiliser les valeurs pour l'intensité de la couleur
        color_continuous_scale="Inferno"  # Dégradé de couleurs
    )
    st.plotly_chart(fig_youtube_top)

fig = px.box(df_filtered, 
             x='album_name', 
             y='track_score', 
             title='Distribution du Track Score par Album',
             labels={'album_name': 'Album Name', 'track_score': 'Track Score'},
             points='all')  
fig.update_xaxes(tickangle=45)
st.plotly_chart(fig)
# Box plot de la popularité Spotify par rapport au nombre de playlists sur Deezer
fig = px.box(
    df, 
    x='deezer_playlist_count', 
    y='spotify_popularity', 
    title='Distribution de la popularité Spotify par rapport aux playlists Deezer',
    labels={'deezer_playlist_count': 'Nombre de playlists Deezer', 'spotify_popularity': 'Popularité Spotify'},
    points='all'  # Affiche tous les points pour une meilleure visibilité
)

# Affichage du graphique
fig.show()

