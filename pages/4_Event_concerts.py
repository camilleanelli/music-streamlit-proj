import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from sqlalchemy import create_engine, text
from streamlit_folium import st_folium, folium_static


# Configuration de la page 
st.session_state["_page"] = "Event_concerts"

st.set_page_config(
    page_title="Festival",
    page_icon="🎤",
    layout="wide"
)

DB_CONFIG = {
    'user': 'postgres',
    'password': 'hWWCWtvKQODqEErOleTnHmTcuKWaRAgd',
    'host': 'monorail.proxy.rlwy.net',
    'port': '59179',
    'database': 'railway'
}


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
    st.markdown("<h1 style='text-align: center; color: white;'> Analyse des festivals à travers le monde </h1>", unsafe_allow_html=True)

    # Sidebar - Filtres
    st.sidebar.header("Filtres")

    # Options de filtre sans "Tous" affiché par défaut
    festival_list = sorted(df["Festival_Name"].unique())
    country_list = sorted(df["Country"].unique())
    city_list = sorted(df["Location"].dropna().unique())  # Vérifier les valeurs vides
    age_category_list = sorted(df["Age_Category"].dropna().unique())
    music_genre_list = sorted(df["Music_Genre"].dropna().unique())

    # Widgets interactifs pour filtrer
    selected_festival = st.sidebar.multiselect("Festival", options=festival_list, placeholder="Tous")
    selected_country = st.sidebar.multiselect("Pays", options=country_list, placeholder="Tous")
    selected_city = st.sidebar.multiselect("Ville", options=city_list, placeholder="Tous")
    selected_age_category = st.sidebar.multiselect("Catégorie d'âge", options=age_category_list, placeholder="Tous")
    selected_music_genre = st.sidebar.multiselect("Genre Musical", options=music_genre_list, placeholder="Tous")

    # Appliquer les filtres à la dataframe
    filtered_df = df.copy()

    if selected_festival:
        filtered_df = filtered_df[filtered_df["Festival_Name"].isin(selected_festival)]
    if selected_country:
        filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]
    if selected_city:
        filtered_df = filtered_df[filtered_df["Location"].isin(selected_city)]
    if selected_age_category:
        filtered_df = filtered_df[filtered_df["Age_Category"].isin(selected_age_category)]
    if selected_music_genre:
        filtered_df = filtered_df[filtered_df["Music_Genre"].isin(selected_music_genre)]


    tab1, tab2, tab3 = st.tabs(["Aperçu des performances globales 📈", "Analyse d'audience 👥", "Impact économique internationale 💰"])


    #### BLOC 1 : OVERVIEW AND OVERALL PERFORMANCE ####
    with tab1:
        # Fonction Format K/M avec 2 décimales
        def format_large_number(num):
            if num >= 1_000_000:
                return f"{num / 1_000_000:.2f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.2f}K"
            return str(num)

        # Ajouter un fond gris aux métriques en utilisant CSS 
        st.markdown("""
            <style>
                .metric-container {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 20px;
                }
                .metric-box {
                    flex: 1;
                    padding: 10px;
                    text-align: center;
                    background-color: #f0f2f6;
                    border-radius: 5px;
                    margin: 5px;
                }
                .metric-label {
                    font-size: 16px;
                    color: #555;
                    margin-bottom: 5px;
                }
                .metric-value {
                    font-size: 20px;
                    font-weight: bold;
                    color: #0e1117;
                }
            </style>
        """, unsafe_allow_html=True)

        # Calcul des métriques
        total_festivals = filtered_df["Festival_Name"].nunique()
        total_participants = round(filtered_df["Attendance_Numbers"].sum(), 0)
        total_revenue = round(filtered_df["Economic_Impact_USD"].sum(), 2)
        avg_participants = round(total_participants / total_festivals, 2)

        metrics1_html = f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-label">🎉 Total Festivals</div>
                <div class="metric-value">{total_festivals}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">👫 Total Participants</div>
                <div class="metric-value">{format_large_number(total_participants)}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">💲 Total Revenue</div>
                <div class="metric-value">${format_large_number(total_revenue)}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">📊 Moyenne Participants/Festival</div>
                <div class="metric-value">{format_large_number(avg_participants)}</div>
            </div>
        </div>
        """
        st.markdown(metrics1_html, unsafe_allow_html=True)


        # Diviser en deux colonnes pour afficher les tables côte à côte
        col1, col2 = st.columns(2)

        # --- Table 1 : Total Revenue par Pays
        with col1:
            st.subheader("_Total Revenue par Pays_")
            
            # Agréger les données par pays et trier par impact économique décroissant
            country_impact = filtered_df.groupby(["Flag_URL", "Country"])["Economic_Impact_USD"].sum().reset_index()
            country_impact = country_impact.sort_values("Economic_Impact_USD", ascending=False)
            
            # Configurer l'affichage des images
            styled_country_impact = country_impact.style.format({"Economic_Impact_USD": "${:,.0f}"}).background_gradient(
            subset=["Economic_Impact_USD"], cmap="RdYlGn")

            # Affichage du tableau dans Streamlit
            st.dataframe(
                styled_country_impact,
                column_config={
                    "Flag_URL": st.column_config.ImageColumn("Drapeau", width = "350"),
                    "Country": st.column_config.TextColumn("Pays", width="stretch"),
                    "Economic_Impact_USD": st.column_config.TextColumn("Impact Économique (USD)", width="stretch"),
                },
                hide_index=True,
                use_container_width=True
            )

        # --- Table 2 : Liste des Festivals
        with col2:
            st.subheader("_Liste des Festivals_")
            
            # Extraire uniquement les colonnes nécessaires
            festival_list = filtered_df[["Festival_Name"]].drop_duplicates().sort_values("Festival_Name")
            
            # Affichage de la table avec configuration des colonnes
            st.dataframe(
                festival_list,
                column_config={
                    "Festival_Name": st.column_config.TextColumn("Festival", width="stretch")
                },
                hide_index=True,
                use_container_width=True 
            )

        # --- Carte des Festivals
        st.subheader("_Carte géographique des Festivals_")

        # Créer une carte Folium centrée sur un point moyen des festivals
        m = folium.Map(location=[filtered_df["Latitude_Location"].mean(), 
                                filtered_df["Longitude_Location"].mean()], zoom_start=2)

        # Ajouter les marqueurs des festivals
        for _, row in filtered_df.iterrows():
            folium.Marker(
                location=[row["Latitude_Location"], row["Longitude_Location"]], 
                tooltip=(
                    f"Nom: {row['Festival_Name']}<br>"
                    f"Pays: {row['Country']}<br>"
                    f"Ville: {row['Location']}<br>"
                    f"Total Participants: {row['Attendance_Numbers']:,}"
                ),
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

        # Afficher la carte dans Streamlit
        with st.container():
            folium_static(m, width=1200, height=600)


    #### BLOC 2 : AUDIENCE AND TREND ANALYSIS ####
    with tab2:
        # --- KPI Catégorie d'âge dominante
        top_age_group = filtered_df.groupby("Age_Category")["Attendance_Numbers"].sum().idxmax()
        total_top_age = filtered_df.groupby("Age_Category")["Attendance_Numbers"].sum().max()

        metrics2_html = f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-label">👨‍👨‍👧‍👧 Catégorie d'âge dominant</div>
                <div class="metric-value">{top_age_group} - {total_top_age:,} Participants</div>
            </div>
        """
        st.markdown(metrics2_html, unsafe_allow_html=True)

        # --- Graphique en secteurs : Proportion des participants par catégorie d'âge
        st.subheader("_Proportion des participants par catégorie d'âge_")
        fig_pie = px.pie(
            filtered_df,
            names="Age_Category",
            values="Attendance_Numbers",
            labels={"Age_Category": "Catégorie d'âge", "Attendance_Numbers": "Total Participants"},
            color="Age_Category",  # Assurer la correspondance des couleurs
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        # Personnalisation de la mise en page avec fond semi-transparent
        fig_pie.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
            paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
            legend=dict(
                bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
                font=dict(color="white")  # Texte blanc pour la lisibilité
            ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # --- Bubble Chart : Classement des Festivals par Âge 
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
            labels={"Age_Category": "Catégorie d'âge", "Festival_Name": "Festival", "Attendance_Numbers": "Total Participants"},
            hover_data={
                "Festival_Name": True,  
                "Age_Category": True,
                "Attendance_Numbers":':,',  # Formatage des milliers
            },
            height=1400,
            size_max=50,
            category_orders={"Age_Category": age_category_order, "Festival_Name": top_festivals_age["Festival_Name"].tolist()}
        )
        # Personnalisation de la mise en page avec fond semi-transparent
        fig_bubble.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
            paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
            legend=dict(
                bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
                font=dict(color="white")  # Texte blanc pour la lisibilité
            ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
        )
        st.plotly_chart(fig_bubble, use_container_width=True)


    #### BLOC 3 : ECONOMIC IMPACT AND INTERNATIONAL COMPARISON ####
    with tab3 : 
        # --- KPI Ratio Impact Économique
        economic_ratio = round(filtered_df["Economic_Impact_USD"].sum() / filtered_df["Attendance_Numbers"].sum(), 2)
        
        metrics2_html = f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-label">💵 Ratio économique par participant</div>
                <div class="metric-value">${economic_ratio} /pers</div>
            </div>
        </div>
        """
        st.markdown(metrics2_html, unsafe_allow_html=True)

        # --- Tableau : Analyse des festivals par chiffre d'affaires
        st.subheader("_Analyse des festivals par Chiffre d'affaires_")
        festival_revenue = filtered_df.groupby(["Flag_URL", "Festival_Name", "Country", "Music_Genre"])[["Economic_Impact_USD", "Attendance_Numbers"]].sum().reset_index()
        festival_revenue = festival_revenue.sort_values("Economic_Impact_USD", ascending=False)

        # Configurer l'affichage des images
        styled_df = (festival_revenue.style.format({
                "Economic_Impact_USD": "${:,.0f}", 
                "Attendance_Numbers": "{:,.0f}"
                })).background_gradient(subset=["Economic_Impact_USD"], cmap="RdYlGn")
        
        # Affichage du tableau dans Streamlit
        st.dataframe(
            styled_df,
            column_config={
                "Flag_URL": st.column_config.ImageColumn("Drapeau", width=40),
                "Country": st.column_config.TextColumn("Pays", width="stretch"),
                "Festival_Name": st.column_config.TextColumn("Festival", width="stretch"),
                "Economic_Impact_USD": st.column_config.TextColumn("Impact Économique (USD)", width="stretch"),
                "Attendance_Numbers": st.column_config.TextColumn("Nombre de Participants", width="stretch"),
                "Music_Genre": st.column_config.TextColumn("Genre Musical", width="stretch")
            },
            hide_index=True,
            use_container_width=True
        )

        col1, col2 = st.columns(2)

        # --- Graphique Bar : Impact Économique par Festival (colonne 1)
        with col1:
            st.subheader("_Aspect financier par Festival_")
            
            top_revenue_festivals = filtered_df.groupby("Festival_Name")["Economic_Impact_USD"].sum().nlargest(10).reset_index()
            
            fig_revenue = px.bar(
                top_revenue_festivals.sort_values("Economic_Impact_USD", ascending=True),  # Trier pour affichage du plus petit au plus grand
                x="Economic_Impact_USD",
                y="Festival_Name",
                orientation="h",
                color="Economic_Impact_USD",
                labels={"Festival_Name": "Festival", "Economic_Impact_USD": "Economic Impact (USD)"},
                hover_data={
                    "Festival_Name": True,  
                    "Economic_Impact_USD":':,',  # Formatage des milliers
                },
                height=500
            )
            # Personnalisation de la mise en page avec fond semi-transparent
            fig_revenue.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
            paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
            legend=dict(
                bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
                font=dict(color="white")  # Texte blanc pour la lisibilité
            ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
            )
            st.plotly_chart(fig_revenue, use_container_width=True)

        # --- Graphique Bar : Impact Économique par Genre Musical (colonne 2)
        with col2:
            st.subheader("_Aspect financier par Genre musical_")

            music_genre_impact = filtered_df.groupby("Music_Genre")["Economic_Impact_USD"].sum().nlargest(10).reset_index()
            music_genre_impact = music_genre_impact.sort_values("Economic_Impact_USD", ascending=True)  

            fig_music_genre = px.bar(
                music_genre_impact,
                x="Economic_Impact_USD",
                y="Music_Genre",
                orientation="h",
                color="Economic_Impact_USD",
                labels={"Music_Genre": "Genre Musical", "Economic_Impact_USD": "Economic Impact (USD)"},
                hover_data={
                    "Music_Genre": True,  
                    "Economic_Impact_USD":':,',  # Formatage des milliers
                },
                height=500
            )
            # Personnalisation de la mise en page avec fond semi-transparent
            fig_music_genre.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la zone de traçage
            paper_bgcolor="rgba(0, 0, 0, 0.5)",  # Fond semi-transparent pour tout le graphique
            legend=dict(
                bgcolor="rgba(0, 0, 0, 0.0)",  # Fond semi-transparent pour la légende
                font=dict(color="white")  # Texte blanc pour la lisibilité
            ),
            margin=dict(t=50, b=50, l=50, r=50),  # Ajustement des marges
            )
            st.plotly_chart(fig_music_genre, use_container_width=True)

        

