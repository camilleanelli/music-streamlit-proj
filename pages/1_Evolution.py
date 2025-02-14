import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend non interactif
import matplotlib.pyplot as plt
import matplotlib.offsetbox as offsetbox
from PIL import Image
from io import BytesIO
import plotly.express as px
import asyncio
import aiohttp
import base64
import time
from sqlalchemy import create_engine, text
import matplotlib.image as mpimg
import matplotlib.patches as patches
from datetime import datetime, timedelta

# Configuration Streamlit
st.session_state["_page"] = "Evolution"
st.set_page_config(layout="wide")

# Ajouter une image background depuis une URL en utilisant CSS 
st.markdown(
    f"""
    <style>
        /* Définition de l'animation pour le fond d'écran */
        @keyframes moveBackground {{
            0% {{
                background-position: 0% 0%;
            }}
            50% {{
                background-position: 100% 100%;
            }}
            100% {{
                background-position: 0% 0%;
            }}
        }}

        .stApp {{
            background-image: url("https://img.freepik.com/free-vector/wavy-colorful-background-style_23-2148497521.jpg");
            background-size: cover;
            background-position: 0% 0%;
            background-attachment: fixed;
            background-color: rgba(0,0,0, 0.5); /* Modifie entre 0.3 et 0.8 selon le niveau de transparence voulu */
            background-blend-mode: overlay; /* Fusionne l'image et la couleur */
            animation: moveBackground 40s ease-in-out infinite; /* Animation du fond avec une durée de 20 secondes et un mouvement infini */
        }}
    </style>
    """,
    unsafe_allow_html=True
)

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


def section_background(title):
    # Ajouter un fond gris aux métriques en utilisant CSS 
    st.markdown("""
        <style>
            .metric-container {
                display: flex;
                justify-content: space-between;
                align-items: stretch;
                margin-top: 10px;
            }
            .metric-box {
                background-color: #f0f2f6;
                padding: 10px;
                border-radius: 10px;
                text-align: center;
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
                height: 90%;
                min-height: 90px; /* Définit une hauteur minimale */
            }
            .metric-value {
                font-size: 20px;
                font-weight: bold;
                color: #0e1117;
            }
        </style>
        """, unsafe_allow_html=True)

if "current_week" not in st.session_state:
    st.session_state.current_week = 0
if "total_week" not in st.session_state:
    st.session_state.total_week = 0

# Conteneurs pour les metrics
semaine_actuelle = st.empty()
total_semaines = st.empty()

min_date = None
max_date = None

# Configuration de la base de données
if "DB_CONFIG" not in st.session_state:
    st.session_state.DB_CONFIG = {
        'user': 'postgres',
        'password': 'hWWCWtvKQODqEErOleTnHmTcuKWaRAgd',
        'host': 'monorail.proxy.rlwy.net',
        'port': '59179',
        'database': 'railway'
    }
        
if "engine" not in st.session_state:
    st.session_state.engine = create_engine(
        f"postgresql://{st.session_state.DB_CONFIG['user']}:"
        f"{st.session_state.DB_CONFIG['password']}@"
        f"{st.session_state.DB_CONFIG['host']}:"
        f"{st.session_state.DB_CONFIG['port']}/"
        f"{st.session_state.DB_CONFIG['database']}"
    )

if "Evolution" in st.session_state.get("_page", ""):
    # Ajout du titre principal du dashboard
    st.markdown("<h1 style='text-align: center; color: white;'> Evolution du charts Top 10 / Semaine</h1>", unsafe_allow_html=True)
    st.write('')
    
    @st.cache_data(show_spinner=False, hash_funcs={datetime: lambda x: x.timestamp()})
    def load_data(min_date, max_date):
        with st.session_state.engine.connect() as connection:
            result = connection.execute(text(f"""
                WITH ranked_data AS (
                    SELECT 
                        _year AS "Year",
                        CAST(_date AS DATE) AS "Date",
                        week AS "Week",
                        _rank AS "Rank",
                        title AS "Title",
                        cover AS "Cover",
                        artist AS "Artist",
                        ROW_NUMBER() OVER (PARTITION BY _year, week ORDER BY _rank ASC) AS rn
                    FROM billboard_ol
                    WHERE CAST(_date AS DATE) BETWEEN '{min_date}' AND '{max_date}'
                )
                SELECT * FROM ranked_data WHERE rn <= 10;
            """))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        return data

    # Récupération des dates min et max dans la base
    with st.session_state.engine.connect() as connection:
        limites = connection.execute(text("""
            SELECT MIN(_date) AS date_min, MAX(_date) AS date_max FROM billboard_ol
        """))
        row = limites.fetchone()
        if row and row[0] and row[1]:
            min_date = row[0]
            max_date = row[1]
            if isinstance(min_date, str):
                min_date = datetime.strptime(min_date, "%Y-%m-%d").date()
            if isinstance(max_date, str):
                max_date = datetime.strptime(max_date, "%Y-%m-%d").date()
            
            start_date_default = min_date
            end_date_default = max_date

            # Sélection de la plage de dates dans la sidebar
            date_range = st.sidebar.date_input(
                "Sélection de la plage de dates",
                (start_date_default, end_date_default),
                min_value=min_date,
                max_value=max_date
            )

            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
                if start_date > end_date:
                    st.error("La date de début ne peut pas être postérieure à la date de fin.")
                else:
                    st.cache_data.clear()
                    df = load_data(start_date, end_date)
                    # st.dataframe(df)  # débugger

                    # Conversion et tri chronologique
                    df['Date'] = pd.to_datetime(df['Date'])
                    df['Year'] = df['Date'].dt.year
                    df = df.sort_values(['Year', 'Week'])

                    # Récupération des semaines uniques
                    weeks = df[['Year', 'Week']].drop_duplicates().values
                    total_weeks = len(weeks)

                    # Préparation des classements et titres par semaine
                    rank_data = {}
                    titles_per_week = {}
                    for year, week in weeks:
                        week_data = df[(df['Year'] == year) & (df['Week'] == week)].sort_values('Rank')
                        rank_data[(year, week)] = {row['Title']: row['Rank'] for _, row in week_data.iterrows()}
                        titles_per_week[(year, week)] = set(week_data['Title'])

                    # --- Chargement asynchrone des images ---
                    async def load_image_async(session, url):
                        try:
                            async with session.get(url, timeout=5) as response:
                                content = await response.read()
                                img = Image.open(BytesIO(content)).convert("RGB")
                                # On ne redimensionne pas ici pour conserver la résolution pour le fond
                                return img
                        except Exception as e:
                            return None

                    async def load_images_async(df):
                        async with aiohttp.ClientSession() as session:
                            tasks = [load_image_async(session, url) for url in df['Cover']]
                            results = await asyncio.gather(*tasks)
                            cover_images = dict(zip(df['Title'], results))
                        return cover_images

                    cover_images = asyncio.run(load_images_async(df))
                    # Préparation d'une version basse résolution pour l'affichage dans le classement
                    cover_images_low = {
                        title: (img.resize((80, 80)) if img is not None else None)
                        for title, img in cover_images.items()
                    }

                    # --- Pré-calcul des images de fond par semaine ---
                    # Pour chaque semaine, on récupère l'image (haute résolution) associée au numéro 1.
                    # Si aucune image n'est disponible, on utilise une image par défaut.
                    background_images = {}
                    for (year, week) in weeks:
                        ranking_current = rank_data.get((year, week), {})
                        first_title = None
                        for title, rank in ranking_current.items():
                            if rank == 1:
                                first_title = title
                                break
                        if first_title is not None and first_title in cover_images and cover_images[first_title]:
                            background_images[(year, week)] = cover_images[first_title]
                        else:
                            background_images[(year, week)] = mpimg.imread("img/top10_2.jpg")

                    # --- Fonction utilitaire pour réaliser un fondu entre deux images ---
                    def blend_images(img1, img2, alpha):
                        """
                        Mélange deux images PIL avec un coefficient alpha (entre 0 et 1).
                        Si les images ne sont pas de même taille, la deuxième est redimensionnée.
                        """
                        if not isinstance(img1, Image.Image):
                            img1 = Image.fromarray(np.uint8(img1))
                        if not isinstance(img2, Image.Image):
                            img2 = Image.fromarray(np.uint8(img2))
                        if img1.size != img2.size:
                            img2 = img2.resize(img1.size)
                        return Image.blend(img1, img2, alpha)

                    # Fonction d'interpolation linéaire pour les positions
                    def interpolate_positions(start, end, alpha):
                        return start * (1 - alpha) + end * alpha

                    # --- Fonction de mise à jour d'une frame de l'animation ---
                    def update_frame(frame, ax):
                        """
                        Met à jour l'axe 'ax' pour une frame de l'animation.
                        L'image de fond correspond à un fondu entre le numéro 1 de la semaine courante
                        et celui de la semaine suivante.
                        """
                        ax.clear()
                        # Configuration de l'axe pour afficher tout le classement
                        ax.set_xlim(0, 1)
                        ax.set_ylim(0.5, 11.5)
                        ax.set_xticks([])
                        ax.set_yticks([])
                        ax.set_frame_on(False)
                        
                        # Calcul de l'indice de semaine et de la sous-frame
                        week_idx = frame // 40  # 40 frames par semaine
                        sub_frame = frame % 40

                        if week_idx < total_weeks - 1:
                            current_year, current_week = weeks[week_idx]
                            next_year, next_week = weeks[week_idx + 1]
                        else:
                            current_year, current_week = weeks[week_idx]
                            next_year, next_week = weeks[week_idx]

                        # Récupération de l'image de fond avec transition (fondu)
                        bg_current = background_images.get((current_year, current_week))
                        bg_next    = background_images.get((next_year, next_week))
                        if not isinstance(bg_current, Image.Image):
                            bg_current = Image.fromarray(np.uint8(bg_current))
                        if not isinstance(bg_next, Image.Image):
                            bg_next = Image.fromarray(np.uint8(bg_next))
                        if sub_frame < 20:
                            alpha_lin = sub_frame / 19.0
                            smooth_alpha = 1 / (1 + np.exp(-10 * (alpha_lin - 0.5)))
                            bg_blended = blend_images(bg_current, bg_next, smooth_alpha)
                            bg_img = np.asarray(bg_blended)
                        else:
                            bg_img = np.asarray(bg_next)
                        ax.imshow(bg_img, extent=[0, 1, 0.5, 11.5], aspect='auto', zorder=0, alpha=0.6)
                        
                        # --- Affichage des éléments du classement ---
                        if sub_frame < 20:
                            alpha = sub_frame / 19.0
                            smooth_alpha = 1 / (1 + np.exp(-10 * (alpha - 0.5)))
                            # Fusionner les titres des deux semaines
                            current_titles = titles_per_week.get((current_year, current_week), set())
                            next_titles = titles_per_week.get((next_year, next_week), set())
                            all_titles = list(current_titles.union(next_titles))
                            for title in all_titles:
                                current_rank = rank_data.get((current_year, current_week), {}).get(title, 12)
                                next_rank = rank_data.get((next_year, next_week), {}).get(title, 12)
                                
                                y_start = 11 - current_rank
                                y_end = 11 - next_rank
                                y_pos = interpolate_positions(y_start, y_end, smooth_alpha)
                                rank = int(round(interpolate_positions(current_rank, next_rank, smooth_alpha)))
                                artist = df[df['Title'] == title]['Artist'].values[0] if title in df['Title'].values else "Inconnu"
                                ax.text(0.3, y_pos + 0.7, f"{rank}. {title}", ha='left', fontsize=15, fontweight='bold')
                                ax.text(0.3, y_pos + 0.5, artist, ha='left', fontsize=15)
                                
                                # Choix de l'image de flèche
                                if current_rank < next_rank:
                                    image_path = "img/Red-Down-Arrow.png"
                                elif current_rank > next_rank:
                                    image_path = "img/Green-Up-Arrow.png"
                                else:
                                    image_path = "img/No-Arrow.png"
                                try:
                                    img_arrow = Image.open(image_path).convert("RGBA")
                                    background_arrow = Image.new("RGBA", img_arrow.size, (255, 255, 255, 255))
                                    img_arrow = Image.alpha_composite(background_arrow, img_arrow).convert("RGB")
                                except Exception as e:
                                    img_arrow = None
                                
                                if title in cover_images_low and cover_images_low[title]:
                                    image_box = offsetbox.AnnotationBbox(
                                        offsetbox.OffsetImage(cover_images_low[title], zoom=0.8),
                                        (0.1, y_pos +0.7), frameon=False
                                    )
                                    ax.add_artist(image_box)
                                if img_arrow:
                                    fleche = offsetbox.AnnotationBbox(
                                        offsetbox.OffsetImage(img_arrow, zoom=0.1),
                                        (0.2, y_pos + 0.7), frameon=False
                                    )
                                    ax.add_artist(fleche)
                        else:
                            # Affichage pour la semaine suivante
                            next_titles = titles_per_week.get((next_year, next_week), set())
                            for title in next_titles:
                                rank = rank_data.get((next_year, next_week), {}).get(title, 12)
                                y_pos = 11 - rank
                                artist = df[df['Title'] == title]['Artist'].values[0] if title in df['Title'].values else "Inconnu"
                                ax.text(0.3, y_pos + 0.7, f"{rank}. {title}", ha='left', fontsize=15, fontweight='bold')
                                ax.text(0.3, y_pos + 0.5, artist, ha='left', fontsize=15)

                                if title in cover_images_low and cover_images_low[title]:
                                    image_box = offsetbox.AnnotationBbox(
                                        offsetbox.OffsetImage(cover_images_low[title], zoom=0.8),
                                        (0.1, y_pos + 0.7), frameon=False
                                    )
                                    ax.add_artist(image_box)
                                previous_rank = rank_data.get((current_year, current_week), {}).get(title, 12)
                                if previous_rank < rank:
                                    image_path = "img/Red-Down-Arrow.png"
                                elif previous_rank > rank:
                                    image_path = "img/Green-Up-Arrow.png"
                                else:
                                    image_path = "img/No-Arrow.png"
                                try:
                                    img_arrow = Image.open(image_path).convert("RGBA")
                                    background_arrow = Image.new("RGBA", img_arrow.size, (255, 255, 255, 255))
                                    img_arrow = Image.alpha_composite(background_arrow, img_arrow).convert("RGB")
                                except Exception as e:
                                    img_arrow = None
                                if img_arrow:
                                    fleche = offsetbox.AnnotationBbox(
                                        offsetbox.OffsetImage(img_arrow, zoom=0.1),
                                        (0.2, y_pos + 0.7), frameon=False
                                    )
                                    ax.add_artist(fleche)
                        # Fin affichage des éléments

                    # --- Fonction pour dessiner et encoder une frame ---
                    def draw_frame(frame):
                        fig, ax = plt.subplots(figsize=(10, 13))
                        ax.set_position([0, 0, 1, 1])
                        update_frame(frame, ax)
                        buf = BytesIO()
                        fig.savefig(buf, format="png")
                        plt.close(fig)
                        buf.seek(0)
                        encoded = base64.b64encode(buf.read()).decode("ascii")
                        return f"data:image/png;base64,{encoded}"

                    # graph plotly
                    col1, col2, col3, col4 = st.columns([4, 1, 4, 1])
                    with col3:    
                        artist_counts = df['Artist'].value_counts().reset_index()
                        artist_counts.columns = ['Artist', 'Count']
                        top_artists = artist_counts.head(10)
                        fig_bar = px.bar(
                            top_artists,
                            x='Count',
                            y='Artist',
                            orientation='h',
                            title=f"Nombre d'apparition sur la période<br>du {start_date.strftime("%d-%m-%Y")} au {end_date.strftime("%d-%m-%Y")}",  # Dates formatées
                            category_orders={'Artist': top_artists['Artist'].tolist()}
                        )
                        fig_bar.update_layout(
                            xaxis_title=None,
                            yaxis_title=None,
                            plot_bgcolor="rgba(0,0,0,0)",  
                            paper_bgcolor="rgba(0,0,0,0)",  
                            width=800, 
                            height=700,
                            title_font=dict(size=24), 
                            xaxis_title_font=dict(size=18),  
                            yaxis_title_font=dict(size=18),  
                            font=dict(size=14),
                            title_x=0.3,
                            title_xanchor='left'
                        )
                        st.plotly_chart(fig_bar)
                    
                    # classement 
                    with col1:
                        image_container = st.empty()
                        total_frames = total_weeks * 40  # 40 frames par semaine
                        frame = 0
                        while True:
                            frame_to_draw = frame % total_frames
                            img = draw_frame(frame_to_draw)
                            image_container.image(img)
                            time.sleep(0.02)  # Intervalle entre les frames (20ms)
                            frame += 1
            else:
                st.info("Sélectionner une plage de dates.")
