import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class NetflixRecommender:
    def __init__(self, data_path="data/netflix_titles.csv"):
        try:
            self.df = pd.read_csv(data_path, encoding="utf-8")
        except UnicodeDecodeError:
            self.df = pd.read_csv(data_path, encoding="latin-1")

        self.similarity = None
        self.indices = None
        self._prepare()

    def _prepare(self):
    # Fill missing values
        self.df["listed_in"] = self.df["listed_in"].fillna("")
        self.df["cast"] = self.df["cast"].fillna("")
        self.df["director"] = self.df["director"].fillna("")

    # Combine features into one string
        self.df["combined"] = self.df["listed_in"] + " " + self.df["cast"] + " " + self.df["director"]

    # Vectorize text
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        tfidf = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf.fit_transform(self.df["combined"])

        # Cosine similarity matrix
        self.similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Store titles in lowercase for easier lookup
        self.df["title_lower"] = self.df["title"].str.lower()
        self.indices = pd.Series(self.df.index, index=self.df["title_lower"]).drop_duplicates()

    def recommend(self, title, n=5):
        import difflib
        title = title.lower().strip()

        if title not in self.indices:
        # Suggest closest match
            close_matches = difflib.get_close_matches(title, self.indices.index, n=1, cutoff=0.6)
            if close_matches:
                title = close_matches[0]
            else:
                return ["Title not found in dataset."]

        idx = self.indices[title]
        sim_scores = list(enumerate(self.similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n+1]
        movie_indices = [i[0] for i in sim_scores]

    # ✅ Return proper titles from dataframe, not lowercase ones
        return self.df["title"].iloc[movie_indices].tolist()

    import pandas as pd

    def __init__(self, data_path="data/netflix_titles.csv"):
        try:
            self.df = pd.read_csv(data_path, encoding="utf-8")
        except UnicodeDecodeError:
            self.df = pd.read_csv(data_path, encoding="latin-1")

        self.similarity = None
        self.indices = None
        self._prepare()
