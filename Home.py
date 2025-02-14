import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine, text
import pandas as pd
# Configuration de la page
st.session_state["_page"] = "Home"
st.set_page_config(
    layout="centered",
    page_title="Home",
    page_icon="👋",
    )

# Ajouter une image background depuis une URL en utilisant CSS 
st.markdown(
    f"""
    <style>
        .stApp {{
            background-image: url("https://img.freepik.com/free-vector/wavy-colorful-background-style_23-2148497521.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-color: rgba(0,0,0, 0.5); /* Modifie entre 0.3 et 0.8 selon le niveau de transparence voulu */
            background-blend-mode: overlay; /* Fusionne l'image et la couleur */
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Rendre la sidebar de Streamlit semi-transparente afin qu'on puisse voir le background
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

# Ajout du titre principal du dashboard
st.markdown("<h1 style='text-align: center; color: white;'> Projet - Analyse Music </h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Présentation 👥", "Objectif et enjeux 🎯", "Rétroplanning 📅", "Démarche et Méthodologie 📝", "🤖 Diagramme Mage-Ai"])

#### PRESENTATION DE L'EQUIPE ####
with tab1: 
    cols = st.columns(4)
    teammates = [
        ("Olivier", "Lemperriere", "https://img.freepik.com/photos-gratuite/amis-age-moyen-s-amusant_23-2149150938.jpg"),
        ("Elisabeth", "Tran", "https://img.freepik.com/photos-gratuite/femme-heureuse-coup-moyen_23-2149007441.jpg"),
        ("Meriem", "Nemri", "https://img.freepik.com/photos-gratuite/smiley-femme-posant-au-bord-plage_23-2148629772.jpg"),
        ("Camille", "Anelli", "https://img.freepik.com/photos-gratuite/jeune-belle-femme-dodue-aimant-son-corps_23-2149180832.jpg")
    ]
    for col, (first_name, last_name, img_url) in zip(cols, teammates):
        with col:
            st.image(img_url, width=150)
            background_html = f"""
            <div class="metric-container">
                <div class="metric-box">
                    <div class="metric-value">{first_name}</div>
                    <div class="metric-value">{last_name}</div>
                </div>
            </div>
            """
            st.markdown(background_html, unsafe_allow_html=True)


#### OBJECTIF ET ENJEUX ####
with tab2:
    background_html = f"""
    <div class="metric-container">
        <div class="metric-box">
            <div class="metric-value">Objectif du projet</div>
        </div>
    </div>
    """
    st.markdown(background_html,unsafe_allow_html=True)
    st.markdown("""
    - **Développer une application d'analyse de données complète, de la collecte à la visualisation**  
    - **Expérimenter l'ensemble du workflow data : collecte, nettoyage, stockage, analyse et visualisation**  
    - **Mettre en place une infrastructure pour gérer les données efficacement**  
    - **Proposer une interface interactive permettant l'exploration et la personnalisation des visualisations**
    """, unsafe_allow_html=False)

    background_html = f"""
    <div class="metric-container">
        <div class="metric-box">
            <div class="metric-value">Enjeux du projet</div>
        </div>
    </div>
    """
    st.markdown(background_html,unsafe_allow_html=True)
    st.markdown("""
    - **Assurer la collecte de données de qualité et leur mise à jour régulière**  
    - **Structurer et nettoyer les données pour une exploitation optimale**  
    - **Offrir une interface intuitive et des visualisations dynamiques**
    """, unsafe_allow_html=False)


#### RETROPLANNING ####
with tab3: 
    cols = st.columns(4)
    weeks = ["Sem 1", "Sem 2", "Sem 3", "Sem 4"]
    descriptions = [
        "Acquisition des Données, Traitement et Nettoyage",
        "Mise en place d'une Infrastructure de Données",
        "Création des Visualisations et de l'Interface Utilisateur",
        "Affinage de l'interface et Présentation du projet"
    ]
    for col, week, desc in zip(cols, weeks, descriptions):
        with col:
            background_html = f"""
            <div class="metric-container">
                <div class="metric-box">
                    <div class="metric-value">{week}</div>
                </div>
            """
            st.markdown(background_html, unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'>{desc}</p>", unsafe_allow_html=True)


#### DEMARCHE, OUTILS ET EXPLORATION DES DONNEES ####
with tab4:
    section_background("Démarche et Méthodologie")
    cols = st.columns(3)
    with cols[0]:
        background1_html = f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-value">Étapes réalisées </div>
            </div>
        </div>
        """
        st.markdown(background1_html, unsafe_allow_html=True)
        st.markdown("""
        1. **Acquisition des Données**
        2. **Analyse et nettoyage**  
        3. **Intégration dans Mage-AI et création d'une base de données PostgreSQL**
        4. **Recherche de KPI pertinents**
        5. **Création de l'interface Streamlit**
        6. **Test de l'interface**
        """, unsafe_allow_html=False)


    with cols[1]:
        background1_html = f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-value">Outils Utilisés</div>
            </div>
        </div>
        """
        st.markdown(background1_html, unsafe_allow_html=True)
        st.markdown("""
        - **🐍 Python (pandas, numpy)**
        - **🐳 Docker**  
        - **🤖 Mage-Ai**
        - **🌐 PostgreSQL**
        - **📺 Streamlit**
        """, unsafe_allow_html=False)

    with cols[2]:
        background1_html = f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-value">Exploration des Données</div>
            </div>
        </div>
        """
        st.markdown(background1_html, unsafe_allow_html=True)
        st.markdown("""
        - **Fichiers bases de données**
        - **Web scraping**  
        """, unsafe_allow_html=False)
        
### Diagramme Mage-AI

with tab5:
    # st.image("diagramme_mage-ai.png", use_column_width=True)
    st.markdown("""
    Le diagramme ci-dessus montre la structure du projet et les interactions entre les différents composants.
    """, unsafe_allow_html=False)

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
        WorldCharts_ajout_genre_popularity [label="API Spotify -> Ajout Genre et Popularité\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        WorldCharts_explode_genres [label="Explode des Genres\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
        WorldCharts_add_coordinates [label="Définition Coords geo\\nTransformer", fillcolor="#9467bd", fontcolor="white"];
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
            WorldCharts_explode_genres -> {WorldCharts_add_coordinates WorldCharts_coordinates_to_table}
            WorldCharts_add_coordinates -> WorldCharts_coordinates_to_table
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
    
    st.header("Diagramme Mage-AI")
    if st.__version__ != "1.39.0":
        st.graphviz_chart(diagram_global, use_container_width=False)
    else:
        st.graphviz_chart(diagram_global, use_container_width=True)