
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import os

# Load recommender
# Always resolve path relative to repo root
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # goes up from /app to project root
DATA_PATH = os.path.join(BASE_DIR, "Data", "netflix_titles.csv")

from src.recommendation import NetflixRecommender
rec = NetflixRecommender(DATA_PATH)


# Inject custom CSS for Netflix-style theme
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: #141414;
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    /* Titles and headers */
    h1, h2, h3, h4 {
        color: #E50914 !important;
        font-weight: bold;
    }

    /* Subheaders and text */
    .css-10trblm, .css-1v0mbdj {
        color: #ffffff !important;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #E50914;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
    }
    div.stButton > button:hover {
        background-color: #f40612;
        color: #fff;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #222;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #333;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)



OMDB_API_KEY = "c59e3387"  

def get_poster(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()
    if response.get("Response") == "True":
        return response.get("Poster")
    return None




st.set_page_config(page_title="Netflix Dashboard", page_icon="📺", layout="wide")
st.title("📺 Netflix Dashboard")

# Tabs
tab1, tab2 = st.tabs(["📊 Data Insights", "🎬 Recommendations"])

# ---------------- Tab 1: Insights ----------------
import plotly.express as px

with tab1:
    st.markdown("## 📊 Netflix Insights Dashboard")
    st.write("Explore trends in Netflix shows and movies.")

    # Row 1 → Movies vs TV Shows + Ratings
    col1, col2 = st.columns(2)

    with col1:
        counts = rec.df["type"].value_counts().reset_index()
        counts.columns = ["Type", "Count"]
        fig = px.pie(counts, values="Count", names="Type",
                     title="🎬 Movies vs TV Shows",
                     color_discrete_sequence=["#E50914", "#221f1f"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ratings = rec.df["rating"].value_counts().head(8).reset_index()
        ratings.columns = ["Rating", "Count"]
        fig = px.bar(ratings, x="Rating", y="Count",
                     title="⭐ Top Ratings",
                     text="Count", color="Rating",
                     color_discrete_sequence=px.colors.sequential.Reds)
        st.plotly_chart(fig, use_container_width=True)

    # Row 2 → Top countries + Release Year Trend
    col3, col4 = st.columns(2)

    with col3:
        countries = rec.df["country"].value_counts().head(10).reset_index()
        countries.columns = ["Country", "Count"]
        fig = px.bar(countries, x="Count", y="Country", orientation="h",
                     title="🌍 Top 10 Countries",
                     text="Count", color="Country",
                     color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        years = rec.df["release_year"].value_counts().sort_index().reset_index()
        years.columns = ["Year", "Count"]
        fig = px.line(years, x="Year", y="Count",
                      title="📅 Titles Released Over Years",
                      markers=True)
        st.plotly_chart(fig, use_container_width=True)

# ---------------- Tab 2: Recommendations ----------------
with tab2:
    st.subheader("Find Similar Titles")

    movie_list = rec.df["title"].dropna().sort_values().unique().tolist()
    selected_movie = st.selectbox("Choose a Movie/Show", movie_list)

    if st.button("Get Recommendations"):
        results = rec.recommend(selected_movie, n=5)

        # Create 5 equal columns for horizontal layout
        cols = st.columns(5)

        for i, r in enumerate(results):
            row = rec.df[rec.df["title"] == r].iloc[0]
            poster_url = get_poster(row["title"])

            with cols[i]:
                if poster_url:
                    st.image(poster_url, use_container_width =True)
                else:
                    st.write("🎬 No poster")

                st.markdown(f"**{row['title']}**")
                st.caption(f"{row['release_year']} • {row['rating']}")
                st.caption(f"{row['listed_in'].split(',')[0]}")
