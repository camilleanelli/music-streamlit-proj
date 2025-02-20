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

st.set_page_config(
    page_title="Plateforme",
    page_icon="🎧",
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
    </style>
    """,
    unsafe_allow_html=True
)


# Ajout du titre principal du dashboard
st.markdown("<h1 style='text-align: center; color: white;'> Analyse des services de streaming </h1>", unsafe_allow_html=True)


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

# Sidebar - Filtres
st.sidebar.header("Filtres")

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

# 5️⃣ Filtrage par artiste
artist_list = df_filtered["artist"].unique()
selected_artist = st.sidebar.selectbox("Artiste", ["Tous"] + list(artist_list))

if selected_artist != "Tous":
    df_filtered = df_filtered[df_filtered["artist"] == selected_artist]

# 6️⃣ Filtrage par album
album_list = df_filtered["album_name"].unique()
selected_album = st.sidebar.selectbox("Album", ["Tous"] + list(album_list))

if selected_album != "Tous":
    df_filtered = df_filtered[df_filtered["album_name"] == selected_album]

    
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
st.subheader(f"_Comparaison des plateformes de Streaming_")
# Création du graphique
def format_large_number(num):
    if num >= 1_000_000_000:  # Milliards
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:  # Millions
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:  # Milliers
        return f"{num / 1_000:.1f}K"
    return f"{num:.0f}"  # Valeurs normales sans décimales

# 🟢 Appliquer la fonction sur les valeurs de texte
formatted_text = [format_large_number(val) for val in platform_comparaison.values]

# Création du graphique
fig = px.bar(
    x=platform_comparaison.index,  
    y=platform_comparaison.values,  # Valeurs d'origine sur l'axe Y
    labels={'x': 'Plateformes', 'y': 'Total des Streams'},  
    text=formatted_text,  # Texte dynamique affiché sur les barres
    template='plotly_dark'
)

# Personnalisation des couleurs et affichage des valeurs
fig.update_traces(
    textposition='outside',  # Texte au sommet des barres
    texttemplate='%{text}',  # Utilisation des valeurs préformatées
    marker=dict(
        color=["#0077B5", '#636EFA', '#69C9D0'],
        line=dict(width=0.2, color='DarkSlateGrey')
    )
)

# Mise en page et ajustements
fig.update_layout(
    xaxis_title="Plateformes",
    yaxis=dict(
        title="Total des Streams",
        tickformat="~s"  # Format automatique avec K, M, B
    ),
    plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
    paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
    legend=dict(
        bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
        font=dict(color="white")  # Texte blanc pour la lisibilité
       ),
        margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
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
st.subheader(f"_Top 10 des Titres pour {platform_choice}_")
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
    plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
    paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
    legend=dict(
        bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
        font=dict(color="white")  # Texte blanc pour la lisibilité
       ),
        margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
    )
# Affichage du graphique dans Streamlit
st.plotly_chart(fig2)

st.divider()
col1, col2 = st.columns(2)

with col1:
    # Comparaison de la portée des playlists par plateforme
    # Étape 1 : Calcul de la portée totale des playlists par plateforme
    playlist_reach_comparison = df_filtered[
        ["spotify_playlist_reach", "youtube_playlist_reach", "deezer_playlist_reach"]
    ].sum()
    st.subheader(f"_Nombre de playlists contenant les chansons_")
    # Étape 2 : Renommer les index pour des noms plus compréhensibles
    playlist_reach_comparison.index = ["Portée Spotify", "Portée YouTube", "Portée Deezer"]

    # Étape 3 : Création du graphque
    fig_reach = px.bar(
        x=playlist_reach_comparison.index,  # Plateformes sur l'axe X
        y=playlist_reach_comparison.values,  # Portée totale sur l'axe Y
        labels={'x': 'Plateformes', 'y': 'Portée totale des playlists'}, # Étiquettes des axes
        text_auto=True,  # Affichei les valeurs directement sur les barres
        width=600,  # Largeur du graphique 
        height=500  # Hauteur du graphique
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
        yaxis=dict(tickformat=".2s") ,
        plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
        paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
        legend=dict(
            bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
            font=dict(color="white")  # Texte blanc pour la lisibilité
        ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
        )
    # Afficher avec Streamlit
    st.plotly_chart(fig_reach)

with col2:
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
    st.subheader(f"_Nombre de playlists par plateforme_")
    # Renommer les index
    playlist_count_total = playlist_count_total.rename(platform_labels)

    # Création du graphique
    fig_playlist_comparison = px.bar(
        x=playlist_count_total.index,
        y=playlist_count_total.values,
        labels={'x': 'Plateformes de streaming', 'y': 'Nombre de playlists contenant les chansons'},
        text_auto=True,
        width=600,  # Largeur du graphique
        height=500  # Hauteur du graphique
        )

    # Personnalisation de la mise en page
    fig_playlist_comparison.update_layout(
        yaxis=dict(tickformat=".2s") ,
        plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
        paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
        legend=dict(
            bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
            font=dict(color="white")  # Texte blanc pour la lisibilité
        ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
        )
    # Afficher avec Streamlit
    st.plotly_chart(fig_playlist_comparison)


col1, col2 = st.columns(2)

st.divider()
with col1:
    # Calcul des ratios d'engagement
    df_filtered["youtube_engagement"] = df_filtered["youtube_likes"] / df_filtered["youtube_views"]
    df_filtered["tiktok_engagement"] = df_filtered["tiktok_likes"] / df_filtered["tiktok_views"]

    # Moyenne par plateforme
    engagement_metrics = df_filtered[["youtube_engagement", "tiktok_engagement"]].mean()
    st.subheader(f"_Engagement sur YouTube vs TikTok_")
    # Création du graphique
    fig_engagement = px.bar(
        x=engagement_metrics.index,
        y=engagement_metrics.values,
        labels={'x': 'Plateforme', 'y': 'Ratio Likes / Vues'},
        text_auto=True,
        width=600,  # Largeur du graphique
        height=500  # Hauteur du graphique
        )

    # Personnalisation de la mise en page
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
        plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
        paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
        legend=dict(
            bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
            font=dict(color="white")  # Texte blanc pour la lisibilité
        ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
        )
    # Afficher avec Streamlit
    st.plotly_chart(fig_engagement)

with col2:
    # Calcul des streams totaux par artiste
    top_artists = df_filtered.groupby("artist")[
        ["spotify_streams", "youtube_views", "tiktok_views", "shazam_counts"]
    ].sum().sum(axis=1).sort_values(ascending=False).head(10)

    # Appliquer la fonction de mise à l'échelle aux valeurs affichées
    formatted_text = [format_large_number(val) for val in top_artists.values]

    # Création du graphique
    fig_top_artists = px.bar(
        x=top_artists.index,
        y=top_artists.values,  # Valeurs originales sur l'axe Y
        labels={'x': 'Artistes', 'y': 'Total des streams'},
        text=formatted_text,  # Texte mis à l'échelle affiché sur les barres
        width=600,  # Largeur du graphique
        height=500  # Hauteur du graphique
    )

    # Ajustement des styles
    fig_top_artists.update_traces(
        textposition='outside',  # Affichage du texte au-dessus des barres
        texttemplate='%{text}',  # Utilisation des valeurs formatées
        marker=dict(color='#636EFA', line=dict(width=0.2, color='DarkSlateGrey')) # Couleur des barres
    )
    st.subheader(f"_Les artistes les plus streamés sur les plateformes_")

    # Ajustement de l'espacement et des axes
    fig_top_artists.update_layout(
        bargap=0.2,  # Espacement entre les barres
        yaxis=dict(
            title="Total des Streams",
            tickformat="~s"  # Format automatique (K, M, B) pour les ticks de l'axe Y
        ),
        xaxis_tickangle=-45,  # Inclinaison des noms d'artistes pour lisibilité
        plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
        paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
        legend=dict(
            bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
            font=dict(color="white")  # Texte blanc pour la lisibilité
        ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
        )
    st.plotly_chart(fig_top_artists)

col1, col2 = st.columns(2)

# Grouper par année de sortie et calculer les streams totaux
with col1:
    df_filtered["release_year"] = df_filtered["release_date"].dt.year
    streams_by_year = df_filtered.groupby("release_year")[
        ["spotify_streams", "youtube_views", "tiktok_views", "shazam_counts"]
    ].sum().reset_index()
    st.subheader(f"_Évolution du nombre de streams en fonction de l'année de sortie_")
    # Graphique interactif
    fig_time_series = px.line(
        streams_by_year,
        x="release_year",
        y=["spotify_streams", "youtube_views", "tiktok_views", "shazam_counts"],
        labels={"release_year": "Année de sortie", "value": "Nombre total de streams"},
        width=600,  # Largeur du graphique
        height=500  # Hauteur du graphique
    )
    fig_time_series.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
        paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
        legend=dict(
            bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
            font=dict(color="white")  # Texte blanc pour la lisibilité
        ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
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

with col2:    
    st.subheader(f"_Répartition des écoutes par plateforme pour les chansons les plus populaires_")
    # Création du graphique en barres empilées
    fig_stacked = px.bar(
        top_tracks_renamed, 
        x="track", 
        y=["Écoutes Spotify", "Vues YouTube", "Vues TikTok", "Identifications Shazam"],
        labels={"value": "Nombre d'écoutes", "track": "Titre du morceau"},
        barmode="stack",
        width=600,  # Largeur du graphique
        height=500  # Hauteur du graphique
    )
    fig_stacked.update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
        paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
        legend=dict(
            bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
            font=dict(color="white")  # Texte blanc pour la lisibilité
        ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
        )
    # Affichage du graphique avec Streamlit
    st.plotly_chart(fig_stacked)

