import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine, text
import pandas as pd

# Configuration de la page
st.session_state["_page"] = "Home"
st.set_page_config(
    page_title="Music Data Insights",
    page_icon="🎶",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Configuration de l'image de fond et de l'animation
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


# Configuration de la sidebar
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


# Configuration du Titre principal du dashboard et des icons animés
st.markdown(
    """
    <style>
        /* Animation pour les images autour du Titre */
        @keyframes rotateImages {
            0% { transform: rotate(0deg); }
            50% { transform: rotate(360deg); }
            100% { transform: rotate(0deg); }
        }

        /* Classe pour appliquer l'animation au Titre */
        .animated-music {
            display: inline-block;
            font-weight: bold;
            font-size: 50px;
            animation: vibration 0.5s linear infinite; /* Animation rapide en boucle infinie */
        }

        /* Classe pour les images autour du Titre */
        .music-icon {
            width: 40px;
            height: 40px;
            animation: rotateImages 4s linear infinite; /* Animation de rotation */
            margin: 0 15px; /* Espacement entre les icônes */
            filter: drop-shadow(0 0 15px rgba(255, 99, 71, 0.8)); /* Lueur autour des icônes */
        }

        /* Centrer le titre et les images */
        .title-container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: row;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Ajouter le titre avec le mot "Music Data Insights" et les icônes autour
st.markdown(
    """
    <div class="title-container">
        <img src="https://img.icons8.com/ios-filled/50/ffffff/guitar.png" class="music-icon" />
        <img src="https://img.icons8.com/ios-filled/50/ffffff/saxophone.png" class="music-icon" />
        <img src="https://img.icons8.com/ios-filled/50/ffffff/music.png" class="music-icon" style="margin-right: 10%" />
        <h1 style="text-align: center; color: white;">
           <span class="animated-music">Music Data Insights</span>
        </h1>
        <img src="https://img.icons8.com/ios-filled/50/ffffff/music.png" class="music-icon" />
        <img src="https://img.icons8.com/ios-filled/50/ffffff/saxophone.png" class="music-icon" />
        <img src="https://img.icons8.com/ios-filled/50/ffffff/guitar.png" class="music-icon" />
    </div>
    """,
    unsafe_allow_html=True
)
       

# Configuration CSS harmonisé pour toute l'application
st.markdown("""
    <style>
    /* Style des cartes */
    .custom-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
        color: #0e1117;
    }
    .custom-card h1, 
    .custom-card h2, 
    .custom-card h3,
    .custom-card strong {
    color: #431543
    }
            
    .custom-card:hover {
        transform: translateY(-2px);
        color: #0e1117;
    }
    
    /* Style des boutons Streamlit */
    .stButton button {
        width: 100%;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 1rem 2rem;
        transition: all 0.2s ease;
        color: #0e1117;
    }
    .stButton button:hover {
        background-color: #7A577A;;
        transform: translateY(-2px);
        color: #0e1117
    }
    
    /* Style des métriques */
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        color: #0e1117                
    }
    
    /* Style du ticker */
    .ticker-container {
        background-color: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(5px);
        position: sticky;
        top: 0;
        z-index: 100;
        color: #0e1117;
    }
    
    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        color: #0e1117
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
    }
    </style>
""", unsafe_allow_html=True)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="custom-card">
            <h3>📈 Évolution</h3>
            <p>Suivez en temps réel les titres les plus populaires de la semaine. Découvrez l'évolution des classements et identifiez les morceaux qui dominent les plateformes de streaming.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Accéder à l'Évolution", key="btn_evolution", use_container_width=True):
        st.switch_page("pages/1_Evolution.py")

with col2:
    st.markdown("""
        <div class="custom-card">
            <h3>🌍 Monde </h3>
            <p>Explorez les artistes et chansons les plus écoutés à travers le monde. Comparez les tendances musicales par pays et observez les dynamiques culturelles du marché global.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Accéder au Monde", key="btn_monde", use_container_width=True):
        st.switch_page("pages/2_world.py")

with col3:
    st.markdown("""
        <div class="custom-card">
            <h3>🎧 Plateforme</h3>
            <p> Analysez la répartition des écoutes sur les principales plateformes de streaming (Spotify, Youtube, Deezer,…). Identifiez la performance des titres selon les différents services.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Accéder aux Plateformes", key="btn_plateforme", use_container_width=True):
        st.switch_page("pages/3_Platforms.py")

with col4:
    st.markdown("""
    <div class="custom-card">
        <h3>🎤 Festival</h3>
        <p>Plongez dans l'univers des festivals de musique ! Découvrez les événements majeurs, leurs statistiques d'affluence, leur impact économique et les genres musicaux les plus représentés .</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Accéder aux Festivals", key="btn_festivals", use_container_width=True):
        st.switch_page("pages/4_Event_concerts.py")

st.divider()

st.markdown("""
    <div class="custom-card">
        <h2>Contexte et présentation du projet </h2>
        </div>
""", unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Présentation 👥", "Objectif et enjeux 🎯", "Rétroplanning 📅", "Démarche et Méthodologie 📝", "Diagramme 🤖"])

#### PRESENTATION DE L'EQUIPE ####
with tab1: 
    cols = st.columns(4)
    teammates = [
        ("Elisabeth", "Tran", "https://img.freepik.com/photos-gratuite/femme-heureuse-coup-moyen_23-2149007441.jpg"),
        ("Meriem", "Nemri", "https://img.freepik.com/photos-gratuite/smiley-femme-posant-au-bord-plage_23-2148629772.jpg"),
        ("Camille", "Anelli", "https://img.freepik.com/photos-gratuite/jeune-belle-femme-dodue-aimant-son-corps_23-2149180832.jpg"),
        ("Olivier", "Lemperriere", "https://img.freepik.com/photos-gratuite/amis-age-moyen-s-amusant_23-2149150938.jpg")
    ]
    for col, (first_name, last_name, img_url) in zip(cols, teammates):
        with col:
            # Centrage de l'image
            st.markdown(f"""
                <div style='display: flex; justify-content: center; margin-bottom: 10px;'>
                    <img src='{img_url}' width='150' style='border-radius: 10px;'>
                </div>
            """, unsafe_allow_html=True)

            # Utilisation du CSS harmonisé pour afficher les noms
            st.markdown(f"""
                <div class="custom-card" style='text-align: center;'>
                    {first_name}<br>{last_name}
                </div>
            """, unsafe_allow_html=True)

#### OBJECTIF ET ENJEUX ####
with tab2:
    # Affichage du titre "Objectif du projet" avec le style harmonisé
    st.markdown("""
        <div class="custom-card" style='text-align: center;'>
            Objectif du projet
        </div>
    """, unsafe_allow_html=True)

    # Liste des objectifs
    st.markdown("""
    - Concevoir une application complète d'analyse de données musicales, de la collecte à la visualisation interactive.  
    - Expérimenter l'ensemble du cycle de vie des données : acquisition, traitement, stockage, analyse et restitution.  
    - Automatiser la gestion des données grâce à un pipeline ETL performant et adaptable.  
    - Offrir une interface intuitive permettant d'explorer les tendances musicales et d'adapter les visualisations aux besoins des utilisateurs.  
    """, unsafe_allow_html=False)

    # Affichage du titre "Enjeux du projet" avec le style harmonisé
    st.markdown("""
        <div class="custom-card" style='text-align: center;'>
            Enjeux du projet
        </div>
    """, unsafe_allow_html=True)

    # Liste des enjeux
    st.markdown("""
    - **Fiabilité et actualisation des données** : Assurer la collecte et la mise à jour régulière des informations pour garantir des analyses pertinentes.  
    - **Qualité et structuration des données** : Optimiser le nettoyage et l'organisation des données pour une exploitation efficace.  
    - **Accessibilité et expérience utilisateur** : Développer une interface fluide et interactive pour une exploration intuitive des tendances.  
    """, unsafe_allow_html=False)


#### RETROPLANNING ####
with tab3: 
    cols = st.columns(4)
    weeks = ["Semaine 1", "Semaine 2", "Semaine 3", "Semaine 4"]
    descriptions = [
        "Acquisition des Données, Traitement et Nettoyage",
        "Mise en place d'une Infrastructure de Données",
        "Création des Visualisations et de l'Interface Utilisateur",
        "Affinage de l'interface et Présentation du projet"
    ]
    for col, week, desc in zip(cols, weeks, descriptions):
        with col:
            st.markdown(f"""
                <div class="custom-card" style='text-align: center;'>
                    {week}
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'>{desc}</p>", unsafe_allow_html=True)

#### DEMARCHE, OUTILS ET EXPLORATION DES DONNEES ####
with tab4:
    cols = st.columns(3)
    # Étapes réalisées
    with cols[0]:
        st.markdown(f"""
            <div class="custom-card" style='text-align: center;'>
                Étapes réalisées
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        1. **Acquisition des Données**  
        2. **Intégration et traitement dans Mage-AI (nettoyage et update PostgreSQL)**  
        3. **Recherche de KPI pertinents**  
        4. **Création de l'interface Streamlit**  
        5. **Test de l'interface**  
        """, unsafe_allow_html=False)

    # Outils utilisés
    with cols[1]:
        st.markdown(f"""
            <div class="custom-card" style='text-align: center;'>
                Outils Utilisés
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        - **🐍 Python (pandas, numpy)**  
        - **🐳 Docker**  
        - **🤖 Mage-AI**  
        - **🌐 PostgreSQL**  
        - **📺 Streamlit**  
        """, unsafe_allow_html=False)

    # Collecte des données
    with cols[2]:
        st.markdown(f"""
            <div class="custom-card" style='text-align: center;'>
                Collecte des Données
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        - **Fichiers CSV**  
        - **Web scraping**  
        - **API REST**  
        """, unsafe_allow_html=False)

        
### Diagramme Mage-AI

with tab5:
    # Configuration de la connexion à la base de données PostgreSQL
    if "DB_CONFIG" not in st.session_state:
        st.session_state.DB_CONFIG = {
            'user': 'postgres',
            'password': 'hWWCWtvKQODqEErOleTnHmTcuKWaRAgd',
            'host': 'monorail.proxy.rlwy.net',
            'port': '59179',
            'database': 'railway'
        }

    # Vérifier si engine n'est pas déjà en session_state
    if "engine" not in st.session_state:
        st.session_state.engine = create_engine(
            f"postgresql://{st.session_state.DB_CONFIG['user']}:"
            f"{st.session_state.DB_CONFIG['password']}@"
            f"{st.session_state.DB_CONFIG['host']}:"
            f"{st.session_state.DB_CONFIG['port']}/"
            f"{st.session_state.DB_CONFIG['database']}"
        )


    # Chargement des données Billboard
    @st.cache_data
    def load_data():
        with st.session_state.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM billboard_ol"))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        return data

    df = load_data()

    # Définir le diagramme en tant que chaîne DOT
    diagram_global = """
    digraph process {
        rankdir=TB;  // Organisation de haut à bas

        // Définition du style commun des noeuds
        node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=12];
        
        bgcolor="#2b2b2b";

        // concerts
        concert_data_loader [label="CSV Brut\\nData loader", fillcolor="#1f77b4", fontcolor="white"];
        concert_clean_economic_impact [label="Convertion devises en USD\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        concert_ages_ranges [label="Création des tranches d'âges\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        concert_add_coordinates_country [label="Coords geo des pays\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        concert_add_coordinates_location [label="Coords geo des villes\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        concert_flag_url [label="Ajout URL des drapeaux de pays\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        concert_clean [label="Nettoyage (Manquants / Doublons)\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        concert_table_festivals [label="UPSERT table FESTIVALS\\nData exporter", fillcolor="#ff7f0e", fontcolor="white"];
        
        //evolution
        evolution_data_loader [label="Web Scrapping Billboard.com\\nData loader", fillcolor="#1f77b4", fontcolor="white"];
        evolution_ajout_week_year [label="Ajout Week et Year\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        evolution_table_billboard [label="UPSERT table BILLBOARD\\nData exporter", fillcolor="#ff7f0e", fontcolor="white"];
        
        //WorldCharts
        WorldCharts_data_loader [label="Web Scrapping kworb.net\\nData loader", fillcolor="#1f77b4", fontcolor="white"];
        WorldCharts_ajout_genre_popularity [label="API Spotify\\nAjout Genre et Popularité\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        WorldCharts_explode_genres [label="Explode des Genres\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        # WorldCharts_add_coordinates [label="Définition Coords geo\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        WorldCharts_coordinates_to_table [label="Ajout Coords geo\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        WorldCharts_table_WorldCharts [label="UPSERT table WORLDCHATS\\nData exporter", fillcolor="#ff7f0e", fontcolor="white"];
        
        //plateform
        plateform_data_loader [label="CSV Brut\\nData loader", fillcolor="#1f77b4", fontcolor="white"];
        plateform_drop_columns [label="Drop colonnes inutiles\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        plateform_num_values [label="Valeurs num. manquantes\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        plateform_text_values [label="Valeurs txt manquantes\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        plateform_table_plateforms [label="UPSERT table PLATEFORMS\\nData exporter", fillcolor="#ff7f0e", fontcolor="white"];
        
        // streamlit
        streamlit [label="STREAMLIT", fillcolor=red, fontcolor="white"];
        
        
        subgraph cluster_concert {
            labelloc="t"
            label="Event Concerts"  
            fontcolor="white"
            fontsize=20         
            concert_data_loader -> concert_clean_economic_impact
            concert_clean_economic_impact -> concert_ages_ranges
            concert_ages_ranges -> concert_add_coordinates_country
            concert_add_coordinates_country -> concert_add_coordinates_location
            concert_add_coordinates_location -> concert_flag_url
            concert_flag_url -> concert_clean
            concert_clean -> concert_table_festivals
        }
            concert_table_festivals -> streamlit
        
        subgraph cluster_evolution {
            labelloc="t"
            label="Evolution"        
            fontcolor="white"
            fontsize=20   
            evolution_data_loader -> evolution_ajout_week_year
            evolution_ajout_week_year -> evolution_table_billboard
        }  
            evolution_table_billboard -> streamlit 
        
        subgraph cluster_WorldCharts {
            labelloc="t"
            label="WorldCharts"
            fontcolor="white"
            fontsize=20   
            WorldCharts_data_loader -> WorldCharts_ajout_genre_popularity 
            WorldCharts_ajout_genre_popularity -> WorldCharts_explode_genres
            WorldCharts_explode_genres -> WorldCharts_coordinates_to_table
            WorldCharts_coordinates_to_table -> WorldCharts_table_WorldCharts
        }
            WorldCharts_table_WorldCharts -> streamlit
        
        subgraph cluster_plateforms {
            labelloc="t"
            label="plateforms"
            fontcolor="white"
            fontsize=20   
            plateform_data_loader -> plateform_drop_columns
            plateform_drop_columns -> plateform_num_values
            plateform_num_values -> plateform_text_values
            plateform_text_values -> plateform_table_plateforms 
        }
            plateform_table_plateforms -> streamlit 
    }
    """

    st.write("")
    st.markdown(
    """
    <h4 style="text-align: center; color: white;">Le diagramme ci-dessous montre la structure du projet<br>et les pipelines Mage-AI des différents composants.</h4>
    """,
    unsafe_allow_html=True
)
    if st.__version__ != "1.39.0":
        st.graphviz_chart(diagram_global, use_container_width=False)
    else:
        st.graphviz_chart(diagram_global, use_container_width=True)
