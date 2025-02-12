import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
import pandas as pd
import seaborn as sns
import graphviz

st.set_page_config(
    page_title="Home",
    page_icon="👋",

    layout="wide"
)


# Configuration de la connexion à la base de données PostgreSQL
DB_CONFIG = {
    'user': 'postgres',
    'password': 'hWWCWtvKQODqEErOleTnHmTcuKWaRAgd',
    'host': 'monorail.proxy.rlwy.net',
    'port': '59179',
    'database': 'railway'
}

# Création de la connexion
engine = create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

# Chargement des données Billboard
@st.cache_data
def load_data():
    with engine.connect() as connection:
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


