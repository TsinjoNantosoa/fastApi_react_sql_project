from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import pandas as pd
import json
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)
DB_USER = os.getenv("DB_USER", "tsinjo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "nantosoa")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "tsinjo")
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

@app.get("/")
async def root():
    """Route racine de l'API."""
    return {"message": "Welcome to Movies API"}

@app.get("/movies")
async def get_movies(title: str = None):
    """
    Récupère tous les films ou un film spécifique par son titre.
    Si un titre est fourni, filtre par ce titre.
    """
    try:
        if title:
            # Sélectionne un film spécifique par son titre
            query = "SELECT * FROM movies WHERE Series_Title = %s"
            df = pd.read_sql(query, engine, params=(title,))
        else:
            # Sélectionne tous les films de la table
            query = "SELECT * FROM movies"
            df = pd.read_sql(query, engine)
        # Convertit le DataFrame en une liste de dictionnaires
        return df.to_dict(orient='records')
    except Exception as e:
        # Gère les erreurs potentielles lors de l'accès à la base de données
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies-by-year")
async def get_movies_by_year():
    """
    Compte le nombre de films sortis chaque année et les trie par année.
    """
    try:
        # Compte le nombre de films par année de sortie, trié par année
        query = """
            SELECT Released_Year, COUNT(*) AS number_of_movies
            FROM movies
            GROUP BY Released_Year
            ORDER BY Released_Year
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies-by-genre")
async def get_movies_by_genre():
    """
    Compte le nombre de films pour chaque genre.
    """
    try:
        # Compte le nombre de films par genre
        query = """
            SELECT Genre, COUNT(*) AS genre_count
            FROM movies
            GROUP BY Genre
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies-by-rating")
async def get_movies_by_rating():
    """
    Récupère la note IMDB de tous les films.
    """
    try:
        # Sélectionne uniquement la colonne IMDB_Rating pour tous les films
        query = "SELECT IMDB_Rating FROM movies"
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies-by-director")
async def get_movies_by_director():
    """
    Récupère les 10 réalisateurs ayant réalisé le plus de films.
    """
    try:
        # Compte le nombre de films par réalisateur et retourne les 10 premiers par ordre décroissant
        query = """
        SELECT Director, COUNT(*) AS count
        FROM movies
        GROUP BY Director
        ORDER BY count DESC
        LIMIT 10
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-movies")
async def get_top_movies():
    """
    Récupère les 10 films les mieux notés selon IMDB, avec leur titre, note et revenus bruts.
    """
    try:
        # Sélectionne le titre, la note IMDB et les revenus bruts des 10 films les mieux notés
        query = """
        SELECT Series_Title, IMDB_Rating, Gross
        FROM movies
        ORDER BY IMDB_Rating DESC
        LIMIT 10
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies-by-certificate")
async def get_movies_by_certificate():
    """
    Compte le nombre de films par type de classification (Certificate).
    """
    try:
        # Compte le nombre de films pour chaque classification et trie par nombre décroissant
        query = """
        SELECT Certificate, COUNT(*) AS count
        FROM movies
        GROUP BY Certificate
        ORDER BY count DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies-by-runtime")
async def get_movies_by_runtime():
    """
    Récupère les 10 durées de film (Runtime) les plus fréquentes.
    """
    try:
        # Compte le nombre de films par durée et retourne les 10 durées les plus courantes
        query = """
        SELECT Runtime, COUNT(*) AS count
        FROM movies
        GROUP BY Runtime
        ORDER BY count DESC
        LIMIT 10
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Nouvelles routes pour les requêtes avancées
@app.get("/top-gross-by-genre")
async def get_top_gross_by_genre():
    """
    Trouve le film ayant généré le plus de revenus (Gross) pour chaque genre.
    """
    try:
        # Sélectionne le genre, le titre et le revenu brut maximal pour chaque genre, trié par revenu décroissant
        # Note: MySQL peut retourner un titre arbitraire associé au MAX(Gross) dans le groupe.
        query = """
        SELECT Genre, Series_Title, MAX(CAST(REPLACE(Gross, ',', '') AS UNSIGNED)) AS max_gross
        FROM movies
        WHERE Gross IS NOT NULL AND Gross != ''
        GROUP BY Genre
        ORDER BY max_gross DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/top-years-by-movies")
async def get_top_years_by_movies():
    """
    Trouve les 5 années avec le plus grand nombre de sorties de films.
    """
    try:
        # Compte les films par année et retourne les 5 années avec le plus de films
        query = """
        SELECT Released_Year, COUNT(*) AS number_of_movies
        FROM movies
        GROUP BY Released_Year
        ORDER BY number_of_movies DESC
        LIMIT 5
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-rated-high-gross")
async def get_top_rated_high_gross():
    """
    Sélectionne les films très bien notés (IMDB > 8.5) et ayant généré des revenus élevés (Gross > 500, unité non spécifiée).
    Assurez-vous que la colonne Gross est numérique ou correctement castée.
    """
    try:
        # Sélectionne les films avec une note > 8.5 et des revenus > 500 (après conversion), triés par note puis revenus
        query = """
        SELECT Series_Title, IMDB_Rating, Gross
        FROM movies
        WHERE IMDB_Rating > 8.5 AND Gross IS NOT NULL AND Gross != '' AND CAST(REPLACE(Gross, ',', '') AS UNSIGNED) > 50000000  -- Exemple: 50 millions
        ORDER BY IMDB_Rating DESC, CAST(REPLACE(Gross, ',', '') AS UNSIGNED) DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/avg-runtime-by-genre")
async def get_avg_runtime_by_genre():
    """
    Calcule la durée moyenne (en minutes) des films pour chaque genre.
    """
    try:
        # Calcule la durée moyenne par genre, après avoir nettoyé et converti la colonne Runtime
        query = """
        SELECT Genre, AVG(CAST(REPLACE(Runtime, ' min', '') AS UNSIGNED)) AS avg_runtime_minutes
        FROM movies
        WHERE Runtime IS NOT NULL AND Runtime LIKE '% min' -- S'assure que le format est correct
        GROUP BY Genre
        ORDER BY avg_runtime_minutes DESC
        """
        df = pd.read_sql(query, engine)
         # Convertir avg_runtime en entier si nécessaire ou formater
        if 'avg_runtime_minutes' in df.columns:
            df['avg_runtime_minutes'] = df['avg_runtime_minutes'].round().astype(int)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/directors-multiple-genres")
async def get_directors_multiple_genres():
    """
    Trouve les réalisateurs qui ont dirigé des films dans plus d'un genre distinct.
    """
    try:
        # Compte le nombre de genres distincts par réalisateur et filtre ceux avec plus d'un genre
        query = """
        SELECT Director, COUNT(DISTINCT Genre) AS genre_count
        FROM movies
        GROUP BY Director
        HAVING genre_count > 1
        ORDER BY genre_count DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/low-gross-high-rating")
async def get_low_gross_high_rating():
    """
    Trouve les 5 films avec les plus faibles revenus (Gross) parmi ceux ayant une bonne note (IMDB > 7).
    Assurez-vous que la colonne Gross est numérique ou correctement castée.
    """
    try:
        # Sélectionne les 5 films avec note > 7 et les revenus les plus bas (après conversion)
        query = """
        SELECT Series_Title, Gross, IMDB_Rating
        FROM movies
        WHERE Gross IS NOT NULL AND Gross != '' AND IMDB_Rating > 7
        ORDER BY CAST(REPLACE(Gross, ',', '') AS UNSIGNED) ASC
        LIMIT 5
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/popular-genres-by-votes")
async def get_popular_genres_by_votes():
    """
    Trouve les 10 genres les plus populaires en termes de nombre total de votes reçus.
    """
    try:
        # Calcule la somme des votes par genre et retourne les 10 genres avec le plus de votes
        query = """
        SELECT Genre, SUM(No_of_Votes) AS total_votes
        FROM movies
        GROUP BY Genre
        ORDER BY total_votes DESC
        LIMIT 10
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/extreme-runtime-movies")
async def get_extreme_runtime_movies():
    """
    Récupère les 5 films les plus courts et les 5 films les plus longs en termes de durée (Runtime).
    """
    try:
        # Sélectionne les 5 films les plus courts (après conversion de Runtime)
        query_shortest = """
        SELECT Series_Title, Runtime
        FROM movies
        WHERE Runtime IS NOT NULL AND Runtime LIKE '% min'
        ORDER BY CAST(REPLACE(Runtime, ' min', '') AS UNSIGNED) ASC
        LIMIT 5
        """
        df_shortest = pd.read_sql(query_shortest, engine)

        # Sélectionne les 5 films les plus longs (après conversion de Runtime)
        query_longest = """
        SELECT Series_Title, Runtime
        FROM movies
        WHERE Runtime IS NOT NULL AND Runtime LIKE '% min'
        ORDER BY CAST(REPLACE(Runtime, ' min', '') AS UNSIGNED) DESC
        LIMIT 5
        """
        df_longest = pd.read_sql(query_longest, engine)

        return {
            "shortest": df_shortest.to_dict(orient='records'),
            "longest": df_longest.to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/votes-gross-correlation")
async def get_votes_gross_correlation():
    """
    Sélectionne le nombre de votes et les revenus bruts pour une analyse potentielle de corrélation.
    Filtre les entrées où l'une des valeurs est manquante.
    """
    try:
        # Sélectionne les votes et les revenus où les deux sont présents
        query = """
        SELECT No_of_Votes, Gross
        FROM movies
        WHERE No_of_Votes IS NOT NULL AND Gross IS NOT NULL AND Gross != ''
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-rated-by-certificate")
async def get_top_rated_by_certificate():
    """
    Trouve le film le mieux noté pour chaque type de classification (Certificate).
    """
    try:
        # Sélectionne la classification, le titre et la note maximale pour chaque classification, trié par note décroissante
        # Note: MySQL peut retourner un titre arbitraire associé au MAX(IMDB_Rating) dans le groupe.
        query = """
        SELECT Certificate, Series_Title, MAX(IMDB_Rating) AS max_rating
        FROM movies
        WHERE Certificate IS NOT NULL
        GROUP BY Certificate
        ORDER BY max_rating DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-directors-by-rating")
async def get_top_directors_by_rating():
    """
    Trouve les réalisateurs ayant au moins 3 films notés > 8.0.
    Les classe par leur note IMDB moyenne (pour ces films) puis par le nombre de ces films.
    """
    try:
        # Sélectionne les réalisateurs avec >= 3 films notés > 8.0, calcule leur note moyenne et compte leurs films
        query = """
        SELECT Director, COUNT(*) AS number_of_movies, AVG(IMDB_Rating) AS avg_IMDB_rating
        FROM movies
        WHERE IMDB_Rating > 8.0
        GROUP BY Director
        HAVING number_of_movies >= 3
        ORDER BY avg_IMDB_rating DESC, number_of_movies DESC
        """
        df = pd.read_sql(query, engine)
         # Arrondir avg_IMDB_rating à une décimale
        if 'avg_IMDB_rating' in df.columns:
            df['avg_IMDB_rating'] = df['avg_IMDB_rating'].round(1)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/movies-by-year-and-genre")
async def get_movies_by_year_and_genre():
    """
    Compte le nombre de films par année et par genre, trié par année puis par nombre de films.
    """
    try:
        # Compte les films par année et genre, trié par année puis par compte décroissant
        query = """
        SELECT Released_Year, Genre, COUNT(*) AS number_of_movies
        FROM movies
        GROUP BY Released_Year, Genre
        ORDER BY Released_Year, number_of_movies DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mid-range-ratings")
async def get_mid_range_ratings():
    """
    Sélectionne les films dont la note IMDB est comprise entre 7.0 et 8.0 (inclus).
    """
    try:
        # Sélectionne les films avec une note IMDB entre 7 et 8, triés par note décroissante
        query = """
        SELECT Series_Title, IMDB_Rating
        FROM movies
        WHERE IMDB_Rating BETWEEN 7 AND 8
        ORDER BY IMDB_Rating DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/missing-gross-and-runtime")
async def get_missing_gross_and_runtime():
    """
    Trouve les films pour lesquels les revenus bruts (Gross) ou la durée (Runtime) sont manquants.
    """
    try:
        # Sélectionne les titres des films où Gross ou Runtime est NULL ou vide
        query = """
        SELECT Series_Title
        FROM movies
        WHERE Gross IS NULL OR Gross = '' OR Runtime IS NULL OR Runtime = ''
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/top-rated-by-director")
async def get_top_rated_by_director():
    """
    Trouve le film le mieux noté pour chaque réalisateur.
    """
    try:
        # Sélectionne le réalisateur, le titre et la note maximale pour chaque réalisateur, trié par note décroissante
        # Note: MySQL peut retourner un titre arbitraire associé au MAX(IMDB_Rating) dans le groupe.
        query = """
        SELECT Director, Series_Title, MAX(IMDB_Rating) AS max_rating
        FROM movies
        GROUP BY Director
        ORDER BY max_rating DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-gross-by-year")
async def get_top_gross_by_year():
    """
    Trouve le film ayant généré le plus de revenus (Gross) pour chaque année de sortie.
    Assurez-vous que la colonne Gross est numérique ou correctement castée.
    """
    try:
        # Sélectionne l'année, le titre et le revenu maximal pour chaque année, trié par année
        # Note: MySQL peut retourner un titre arbitraire associé au MAX(Gross) dans le groupe.
        query = """
        WITH RankedMovies AS (
            SELECT
                Released_Year,
                Series_Title,
                Gross,
                CAST(REPLACE(Gross, ',', '') AS UNSIGNED) as Gross_Numeric,
                ROW_NUMBER() OVER(PARTITION BY Released_Year ORDER BY CAST(REPLACE(Gross, ',', '') AS UNSIGNED) DESC) as rn
            FROM movies
            WHERE Gross IS NOT NULL AND Gross != '' AND Released_Year IS NOT NULL AND Released_Year != 'PG' -- Exclure les années invalides
              AND Released_Year REGEXP '^[0-9]+$' -- S'assurer que Released_Year est numérique
        )
        SELECT Released_Year, Series_Title, Gross
        FROM RankedMovies
        WHERE rn = 1
        ORDER BY Released_Year;
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/shortest-movies")
async def get_shortest_movies():
    """
    Récupère les 5 films ayant la durée (Runtime) la plus courte.
    """
    try:
        # Sélectionne les 5 films les plus courts (après conversion de Runtime)
        query = """
        SELECT Series_Title, Runtime
        FROM movies
        WHERE Runtime IS NOT NULL AND Runtime LIKE '% min'
        ORDER BY CAST(REPLACE(Runtime, ' min', '') AS UNSIGNED) ASC
        LIMIT 5
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/runtime-vs-rating")
async def get_runtime_vs_rating():
    """
    Sélectionne la durée (Runtime) et la note IMDB pour une analyse potentielle de relation.
    Filtre les entrées où l'une des valeurs est manquante.
    """
    try:
        query = """
            SELECT Runtime, IMDB_Rating
            FROM movies
            WHERE Runtime IS NOT NULL AND Runtime LIKE '% min' AND IMDB_Rating IS NOT NULL
        """
        df = pd.read_sql(query, engine)
        # Optionnel: convertir Runtime en numérique pour le front-end si nécessaire
        # df['Runtime_minutes'] = df['Runtime'].str.replace(' min', '').astype(int)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-grossing-movies")
async def get_top_grossing_movies():
    """
    Récupère les 5 films ayant généré le plus de revenus (Gross) au total.
    Assurez-nous que la colonne Gross est numérique ou correctement castée.
    """
    try:
        # Sélectionne les 5 films avec les revenus les plus élevés (après conversion)
        query = """
            SELECT Series_Title, Gross
            FROM movies
            WHERE Gross IS NOT NULL AND Gross != ''
            ORDER BY CAST(REPLACE(Gross, ',', '') AS UNSIGNED) DESC
            LIMIT 5
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/top-rated-by-genre")
async def get_top_rated_by_genre():
    """
    Sélectionne tous les films ayant une note IMDB, triés d'abord par genre,
    puis par note IMDB décroissante à l'intérieur de chaque genre.
    Utile pour voir les films les mieux notés dans chaque catégorie.
    """
    try:
        # Sélectionne Genre, Titre, Note, trié par Genre puis Note décroissante
        query = """
            SELECT Genre, Series_Title, IMDB_Rating
            FROM movies
            WHERE IMDB_Rating IS NOT NULL
            ORDER BY Genre, IMDB_Rating DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/long-high-rated-movies")
async def get_long_high_rated_movies():
    """
    Trouve les films qui sont à la fois longs (durée > 120 min) et très bien notés (IMDB > 8.0).
    """
    try:
        # Sélectionne les films longs (> 120 min) et très bien notés (> 8.0)
        query = """
            SELECT Series_Title, IMDB_Rating, Runtime
            FROM movies
            WHERE IMDB_Rating > 8 AND Runtime IS NOT NULL AND Runtime LIKE '% min'
              AND CAST(REPLACE(Runtime, ' min', '') AS UNSIGNED) > 120
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/runtime-vs-gross")
async def get_runtime_vs_gross():
    """
    Sélectionne la durée (Runtime) et les revenus bruts (Gross) pour une analyse potentielle de relation.
    Filtre les entrées où l'une des valeurs est manquante ou invalide.
    """
    try:
        # Sélectionne Runtime et Gross où les deux sont présents et valides
        query = """
            SELECT Runtime, Gross
            FROM movies
            WHERE Runtime IS NOT NULL AND Runtime LIKE '% min'
              AND Gross IS NOT NULL AND Gross != ''
        """
        df = pd.read_sql(query, engine)
         # Optionnel: convertir Runtime et Gross en numérique pour le front-end
        # df['Runtime_minutes'] = df['Runtime'].str.replace(' min', '').astype(int)
        # df['Gross_numeric'] = df['Gross'].str.replace(',', '').astype(int)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/genre-meta-scores")
async def get_genre_meta_scores():
    """
    Sélectionne le genre et le Metascore pour les 10 premiers films trouvés
    ayant un Metascore non nul. L'ordre n'est pas garanti sans ORDER BY.
    """
    try:
        # Sélectionne Genre et Metascore pour 10 films avec un Metascore
        query = """
            SELECT Genre, Meta_score
            FROM movies
            WHERE Meta_score IS NOT NULL LIMIT 10
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/yearly-avg-ratings")
async def get_yearly_avg_ratings():
    """
    Calcule la note IMDB moyenne des films pour chaque année de sortie.
    """
    try:
        # Calcule la note IMDB moyenne par année, trié par année
        query = """
            SELECT Released_Year, AVG(IMDB_Rating) AS avg_IMDB_rating
            FROM movies
            WHERE IMDB_Rating IS NOT NULL AND Released_Year IS NOT NULL AND Released_Year != 'PG' -- Exclure invalides
              AND Released_Year REGEXP '^[0-9]+$' -- S'assurer que c'est numérique
            GROUP BY Released_Year
            ORDER BY Released_Year
        """
        df = pd.read_sql(query, engine)
         # Arrondir avg_IMDB_rating à une décimale
        if 'avg_IMDB_rating' in df.columns:
            df['avg_IMDB_rating'] = df['avg_IMDB_rating'].round(1)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/highly-rated-popular-movies")
async def get_highly_rated_popular_movies():
    """
    Trouve les 5 films les mieux notés (IMDB > 8.0) parmi ceux qui sont aussi très populaires
    (plus de 500 000 votes).
    """
    try:
        # Sélectionne les 5 films les mieux notés (> 8.0) avec plus de 500k votes
        query = """
            SELECT Series_Title, IMDB_Rating, No_of_Votes
            FROM movies
            WHERE IMDB_Rating > 8.0 AND No_of_Votes > 500000
            ORDER BY IMDB_Rating DESC
            LIMIT 5
        """
        df = pd.read_sql(query, engine)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Lance l'application Uvicorn, la rendant accessible sur le réseau
    uvicorn.run(app, host="0.0.0.0", port=8000)