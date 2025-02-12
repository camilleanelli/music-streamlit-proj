import streamlit as st
import pandas as pd
import plotly.express as px

# Charger les données exportées depuis Power BI
df = pd.read_csv("data_music_festival_cleaned_with_flags.csv")

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
st.markdown("## 📈 Overview and Overall Performance")

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

# Table 1 : Economic Impact by Country
with col1:
    st.subheader("Total Revenue by Country")
    
    # Agréger les données par pays et trier par impact économique décroissant
    country_impact = filtered_df.groupby("Country")["Economic_Impact_USD"].sum().reset_index()
    country_impact = country_impact.sort_values("Economic_Impact_USD", ascending=False)

    # Affichage de la table
    st.dataframe(country_impact.style.format({"Economic_Impact_USD": "${:,.0f}"}))


# Table 2 : Liste des Festivals
with col2:
    st.subheader("List of Festivals")
    
    # Extraire uniquement les colonnes nécessaires
    festival_list = filtered_df[["Festival_Name"]].drop_duplicates()

    # Affichage de la table
    st.dataframe(festival_list)

# Carte des festivals
st.subheader("Geographic Map of Festivals")
fig = px.scatter_mapbox(
    filtered_df, lat="Latitude_Location", lon="Longitude_Location",
    hover_name="Festival_Name",
    hover_data={"Country": True, "Location": True, "Attendance_Numbers": True},
    color="Economic_Impact_USD",
    size="Attendance_Numbers",
    color_continuous_scale="cividis",
    zoom=2, height=500, mapbox_style="open-street-map"
)
st.plotly_chart(fig, use_container_width=True)


# --- BLOC 2 : AUDIENCE AND TREND ANALYSIS ---
st.markdown("## 👥 Audience and Trend Analysis")

# KPI Catégorie d'âge dominante
top_age_group = filtered_df.groupby("Age_Category")["Attendance_Numbers"].sum().idxmax()
total_top_age = filtered_df.groupby("Age_Category")["Attendance_Numbers"].sum().max()

st.metric("👨‍👨‍👧‍👧 Dominant Age Group", f"{top_age_group} - {total_top_age:,} Participants")

# Graphique en secteurs
st.subheader("Proportion of Participants by Age Category")
fig_pie = px.pie(
    filtered_df,
    names="Age_Category",
    values="Attendance_Numbers",
    labels={"Age_Category": "Age Category"},  # Ajout du label explicite
    color="Age_Category",  # Assurer la correspondance des couleurs
    color_discrete_sequence=px.colors.qualitative.Set2
)
st.plotly_chart(fig_pie, use_container_width=True)

# Classement des Festivals par Âge avec légende
st.subheader("Ranking of Festivals by Age Category")
top_festivals_age = filtered_df.groupby(["Festival_Name", "Age_Category"])["Attendance_Numbers"].sum().reset_index()
fig_bar_age = px.bar(
    top_festivals_age.sort_values("Attendance_Numbers", ascending=False),
    x="Attendance_Numbers", 
    y="Festival_Name",
    color="Age_Category",
    orientation="h",
    labels={"Attendance_Numbers": "Total Participants"},
    height=500
)
st.plotly_chart(fig_bar_age, use_container_width=True)


# --- BLOC 3 : ECONOMIC IMPACT AND INTERNATIONAL COMPARISON ---
st.markdown("## 💰 Economic Impact and International Comparison")

# KPI Ratio Impact Économique
economic_ratio = round(filtered_df["Economic_Impact_USD"].sum() / filtered_df["Attendance_Numbers"].sum(), 2)
st.metric("💵 Economic Impact Ratio per Participant", f"${economic_ratio} /pers")

# Graphique Bar : Impact Économique par Festival (trié du plus petit au plus grand)
st.subheader("Economic Impact by Festival")
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

# Graphique Bar : Impact Économique par Genre Musical
st.subheader("Economic Impact by Music Genre")

music_genre_impact = filtered_df.groupby("Music_Genre")["Economic_Impact_USD"].sum().reset_index()
music_genre_impact = music_genre_impact.sort_values("Economic_Impact_USD", ascending=True)  # Tri du plus grand au plus petit (de haut en bas)

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

# Table : Festival Analysis by Revenue
st.subheader("Festival Analysis by Revenue")
festival_revenue = filtered_df.groupby(["Festival_Name", "Country"])[["Economic_Impact_USD", "Attendance_Numbers"]].sum().reset_index()
festival_revenue = festival_revenue.sort_values("Economic_Impact_USD", ascending=False)
st.dataframe(festival_revenue.style.format({"Economic_Impact_USD": "${:,.0f}", "Attendance_Numbers": "{:,.0f}"}))

