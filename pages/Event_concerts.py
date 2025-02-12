import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static
from sqlalchemy import create_engine, select, text

# Configuration de la page 
st.session_state["_page"] = "Event_concerts"
st.set_page_config(layout="wide")

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
if "Event_concerts" in st.session_state.get("_page", ""): 
    @st.cache_data
    def load_data():
        with engine.connect() as connection:
            result = connection.execute(text("""
                                            SELECT 
                                                festival_name AS "Festival_Name",
                                                _location AS "Location",
                                                latitude_location AS "Latitude_Location",
                                                longitude_location AS "Longitude_Location",
                                                country AS "Country",
                                                latitude_country AS "Latitude_country",
                                                longitude_country AS "Longitude_country",
                                                _year AS "Year",
                                                attendance_numbers AS "Attendance_Numbers",
                                                age_category AS "Age_Category",
                                                visitor_demographics AS "Visitor_Demographics",
                                                economic_impact AS "Economic_Impact",
                                                economic_impact_usd AS "Economic_Impact_USD",
                                                music_genre AS "Music_Genre",
                                                flag_url AS "Flag_URL"
                                            FROM festivals
                                            """))
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        return data

    df = load_data()

    # Ajout du titre principal du dashboard
    st.markdown("<h1 style='text-align: center; color: brown;'> Dashboard Music Festival - 2024 </h1>", unsafe_allow_html=True)

    # Sidebar - Filtres
    st.sidebar.header("🔍 Filtres Interactifs")

    # Options de filtre avec "Tous" comme valeur par défaut
    festival_list = ["Tous"] + sorted(df["Festival_Name"].unique())
    country_list = ["Tous"] + sorted(df["Country"].unique())
    city_list = ["Tous"] + sorted(df["Location"].dropna().unique())  # Vérifier les valeurs vides
    age_category_list = ["Tous"] + sorted(df["Age_Category"].dropna().unique())
    music_genre_list = ["Tous"] + sorted(df["Music_Genre"].dropna().unique())

    # Widgets interactifs pour filtrer
    selected_festival = st.sidebar.selectbox("🎤 Festival", festival_list)
    selected_country = st.sidebar.selectbox("🌍 Pays", country_list)
    selected_city = st.sidebar.selectbox("🏙️ Ville", city_list)
    selected_age_category = st.sidebar.selectbox("👥 Catégorie d'Âge", age_category_list)
    selected_music_genre = st.sidebar.selectbox("🎶 Genre Musical", music_genre_list)

    # Bouton pour réinitialiser les filtres
    if st.sidebar.button("🔄 Reset Filters"):
        selected_festival = "Tous"
        selected_country = "Tous"
        selected_city = "Tous"
        selected_age_category = "Tous"
        selected_music_genre = "Tous"

    # Appliquer les filtres à la dataframe
    filtered_df = df.copy()

    if selected_festival != "Tous":
        filtered_df = filtered_df[filtered_df["Festival_Name"] == selected_festival]

    if selected_country != "Tous":
        filtered_df = filtered_df[filtered_df["Country"] == selected_country]

    if selected_city != "Tous":
        filtered_df = filtered_df[filtered_df["Location"] == selected_city]

    if selected_age_category != "Tous":
        filtered_df = filtered_df[filtered_df["Age_Category"] == selected_age_category]

    if selected_music_genre != "Tous":
        filtered_df = filtered_df[filtered_df["Music_Genre"] == selected_music_genre]


    # --- BLOC 1 : OVERVIEW AND OVERALL PERFORMANCE ---
    st.header("📈 Aperçu et performances globales", divider="gray")

    col1, col2, col3, col4 = st.columns(4)

    # Fonction Format K/M avec 2 décimales
    def format_large_number(num):
        if num >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.2f}K"
        return str(num)

    # Calcul des métriques
    total_festivals = filtered_df["Festival_Name"].nunique()
    total_participants = round(filtered_df["Attendance_Numbers"].sum(), 0)
    total_revenue = round(filtered_df["Economic_Impact_USD"].sum(), 2)
    avg_participants = round(total_participants / total_festivals, 2)

    # Affichage des KPI Cards
    col1.metric("🎉 Total Festivals", f"{total_festivals}")
    col2.metric("👥 Total Participants", f"{format_large_number(total_participants)}")
    col3.metric("💰 Total Revenue", f"${format_large_number(total_revenue)}")
    col4.metric("📊 Avg Participants/Fest", f"{format_large_number(avg_participants)}")

    # Diviser en deux colonnes pour afficher les tables côte à côte
    col1, col2 = st.columns(2)

    # Table 1 : Total Revenue par Pays
    with col1:
        st.subheader("_Total Revenue par Pays_")
        
        # Agréger les données par pays et trier par impact économique décroissant
        country_impact = filtered_df.groupby(["Flag_URL", "Country"])["Economic_Impact_USD"].sum().reset_index()
        country_impact = country_impact.sort_values("Economic_Impact_USD", ascending=False)
        
        # Configurer l'affichage des images
        st.dataframe(
            country_impact.style.format({"Economic_Impact_USD": "${:,.0f}"}),
            column_config={
                "Flag_URL": st.column_config.ImageColumn("Drapeau", width = "350"),
                "Country": st.column_config.TextColumn("Pays", width="medium"),
                "Economic_Impact_USD": st.column_config.TextColumn("Impact Économique (USD)", width="medium"),
            },
            hide_index=True,
        )

    # Table 2 : Liste des Festivals
    with col2:
        st.subheader("_Liste des Festivals_")
        
        # Extraire uniquement les colonnes nécessaires
        festival_list = filtered_df[["Festival_Name"]].drop_duplicates()
        
        # Affichage de la table avec configuration des colonnes
        st.dataframe(
            festival_list,
            column_config={
                "Festival_Name": st.column_config.TextColumn("Festival", width="medium")
            },
            hide_index=True
        )

    # Carte des Festivals
    st.subheader("_Carte géographique des Festivals_")

    # Créer une carte Folium centrée sur un point moyen des festivals
    m = folium.Map(location=[filtered_df["Latitude_Location"].mean(), 
                            filtered_df["Longitude_Location"].mean()], zoom_start=4)

    # Ajouter les marqueurs des festivals
    for _, row in filtered_df.iterrows():
        folium.Marker(
            location=[row["Latitude_Location"], row["Longitude_Location"]], 
            tooltip=(
                f"Nom: {row['Festival_Name']}<br>"
                f"Pays: {row['Country']}<br>"
                f"Ville: {row['Location']}<br>"
                f"Participants: {row['Attendance_Numbers']:,}"
            ),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # Afficher la carte dans Streamlit
    folium_static(m)


    # --- BLOC 2 : AUDIENCE AND TREND ANALYSIS ---
    st.header("👥 Analyse d'audience et de tendances", divider="gray")

    # KPI Catégorie d'âge dominante
    top_age_group = filtered_df.groupby("Age_Category")["Attendance_Numbers"].sum().idxmax()
    total_top_age = filtered_df.groupby("Age_Category")["Attendance_Numbers"].sum().max()

    st.metric("👨‍👨‍👧‍👧 Groupe d'âge dominant", f"{top_age_group} - {total_top_age:,} Participants")

    # Graphique en secteurs : Proportion des participants par catégorie d'âge
    st.subheader("_Proportion des participants par catégorie d'âge_")
    fig_pie = px.pie(
        filtered_df,
        names="Age_Category",
        values="Attendance_Numbers",
        color="Age_Category",  # Assurer la correspondance des couleurs
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Bubble Chart : Classement des Festivals par Âge 
    st.subheader("_Classement des festivals par catégorie d'âge_")
    top_festivals_age = filtered_df.groupby(["Festival_Name", "Age_Category"])["Attendance_Numbers"].sum().reset_index()

    # Trier les festivals par nombre total de participants pour un affichage plus lisible
    top_festivals_age = top_festivals_age.sort_values("Attendance_Numbers", ascending=False)

    # Définir un ordre spécifique des catégories d'âge (du plus jeune au plus vieux)
    age_category_order = ["18-24", "25-34", "35-44", "45-54"]

    fig_bubble = px.scatter(
        top_festivals_age,
        x="Age_Category",
        y="Festival_Name",
        size="Attendance_Numbers",
        color="Age_Category",
        labels={"Attendance_Numbers": "Total Participants"},
        hover_data={
            "Festival_Name": True,  
            "Age_Category": True,
            "Attendance_Numbers":':,',  # Formatage des milliers
        },
        height=1400,
        size_max=50,
        category_orders={"Age_Category": age_category_order, "Festival_Name": top_festivals_age["Festival_Name"].tolist()}
    )
    st.plotly_chart(fig_bubble, use_container_width=True)


    # --- BLOC 3 : ECONOMIC IMPACT AND INTERNATIONAL COMPARISON ---
    st.header("💰 Impact économique et comparaison internationale", divider="gray")

    # KPI Ratio Impact Économique
    economic_ratio = round(filtered_df["Economic_Impact_USD"].sum() / filtered_df["Attendance_Numbers"].sum(), 2)
    st.metric("💵 Ratio économique par participant", f"${economic_ratio} /pers")

    # Table : Analyse des festivals par chiffre d'affaires
    st.subheader("_Analyse des festivals par chiffre d'affaires_")
    festival_revenue = filtered_df.groupby(["Flag_URL", "Festival_Name", "Country"])[["Economic_Impact_USD", "Attendance_Numbers"]].sum().reset_index()
    festival_revenue = festival_revenue.sort_values("Economic_Impact_USD", ascending=False)

    # Configurer l'affichage des images
    st.dataframe(
        festival_revenue.style.format({"Economic_Impact_USD": "${:,.0f}", "Attendance_Numbers": "{:,.0f}"}),
        column_config={
            "Flag_URL": st.column_config.ImageColumn("Drapeau", width=70),
            "Country": st.column_config.TextColumn("Pays", width="medium"),
            "Festival_Name": st.column_config.TextColumn("Festival", width="medium"),
            "Economic_Impact_USD": st.column_config.TextColumn("Impact Économique (USD)", width="medium"),
            "Attendance_Numbers": st.column_config.TextColumn("Nombre de Participants", width="medium")
        },
        hide_index=True,
    )


    # Graphique Bar : Impact Économique par Festival (trié du plus petit au plus grand)
    st.subheader("_Aspect financier par Festival_")
    top_revenue_festivals = filtered_df.groupby("Festival_Name")["Economic_Impact_USD"].sum().nlargest(10).reset_index()
    fig_revenue = px.bar(
        top_revenue_festivals.sort_values("Economic_Impact_USD", ascending=True),  # Affichage du plus grand au plus petit (de haut en bas)
        x="Economic_Impact_USD", y="Festival_Name",
        orientation="h",
        color="Economic_Impact_USD",
        labels={"Economic_Impact_USD": "Economic Impact (USD)"},
        height=500
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

    # Graphique Bar : Impact Économique par Genre Musical (trié du plus petit au plus grand)
    st.subheader("_Aspect financier par Genre musical_")

    music_genre_impact = filtered_df.groupby("Music_Genre")["Economic_Impact_USD"].sum().nlargest(10).reset_index()
    music_genre_impact = music_genre_impact.sort_values("Economic_Impact_USD", ascending=True)  # Affichage du plus grand au plus petit (de haut en bas)

    fig_music_genre = px.bar(
        music_genre_impact,
        x="Economic_Impact_USD",
        y="Music_Genre",
        orientation="h",
        color="Economic_Impact_USD",
        labels={"Economic_Impact_USD": "Economic Impact (USD)"},
        height=500
    )
    st.plotly_chart(fig_music_genre, use_container_width=True)

