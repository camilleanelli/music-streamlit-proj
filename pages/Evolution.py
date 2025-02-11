import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend non interactif
import matplotlib.pyplot as plt
import matplotlib.offsetbox as offsetbox
from PIL import Image
from io import BytesIO
import asyncio
import aiohttp
import base64
import time
from sqlalchemy import create_engine, text
import matplotlib.patches as patches

DB_CONFIG = {
    'user': 'postgres',
    'password': 'hWWCWtvKQODqEErOleTnHmTcuKWaRAgd',
    'host': 'monorail.proxy.rlwy.net',
    'port': '59179',
    'database': 'railway'
}

# Création de la connexion
engine = create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")


# 🎚️ **Ajout du slider pour choisir la plage de semaines**
weeks_range = st.slider("Sélectionnez la plage de semaines :", 1, 52, (2, 10))

# 🛠️ **Conversion des semaines en plage de dates SQL**
min_weeks, max_weeks = weeks_range
min_date = f"CURRENT_DATE - INTERVAL '{max_weeks} week'"
max_date = f"CURRENT_DATE - INTERVAL '{min_weeks} week'"

# 🏷️ Affichage de la sélection utilisateur
st.write(f"📅 Affichage des chansons entre `{max_weeks}` et `{min_weeks}` semaines en arrière.")

# 📥 **Chargement des données avec filtre dynamique**
@st.cache_data
def load_data(min_date, max_date):
    with engine.connect() as connection:
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
                WHERE CAST(_date AS DATE) BETWEEN {min_date} AND {max_date} -- 🔍 Utilisation des filtres dynamiques
            )
            SELECT * FROM ranked_data WHERE rn <= 10;
        """))
        data = pd.DataFrame(result.fetchall(), columns=result.keys())
    return data

# 📊 **Chargement des données et affichage**
df = load_data(min_date, max_date)
st.write("🎶 **Top 10 des chansons dans la plage sélectionnée** 🎶")
st.dataframe(df)



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

# --- Chargement asynchrone des images de couverture ---

async def load_image_async(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            content = await response.read()
            img = Image.open(BytesIO(content))
            return img.resize((80, 80))
    except Exception as e:
        return None

async def load_images_async(df):
    async with aiohttp.ClientSession() as session:
        tasks = [load_image_async(session, url) for url in df['Cover']]
        results = await asyncio.gather(*tasks)
        cover_images = dict(zip(df['Title'], results))
    return cover_images

cover_images = asyncio.run(load_images_async(df))

# --- Fonctions d'interpolation et d'animation ---

def interpolate_positions(start, end, alpha):
    """Interpolation linéaire entre deux positions."""
    return start * (1 - alpha) + end * alpha

import matplotlib.patches as patches

# Calculer ces dates une seule fois (après le chargement et tri des données)
start_date_str = df['Date'].min().strftime("%d/%m/%Y")
end_date_str   = df['Date'].max().strftime("%d/%m/%Y")

import matplotlib.patches as patches

def update_frame(frame, ax):
    """
    Met à jour l'axe 'ax' en dessinant la frame correspondant à l'animation.
    On ajoute une barre de progression chronologique indiquant
    quelle semaine est en cours par rapport à la première et à la dernière date.
    """
    ax.clear()
    
    # Configuration de l'axe (on travaille en coordonnées de données pour l'animation)
    ax.set_xlim(0, 1)
    ax.set_ylim(1, 11)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    
    # Calcul de l'indice de semaine et de la sous-frame (sub_frame inutilisée)
    week_idx = frame // 40  # 40 frames par semaine
    # On n'utilise plus sub_frame pour l'interpolation
    sub_frame = frame % 40

    # La progression n'avance que lorsque la semaine change
    progress_global = week_idx / total_weeks

    if week_idx < total_weeks - 1:
        current_year, current_week = weeks[week_idx]
        next_year, next_week = weeks[week_idx + 1]
    else:
        current_year, current_week = weeks[week_idx]
        next_year, next_week = weeks[week_idx]

    current_titles = titles_per_week.get((current_year, current_week), set())
    next_titles = titles_per_week.get((next_year, next_week), set())
    all_titles = list(current_titles.union(next_titles))

    # --- Barre de progression chronologique ---
    # Coordonnées normalisées pour la barre
    bar_x = 0.05    # 5% depuis la gauche
    bar_y = 0.97    # 97% en hauteur (en haut du graphique)
    bar_width = 0.9 # 90% de la largeur
    bar_height = 0.03  # hauteur de la barre

    # Fond de la barre (gris clair)
    ax.add_patch(patches.Rectangle((bar_x, bar_y), bar_width, bar_height,
                                   transform=ax.transAxes,
                                   color="lightgray", zorder=10))
    # Portion remplie (bleu) selon la progression (uniquement en fonction de la semaine)
    ax.add_patch(patches.Rectangle((bar_x, bar_y), bar_width * progress_global, bar_height,
                                   transform=ax.transAxes,
                                   color="blue", zorder=11))
    # Texte indiquant la semaine en cours
    progress_text = f"Semaine {week_idx + 1} sur {total_weeks}   ({start_date_str} → {end_date_str})"
    ax.text(0.5, bar_y + bar_height/2, progress_text,
            transform=ax.transAxes,
            ha="center", va="center", color="white", fontsize=12, zorder=12)
    # --- Fin barre de progression ---


    # Partie d'animation : affichage des titres, artistes, images, flèches, etc.
    if sub_frame < 20:
        alpha = sub_frame / 19.0
        smooth_alpha = 1 / (1 + np.exp(-10 * (alpha - 0.5)))
        for title in all_titles:
            current_rank = rank_data.get((current_year, current_week), {}).get(title, 12)
            next_rank = rank_data.get((next_year, next_week), {}).get(title, 12)
            
            y_start = 11 - current_rank
            y_end = 11 - next_rank
            y_pos = interpolate_positions(y_start, y_end, smooth_alpha)
            rank = int(round(interpolate_positions(current_rank, next_rank, smooth_alpha)))
            artist = df[df['Title'] == title]['Artist'].values[0] if title in df['Title'].values else "Inconnu"
            ax.text(0.3, y_pos + 0.2, f"{rank}. {title}", ha='left', fontsize=12, fontweight='bold')
            ax.text(0.3, y_pos, artist, ha='left', fontsize=12)
            
            if current_rank < next_rank:
                image_path = "img/Red-Down-Arrow.png"
            elif current_rank > next_rank:
                image_path = "img/Green-Up-Arrow.png"
            else:
                image_path = "img/No-Arrow.png"
            try:
                img_arrow = Image.open(image_path).convert("RGBA")
                background = Image.new("RGBA", img_arrow.size, (255, 255, 255, 255))
                img_arrow = Image.alpha_composite(background, img_arrow).convert("RGB")
            except Exception as e:
                img_arrow = None

            if title in cover_images and cover_images[title]:
                image_box = offsetbox.AnnotationBbox(
                    offsetbox.OffsetImage(cover_images[title], zoom=0.8), (0.1, y_pos), frameon=False
                )
                ax.add_artist(image_box)
            if img_arrow:
                fleche = offsetbox.AnnotationBbox(
                    offsetbox.OffsetImage(img_arrow, zoom=0.1), (0.2, y_pos), frameon=False
                )
                ax.add_artist(fleche)
    else:
        for title in next_titles:
            rank = rank_data.get((next_year, next_week), {}).get(title, 12)
            y_pos = 11 - rank
            artist = df[df['Title'] == title]['Artist'].values[0] if title in df['Title'].values else "Inconnu"
            ax.text(0.3, y_pos + 0.2, f"{rank}. {title}", ha='left', fontsize=12, fontweight='bold')
            ax.text(0.3, y_pos, artist, ha='left', fontsize=12)
            if title in cover_images and cover_images[title]:
                image_box = offsetbox.AnnotationBbox(
                    offsetbox.OffsetImage(cover_images[title], zoom=0.8), (0.1, y_pos), frameon=False
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
                background = Image.new("RGBA", img_arrow.size, (255, 255, 255, 255))
                img_arrow = Image.alpha_composite(background, img_arrow).convert("RGB")
            except Exception as e:
                img_arrow = None
            if img_arrow:
                fleche = offsetbox.AnnotationBbox(
                    offsetbox.OffsetImage(img_arrow, zoom=0.1), (0.2, y_pos), frameon=False
                )
                ax.add_artist(fleche)
    
    # ax.set_title(f"Classement - Année {next_year}, Semaine {next_week}", fontsize=14)

def draw_frame(frame):
    """
    Crée une figure matplotlib pour la frame donnée,
    appelle update_frame pour la dessiner, puis renvoie l'image encodée en base64.
    """
    fig, ax = plt.subplots(figsize=(10, 13))
    update_frame(frame, ax)
    
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

# --- Affichage dans Streamlit ---

st.title("Animation du classement musical")

# Conteneur pour l'image
image_container = st.empty()

# Nombre total de frames pour l'animation (40 frames par semaine)
total_frames = total_weeks * 40
frame = 0

# Boucle d'animation
while True:
    frame_to_draw = frame % total_frames
    img = draw_frame(frame_to_draw)
    image_container.image(img, use_container_width=False)

    time.sleep(0.08)  # Intervalle entre les frames (80ms)
    frame += 1



