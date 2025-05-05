# import streamlit as st
# import requests
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go 
# import os
# import json 
# from dotenv import load_dotenv
# import math 

# load_dotenv() 
# # Utiliser localhost par défaut si la variable d'environnement n'est pas définie
# BACKEND_URL = os.getenv("FASTAPI_BACKEND_URL", "http://127.0.0.1:8000")
# @st.cache_data(ttl=600) 
# def fetch_data(endpoint, params=None):
#     """Récupère les données depuis le backend FastAPI."""
#     url = f"{BACKEND_URL}/{endpoint}"
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status() # Lever une HTTPError pour les mauvaises réponses (4xx ou 5xx)
#         # Essayer de parser le JSON
#         data = response.json()
#         return data
#     except requests.exceptions.RequestException as e:
#         st.error(f"❌ Erreur réseau lors de la récupération des données depuis {url}: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         st.error(f"❌ Erreur de décodage JSON depuis {url}. Statut: {response.status_code}. Réponse: {response.text[:500]}...")
#         return None
#     except Exception as e: # Capturer toute autre erreur inattendue
#         st.error(f"❌ Une erreur inattendue s'est produite lors de la récupération de {url}: {e}")
#         return None

# # --- Assistants de Traitement de Données ---
# def clean_gross(df, column='Gross'):
#     """Nettoie la colonne Gross (supprime les virgules, convertit en numérique). Gère les erreurs potentielles."""
#     if column in df.columns:
#         # S'assurer que la colonne est de type chaîne d'abord, remplir les NaN avec une chaîne vide temporairement
#         df[column] = df[column].fillna('').astype(str)
#         # Supprimer les virgules et les espaces superflus
#         df[column] = df[column].str.replace(',', '', regex=False).str.strip()
#         # Convertir en numérique, en forçant les erreurs en NaN. Gérer les chaînes vides potentielles après le nettoyage.
#         df[column+'_Numeric'] = pd.to_numeric(df[column].replace('', None), errors='coerce')
#     return df

# def clean_runtime(df, column='Runtime'):
#     """Nettoie la colonne Runtime (supprime ' min', convertit en numérique). Gère les erreurs potentielles."""
#     if column in df.columns:
#         # S'assurer que la colonne est de type chaîne d'abord, remplir les NaN avec une chaîne vide temporairement
#         df[column] = df[column].fillna('').astype(str)
#         # Extraire la partie numérique en supposant le suffixe ' min'
#         df[column+'_Minutes'] = df[column].str.extract(r'(\d+)').iloc[:, 0]
#         # Convertir les chiffres extraits en numérique, en forçant les erreurs en NaN
#         df[column+'_Minutes'] = pd.to_numeric(df[column+'_Minutes'], errors='coerce')
#     return df

# # --- Mise en Page de l'Application Streamlit ---
# st.set_page_config(layout="wide", page_title="Explorateur de Données Cinématographiques") # Utiliser une mise en page large et définir le titre
# st.title("🎬 Explorateur de Données Cinématographiques")

# # --- Initialiser l'État de Session (Si nécessaire pour d'autres fonctionnalités) ---
# # Pour la pagination dans la section "Aperçu"
# if 'current_page_apercu' not in st.session_state:
#     st.session_state.current_page_apercu = 1

# # --- Navigation de la Barre Latérale ---
# st.sidebar.header("📊 Sections d'Analyse")
# analysis_options = [
#     "Aperçu",
#     "Films par Année",
#     "Films par Genre",
#     "Films les Mieux Notés",
#     "Films aux Plus Grosses Recettes",
#     "Infos Réalisateurs",
#     "Analyse de la Durée",
#     "Analyse des Notes",
#     "Analyse des Certificats",
#     "Requêtes Avancées & Corrélations"
# ]
# # Utiliser selectbox pour un look plus propre si beaucoup d'options
# selected_analysis = st.sidebar.selectbox("Choisir l'analyse :", analysis_options)

# # --- Zone de Contenu Principal ---

# # --- Section Aperçu ---
# if selected_analysis == "Aperçu":
#     st.header("Aperçu du Tableau de Bord")
#     st.markdown("Bienvenue ! Sélectionnez une analyse dans la barre latérale pour explorer le jeu de données des films.")

#     # Récupérer le nombre total de films (en utilisant le compte du endpoint /movies)
#     all_movies_data = fetch_data("movies")
#     if all_movies_data:
#         df_all = pd.DataFrame(all_movies_data)

#         if not df_all.empty:
#             total_movies = len(df_all)
#             unique_genres = df_all['Genre'].nunique()
#             # S'assurer que IMDB_Rating est numérique avant de calculer la moyenne
#             df_all['IMDB_Rating'] = pd.to_numeric(df_all['IMDB_Rating'], errors='coerce')
#             avg_rating = df_all['IMDB_Rating'].mean() # Recalculer après conversion
#             unique_directors = df_all['Director'].nunique()

#             col1, col2, col3, col4 = st.columns(4)
#             col1.metric("Total des Films", f"{total_movies:,}")
#             col2.metric("Genres Uniques", f"{unique_genres}")
#             col3.metric("Note IMDB Moyenne", f"{avg_rating:.1f} ⭐" if pd.notna(avg_rating) else "N/A")
#             col4.metric("Réalisateurs Uniques", f"{unique_directors}")

#             st.subheader("Exemple de Données de Films")

#             # --- LOGIQUE DE PAGINATION ---
#             items_per_page = 20 
#             total_items = len(df_all)
#             total_pages = math.ceil(total_items / items_per_page)

#             # Assurer que la page actuelle reste valide si les données changent
#             if st.session_state.current_page_apercu > total_pages:
#                 st.session_state.current_page_apercu = total_pages
#             if st.session_state.current_page_apercu < 1:
#                  st.session_state.current_page_apercu = 1

#             start_idx = (st.session_state.current_page_apercu - 1) * items_per_page
#             end_idx = start_idx + items_per_page
#             df_all_display = df_all.iloc[start_idx:end_idx]

#             st.dataframe(df_all_display) # Afficher la tranche de la page actuelle

#             # --- Contrôles de Pagination ---
#             if total_pages > 1:
#                 col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])

#                 with col_nav1:
#                     if st.button("⬅️ Précédent", key="prev_apercu", disabled=(st.session_state.current_page_apercu <= 1)):
#                         st.session_state.current_page_apercu -= 1
#                         st.rerun() # Recharger la page pour afficher la nouvelle page

#                 with col_nav2:
#                     st.markdown(f"<p style='text-align: center;'>Page {st.session_state.current_page_apercu} sur {total_pages}</p>", unsafe_allow_html=True)

#                 with col_nav3:
#                     if st.button("Suivant ➡️", key="next_apercu", disabled=(st.session_state.current_page_apercu >= total_pages)):
#                         st.session_state.current_page_apercu += 1
#                         st.rerun() # Recharger la page pour afficher la nouvelle page
#             # --- FIN LOGIQUE DE PAGINATION ---

#         else:
#             st.warning("Aucun film trouvé dans les données récupérées.")
#     else:
#         st.warning("Impossible de récupérer les données d'aperçu.")


# # --- Section Films par Année ---
# elif selected_analysis == "Films par Année":
#     st.header("Films Sortis par Année")
#     data = fetch_data("movies-by-year")
#     if data:
#         df = pd.DataFrame(data)

#         # Gérer et nettoyer robustement 'Released_Year'
#         df['Released_Year_Numeric'] = pd.to_numeric(df['Released_Year'], errors='coerce')
#         df_valid_years = df.dropna(subset=['Released_Year_Numeric'])
#         df_valid_years['Released_Year_Numeric'] = df_valid_years['Released_Year_Numeric'].astype(int)
#         df_valid_years = df_valid_years.sort_values("Released_Year_Numeric")

#         if not df_valid_years.empty:
#             fig = px.line(df_valid_years, x='Released_Year_Numeric', y='number_of_movies',
#                           title="Nombre de Films Sortis au Fil du Temps",
#                           labels={'Released_Year_Numeric': 'Année', 'number_of_movies': 'Nombre de Films'})
#             fig.update_layout(hovermode="x unified")
#             st.plotly_chart(fig, use_container_width=True)

#             # --- Fonctionnalité d'exploration (Exemple avec un curseur) ---
#             st.subheader("Explorer Année(s) Spécifique(s)")
#             valid_years = sorted(df_valid_years['Released_Year_Numeric'].unique())
#             if len(valid_years) > 1:
#                 selected_years_range = st.select_slider(
#                     "Sélectionnez une plage d'années pour voir les films :",
#                     options=valid_years,
#                     value=(min(valid_years), max(valid_years)) # Plage par défaut
#                 )
#                 start_year, end_year = selected_years_range
#                 st.write(f"Récupération des films sortis entre {start_year} et {end_year}...")

#                 # Récupérer tous les films UNIQUEMENT SI nécessaire pour l'exploration (envisager le filtrage backend)
#                 all_movies_data_year_explore = fetch_data("movies") # Renommé pour éviter conflit
#                 if all_movies_data_year_explore:
#                     df_all_year = pd.DataFrame(all_movies_data_year_explore)
#                     df_all_year['Released_Year_Numeric'] = pd.to_numeric(df_all_year['Released_Year'], errors='coerce')
#                     df_all_year = df_all_year.dropna(subset=['Released_Year_Numeric'])
#                     df_all_year['Released_Year_Numeric'] = df_all_year['Released_Year_Numeric'].astype(int)

#                     filtered_movies = df_all_year[
#                         (df_all_year['Released_Year_Numeric'] >= start_year) &
#                         (df_all_year['Released_Year_Numeric'] <= end_year)
#                     ]
#                     st.dataframe(filtered_movies[['Series_Title', 'Released_Year', 'Genre', 'IMDB_Rating']])
#                 else:
#                     st.warning("Impossible de récupérer la liste complète des films pour l'exploration.")
#             elif len(valid_years) == 1:
#                 st.info(f"Seules les données pour l'année {valid_years[0]} sont disponibles.")
#             else:
#                  st.warning("Aucune donnée d'année valide trouvée à afficher.")

#         else:
#              st.warning("Aucune donnée d'année valide à tracer.")
#         # Afficher les films avec des années invalides s'il y en a
#         invalid_year_movies = df[df['Released_Year_Numeric'].isna()]
#         if not invalid_year_movies.empty:
#             with st.expander("Films avec des entrées 'Released_Year' invalides"):
#                 st.dataframe(invalid_year_movies)

#     else:
#         st.warning("Impossible de récupérer les données pour les films par année.")

# # --- Section Films par Genre ---
# elif selected_analysis == "Films par Genre":
#     st.header("Nombre de Films par Genre")
#     data = fetch_data("movies-by-genre")
#     if data:
#         df = pd.DataFrame(data).sort_values("genre_count", ascending=False)

#         fig = px.bar(df, x='Genre', y='genre_count', title="Nombre de Films par Genre",
#                      labels={'genre_count': 'Nombre de Films'}, text_auto=True)
#         fig.update_layout(xaxis_title="Genre", yaxis_title="Nombre de Films")
#         st.plotly_chart(fig, use_container_width=True)

#         # --- Fonctionnalité d'exploration (Utilisation de Selectbox) ---
#         st.subheader("Explorer les Films les Mieux Notés pour un Genre Spécifique")
#         genres = ["--Sélectionner le Genre--"] + df['Genre'].tolist()
#         selected_genre = st.selectbox("Sélectionner le Genre :", options=genres)

#         if selected_genre and selected_genre != "--Sélectionner le Genre--":
#             st.write(f"Récupération des films les mieux notés pour **{selected_genre}**...")
#             # OPTION 1 : Récupérer tous les films et filtrer (si le backend ne filtre pas)
#             all_movies_data_genre_explore = fetch_data("movies") # Renommé pour éviter conflit
#             if all_movies_data_genre_explore:
#                 df_all_genre = pd.DataFrame(all_movies_data_genre_explore)
#                 df_all_genre['IMDB_Rating'] = pd.to_numeric(df_all_genre['IMDB_Rating'], errors='coerce') # Assurer le type numérique
#                 genre_movies = df_all_genre[df_all_genre['Genre'] == selected_genre].sort_values('IMDB_Rating', ascending=False)
#                 if not genre_movies.empty:
#                     st.dataframe(genre_movies[['Series_Title', 'IMDB_Rating', 'Released_Year', 'Director']].head(20)) # Afficher plus
#                 else:
#                     st.info(f"Aucun film trouvé pour le genre '{selected_genre}' dans les données récupérées.")
#             else:
#                 st.warning("Impossible de récupérer les détails des films pour le genre sélectionné.")
#             # OPTION 2 : Si le backend supporte le filtrage : fetch_data("movies", params={'genre': selected_genre})

#         # Genres Populaires par Votes
#         st.subheader("Top 10 des Genres les Plus Populaires par Nombre Total de Votes")
#         data_popular = fetch_data("popular-genres-by-votes")
#         if data_popular:
#             df_popular = pd.DataFrame(data_popular)
#             fig_popular = px.bar(df_popular, x='Genre', y='total_votes', title="Top 10 des Genres par Nombre Total de Votes",
#                                  labels={'total_votes': 'Nombre Total de Votes'})
#             st.plotly_chart(fig_popular, use_container_width=True)
#         else:
#             st.warning("Impossible de récupérer les données des genres populaires par votes.")

# # --- Section Films les Mieux Notés ---
# elif selected_analysis == "Films les Mieux Notés":
#     st.header("Top 10 des Films les Mieux Notés (IMDB)")
#     data = fetch_data("top-movies")
#     if data:
#         df = pd.DataFrame(data)
#         df = clean_gross(df, 'Gross') # Nettoyer la colonne Gross pour les données au survol
#         df['IMDB_Rating'] = pd.to_numeric(df['IMDB_Rating'], errors='coerce') # Assurer le type numérique
#         df = df.dropna(subset=['IMDB_Rating']) # Supprimer les lignes où la note n'est pas valide

#         if not df.empty:
#             fig = px.bar(df.sort_values('IMDB_Rating', ascending=True), # Trier pour le graphique à barres horizontales
#                          x='IMDB_Rating', y='Series_Title', orientation='h',
#                          title="Top 10 des Films par Note IMDB",
#                          labels={'IMDB_Rating': 'Note IMDB', 'Series_Title': 'Titre du Film'},
#                          hover_data=['Gross']) # Afficher la chaîne Gross originale au survol
#             fig.update_layout(yaxis={'categoryorder':'total ascending'}) # Conserver l'ordre trié
#             st.plotly_chart(fig, use_container_width=True)
#             st.dataframe(df[['Series_Title', 'IMDB_Rating', 'Gross']]) # Afficher le tableau de données
#         else:
#             st.info("Aucun film avec note valide trouvé pour cette section.")

#     else:
#         st.warning("Impossible de récupérer les données des films les mieux notés.")


# # --- Section Films aux Plus Grosses Recettes ---
# elif selected_analysis == "Films aux Plus Grosses Recettes":
#     st.header("Top 5 des Films aux Plus Grosses Recettes")
#     data = fetch_data("top-grossing-movies")
#     if data:
#         df = pd.DataFrame(data)
#         df = clean_gross(df, 'Gross') # Nettoyer et créer Gross_Numeric
#         df = df.dropna(subset=['Gross_Numeric']) # S'assurer que nous avons des valeurs de recettes numériques
#         df = df.sort_values('Gross_Numeric', ascending=False) # Trier par valeur numérique

#         if not df.empty:
#             fig = px.bar(df.head(5).sort_values('Gross_Numeric', ascending=True), # Trier pour l'affichage en barres horizontales
#                         x='Gross_Numeric', y='Series_Title', orientation='h',
#                         title="Top 5 des Films par Recettes Brutes",
#                         labels={'Gross_Numeric': 'Recettes Brutes (Estimées USD)', 'Series_Title': 'Titre du Film'},
#                         text='Gross' # Afficher la chaîne gross originale sur les barres
#                         )
#             fig.update_layout(xaxis_title="Recettes Brutes (Estimées USD)", yaxis_title="Titre du Film", yaxis={'categoryorder':'total ascending'})
#             st.plotly_chart(fig, use_container_width=True)
#             st.dataframe(df.head(5)[['Series_Title', 'Gross']]) # Afficher le top 5 dans un tableau
#         else:
#             st.info("Aucune donnée de recettes brutes valide trouvée pour les films aux plus grosses recettes.")
#     else:
#         st.warning("Impossible de récupérer les données des films aux plus grosses recettes.")

# # --- Section Infos Réalisateurs ---
# elif selected_analysis == "Infos Réalisateurs":
#     st.header("Infos Réalisateurs")
#     st.subheader("Top 10 des Réalisateurs par Nombre de Films dans le Jeu de Données")
#     data_top_directors = fetch_data("movies-by-director")
#     if data_top_directors:
#         df_directors = pd.DataFrame(data_top_directors)
#         if not df_directors.empty:
#             fig = px.bar(df_directors.sort_values('count'), x='count', y='Director', orientation='h',
#                          title="Top 10 des Réalisateurs par Nombre de Films",
#                          labels={'count': 'Nombre de Films'}, text_auto=True)
#             fig.update_layout(yaxis_title="Réalisateur", xaxis_title="Nombre de Films", yaxis={'categoryorder':'total ascending'})
#             st.plotly_chart(fig, use_container_width=True)

#             # --- Exploration par Réalisateur ---
#             st.subheader("Explorer les Films d'un Réalisateur Spécifique")
#             directors_list = ["--Sélectionner le Réalisateur--"] + sorted(df_directors['Director'].unique().tolist()) # Utiliser une liste triée
#             selected_director = st.selectbox("Sélectionner le réalisateur :", options=directors_list)

#             if selected_director and selected_director != "--Sélectionner le Réalisateur--":
#                 st.write(f"Récupération des films réalisés par **{selected_director}**...")
#                 # Récupérer TOUS les films et filtrer (modifier si le backend supporte le filtrage par réalisateur)
#                 all_movies_data_director_explore = fetch_data("movies") # Renommé pour éviter conflit
#                 if all_movies_data_director_explore:
#                      df_all_dir = pd.DataFrame(all_movies_data_director_explore)
#                      df_all_dir['IMDB_Rating'] = pd.to_numeric(df_all_dir['IMDB_Rating'], errors='coerce') # Assurer le type numérique
#                      director_movies = df_all_dir[df_all_dir['Director'] == selected_director].sort_values('IMDB_Rating', ascending=False)
#                      if not director_movies.empty:
#                          st.dataframe(director_movies[['Series_Title', 'IMDB_Rating', 'Genre', 'Released_Year', 'Runtime', 'Gross']])
#                      else:
#                          st.info(f"Aucun film trouvé pour le réalisateur '{selected_director}' dans les données récupérées.")
#                 else:
#                      st.warning("Impossible de récupérer les détails des films pour le réalisateur sélectionné.")
#         else:
#             st.info("Aucune donnée de réalisateur trouvée.")


#     st.subheader("Réalisateurs avec Plusieurs Films Bien Notés (>= 3 films avec Note > 8.0)")
#     data_high_rated = fetch_data("top-directors-by-rating")
#     if data_high_rated:
#         df_high_rated = pd.DataFrame(data_high_rated)
#         st.dataframe(df_high_rated)
#     else:
#         st.warning("Impossible de récupérer les données des meilleurs réalisateurs par note.")

#     st.subheader("Réalisateurs Ayant Réalisé des Films dans Plusieurs Genres")
#     data_multi_genre = fetch_data("directors-multiple-genres")
#     if data_multi_genre:
#         df_multi_genre = pd.DataFrame(data_multi_genre).sort_values("genre_count", ascending=False)
#         st.dataframe(df_multi_genre)
#     else:
#         st.warning("Impossible de récupérer les données des réalisateurs avec plusieurs genres.")

#     st.subheader("Film le Mieux Noté pour Chaque Réalisateur (Exemple)")
#     data_top_rated_dir = fetch_data("top-rated-by-director") # Récupère un film le mieux noté par réalisateur
#     if data_top_rated_dir:
#          # Afficher potentiellement de nombreux réalisateurs pourrait encombrer, montrer un échantillon ou rendre extensible
#          df_top_rated_dir = pd.DataFrame(data_top_rated_dir)
#          with st.expander("Voir le Film le Mieux Noté par Réalisateur (Exemple - Top 50 affichés)"):
#               st.dataframe(df_top_rated_dir.head(50))
#     else:
#          st.warning("Impossible de récupérer les données du film le mieux noté par réalisateur.")


# # --- Section Analyse de la Durée ---
# elif selected_analysis == "Analyse de la Durée":
#     st.header("Analyse de la Durée")
#     st.subheader("Distribution des Durées des Films")
#     all_movies_data_runtime = fetch_data("movies") # Besoin de tous les films pour la distribution
#     if all_movies_data_runtime:
#         df_all_run = pd.DataFrame(all_movies_data_runtime)
#         df_all_run = clean_runtime(df_all_run, 'Runtime') # Nettoyer et créer Runtime_Minutes
#         df_runtime_valid = df_all_run.dropna(subset=['Runtime_Minutes']) # Supprimer les films dont la durée n'a pas pu être analysée

#         if not df_runtime_valid.empty:
#             fig = px.histogram(df_runtime_valid, x='Runtime_Minutes', nbins=50,
#                                title="Distribution des Durées des Films",
#                                labels={'Runtime_Minutes': 'Durée (Minutes)'})
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.warning("Aucune donnée de durée valide trouvée pour le graphique de distribution.")

#         # Afficher les plus courts/longs
#         st.subheader("Films les Plus Courts et les Plus Longs")
#         # Utiliser le point de terminaison spécifique si disponible, sinon calculer à partir de df_all
#         data_extreme = fetch_data("extreme-runtime-movies") # Utilise le point de terminaison spécifique
#         if data_extreme:
#              # Vérifier si les clés existent et sont des listes
#             shortest_movies = data_extreme.get("shortest") if isinstance(data_extreme.get("shortest"), list) else []
#             longest_movies = data_extreme.get("longest") if isinstance(data_extreme.get("longest"), list) else []

#             col1, col2 = st.columns(2)
#             with col1:
#                 st.write("**Top 5 des Films les Plus Courts**")
#                 if shortest_movies:
#                     st.dataframe(pd.DataFrame(shortest_movies))
#                 else:
#                     st.info("Aucune donnée sur les films les plus courts retournée par le point de terminaison.")
#             with col2:
#                 st.write("**Top 5 des Films les Plus Longs**")
#                 if longest_movies:
#                     st.dataframe(pd.DataFrame(longest_movies))
#                 else:
#                     st.info("Aucune donnée sur les films les plus longs retournée par le point de terminaison.")
#         else:
#              st.warning("Impossible de récupérer les données pour les durées extrêmes des films.")

#         # Top 10 des Durées les Plus Fréquentes
#         st.subheader("Top 10 des Durées les Plus Fréquentes")
#         data_freq_runtime = fetch_data("movies-by-runtime")
#         if data_freq_runtime:
#             df_freq = pd.DataFrame(data_freq_runtime)
#             st.dataframe(df_freq)
#             # Optionnel : Graphique à barres
#             # fig_freq = px.bar(df_freq, x='Runtime', y='count', title="Top 10 des Durées les Plus Fréquentes")
#             # st.plotly_chart(fig_freq)
#         else:
#             st.warning("Impossible de récupérer les données pour les durées fréquentes.")

#         # Durée Moyenne par Genre
#         st.subheader("Durée Moyenne par Genre")
#         data_avg_runtime = fetch_data("avg-runtime-by-genre")
#         if data_avg_runtime:
#             df_avg = pd.DataFrame(data_avg_runtime).sort_values("avg_runtime_minutes", ascending=False)
#             if not df_avg.empty:
#                 fig_avg = px.bar(df_avg, x='Genre', y='avg_runtime_minutes',
#                                 title="Durée Moyenne des Films par Genre",
#                                 labels={'avg_runtime_minutes': 'Durée Moyenne (Minutes)'}, text_auto=True)
#                 st.plotly_chart(fig_avg, use_container_width=True)
#             else:
#                 st.info("Aucune donnée de durée moyenne par genre à afficher.")
#         else:
#             st.warning("Impossible de récupérer les données de durée moyenne par genre.")

#     else:
#         st.warning("Impossible de récupérer les données de base des films pour l'analyse de la durée.")


# # --- Section Analyse des Notes ---
# elif selected_analysis == "Analyse des Notes":
#     st.header("Analyse des Notes")
#     st.subheader("Distribution des Notes IMDB")
#     all_movies_data_rating = fetch_data("movies") # Besoin de tous les films
#     if all_movies_data_rating:
#         df_all_rate = pd.DataFrame(all_movies_data_rating)
#         df_all_rate['IMDB_Rating'] = pd.to_numeric(df_all_rate['IMDB_Rating'], errors='coerce') # Assurer le type numérique
#         df_rating_valid = df_all_rate.dropna(subset=['IMDB_Rating'])

#         if not df_rating_valid.empty:
#             fig = px.histogram(df_rating_valid, x='IMDB_Rating', nbins=30,
#                                title="Distribution des Notes IMDB",
#                                labels={'IMDB_Rating': 'Note IMDB'})
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#              st.warning("Aucune donnée de note IMDB valide trouvée pour le graphique de distribution.")

#         # Notes Moyennes
#         st.subheader("Films avec des Notes Moyennes (7.0 à 8.0)")
#         data_mid_range = fetch_data("mid-range-ratings")
#         if data_mid_range:
#              df_mid = pd.DataFrame(data_mid_range)
#              with st.expander(f"Voir les {len(df_mid)} Films avec une Note IMDB entre 7.0 et 8.0"):
#                  st.dataframe(df_mid)
#         else:
#              st.warning("Impossible de récupérer les données des films de note moyenne.")

#         # Faibles Recettes Haute Note
#         st.subheader("Top 5 des Films à Faibles Recettes avec Bonne Note (> 7.0)")
#         data_low_gross = fetch_data("low-gross-high-rating")
#         if data_low_gross:
#              df_low_gross = pd.DataFrame(data_low_gross)
#              st.dataframe(df_low_gross)
#         else:
#             st.warning("Impossible de récupérer les données des films à faibles recettes / haute note.")


#         st.subheader("Note IMDB Moyenne par Année")
#         data_yearly_avg = fetch_data("yearly-avg-ratings")
#         if data_yearly_avg:
#             df_yearly = pd.DataFrame(data_yearly_avg)
#             # S'assurer que l'année est numérique pour le tracé
#             df_yearly['Released_Year_Numeric'] = pd.to_numeric(df_yearly['Released_Year'], errors='coerce')
#             df_yearly = df_yearly.dropna(subset=['Released_Year_Numeric', 'avg_IMDB_rating']) # S'assurer que la note est aussi valide
#             df_yearly['Released_Year_Numeric'] = df_yearly['Released_Year_Numeric'].astype(int)
#             df_yearly = df_yearly.sort_values('Released_Year_Numeric')

#             if not df_yearly.empty:
#                 fig_yearly = px.line(df_yearly, x='Released_Year_Numeric', y='avg_IMDB_rating',
#                                     title="Note IMDB Moyenne au Fil du Temps",
#                                     labels={'Released_Year_Numeric': 'Année', 'avg_IMDB_rating': 'Note IMDB Moyenne'})
#                 fig_yearly.update_layout(hovermode="x unified")
#                 st.plotly_chart(fig_yearly, use_container_width=True)
#             else:
#                 st.warning("Aucune donnée valide pour le graphique des notes moyennes annuelles.")
#         else:
#             st.warning("Impossible de récupérer les données des notes moyennes annuelles.")
#     else:
#         st.warning("Impossible de récupérer les données de base des films pour l'analyse des notes.")

# # --- Section Analyse des Certificats ---
# elif selected_analysis == "Analyse des Certificats":
#     st.header("Analyse des Certificats des Films")

#     st.subheader("Nombre de Films par Certificat")
#     data_cert_count = fetch_data("movies-by-certificate")
#     if data_cert_count:
#         df_cert = pd.DataFrame(data_cert_count)
#         # Gérer les valeurs None potentielles dans Certificate avant le tracé
#         df_cert['Certificate'] = df_cert['Certificate'].fillna('Non Classé/Inconnu')
#         df_cert = df_cert.sort_values("count", ascending=False)

#         if not df_cert.empty:
#             fig_cert = px.bar(df_cert, x='Certificate', y='count', title="Nombre de Films par Certificat",
#                               labels={'count': 'Nombre de Films'}, text_auto=True)
#             st.plotly_chart(fig_cert, use_container_width=True)
#         else:
#             st.info("Aucune donnée de certificat trouvée.")
#     else:
#         st.warning("Impossible de récupérer le nombre de films par certificat.")

#     st.subheader("Film le Mieux Noté par Certificat")
#     data_top_cert = fetch_data("top-rated-by-certificate")
#     if data_top_cert:
#         df_top_cert = pd.DataFrame(data_top_cert)
#         df_top_cert['Certificate'] = df_top_cert['Certificate'].fillna('Non Classé/Inconnu')
#         st.dataframe(df_top_cert)
#     else:
#         st.warning("Impossible de récupérer le film le mieux noté par certificat.")


# # --- Section Requêtes Avancées & Corrélations ---
# elif selected_analysis == "Requêtes Avancées & Corrélations":
#     st.header("Requêtes Avancées & Corrélations")

#     # --- Graphiques de Corrélation ---
#     # On récupère toutes les données une seule fois pour les corrélations si possible
#     # Note: Cela peut être lent si le dataset est très grand.
#     # Il serait plus efficace d'avoir des endpoints spécifiques pour ces corrélations
#     # ou de récupérer uniquement les colonnes nécessaires.
#     # Ici, on suppose que les endpoints spécifiques existent comme dans le code original.
#     col_corr1, col_corr2, col_corr3 = st.columns(3)

#     with col_corr1:
#         st.subheader("Votes vs Recettes Brutes")
#         data_corr_vg = fetch_data("votes-gross-correlation") # Utilise l'endpoint spécifique
#         if data_corr_vg:
#             df_corr_vg = pd.DataFrame(data_corr_vg)
#             df_corr_vg = clean_gross(df_corr_vg, 'Gross')
#             df_corr_vg['No_of_Votes'] = pd.to_numeric(df_corr_vg['No_of_Votes'], errors='coerce')
#             df_corr_vg = df_corr_vg.dropna(subset=['Gross_Numeric', 'No_of_Votes'])

#             if not df_corr_vg.empty:
#                 fig_corr_vg = px.scatter(df_corr_vg, x='No_of_Votes', y='Gross_Numeric',
#                                         title="Votes vs Recettes Brutes",
#                                         labels={'No_of_Votes': 'Votes', 'Gross_Numeric': 'Recettes (USD)'},
#                                         hover_name='Series_Title' if 'Series_Title' in df_corr_vg.columns else None,
#                                         trendline='ols', trendline_color_override="red",
#                                         log_x=True, log_y=True) # L'échelle logarithmique est souvent meilleure
#                 fig_corr_vg.update_layout(xaxis_title="Votes (Échelle Log)", yaxis_title="Recettes (Échelle Log)")
#                 st.plotly_chart(fig_corr_vg, use_container_width=True)
#                 try:
#                     correlation = df_corr_vg['No_of_Votes'].corr(df_corr_vg['Gross_Numeric'])
#                     st.metric("Corrélation de Pearson", f"{correlation:.2f}" if pd.notna(correlation) else "N/A")
#                 except Exception:
#                     st.caption("La corrélation n'a pas pu être calculée.") # Gérer les erreurs potentielles dans corr()
#             else:
#                 st.info("Aucune donnée valide pour la corrélation Votes vs Recettes.")
#         else:
#             st.warning("Impossible de récupérer les données pour la corrélation votes-recettes.")

#     with col_corr2:
#         st.subheader("Durée vs Note")
#         data_corr_rr = fetch_data("runtime-vs-rating") # Utilise l'endpoint spécifique
#         if data_corr_rr:
#             df_corr_rr = pd.DataFrame(data_corr_rr)
#             df_corr_rr = clean_runtime(df_corr_rr, 'Runtime')
#             df_corr_rr['IMDB_Rating'] = pd.to_numeric(df_corr_rr['IMDB_Rating'], errors='coerce')
#             df_corr_rr = df_corr_rr.dropna(subset=['Runtime_Minutes', 'IMDB_Rating'])

#             if not df_corr_rr.empty:
#                 fig_corr_rr = px.scatter(df_corr_rr, x='Runtime_Minutes', y='IMDB_Rating',
#                                         title="Durée vs Note IMDB",
#                                         labels={'Runtime_Minutes': 'Durée (Min)', 'IMDB_Rating': 'Note'},
#                                         hover_name='Series_Title' if 'Series_Title' in df_corr_rr.columns else None,
#                                         trendline='ols', trendline_color_override="red")
#                 st.plotly_chart(fig_corr_rr, use_container_width=True)
#                 try:
#                     correlation_rr = df_corr_rr['Runtime_Minutes'].corr(df_corr_rr['IMDB_Rating'])
#                     st.metric("Corrélation de Pearson", f"{correlation_rr:.2f}" if pd.notna(correlation_rr) else "N/A")
#                 except Exception:
#                      st.caption("La corrélation n'a pas pu être calculée.")
#             else:
#                 st.info("Aucune donnée valide pour la corrélation Durée vs Note.")
#         else:
#             st.warning("Impossible de récupérer les données pour la corrélation durée-note.")

#     with col_corr3:
#         st.subheader("Durée vs Recettes Brutes")
#         data_corr_rg = fetch_data("runtime-vs-gross") # Utilise l'endpoint spécifique
#         if data_corr_rg:
#             df_corr_rg = pd.DataFrame(data_corr_rg)
#             df_corr_rg = clean_runtime(df_corr_rg, 'Runtime')
#             df_corr_rg = clean_gross(df_corr_rg, 'Gross')
#             df_corr_rg = df_corr_rg.dropna(subset=['Runtime_Minutes', 'Gross_Numeric'])

#             if not df_corr_rg.empty:
#                 fig_corr_rg = px.scatter(df_corr_rg, x='Runtime_Minutes', y='Gross_Numeric',
#                                          title="Durée vs Recettes Brutes",
#                                          labels={'Runtime_Minutes': 'Durée (Min)', 'Gross_Numeric': 'Recettes (USD)'},
#                                          hover_name='Series_Title' if 'Series_Title' in df_corr_rg.columns else None,
#                                          log_y=True, # Les recettes nécessitent souvent une échelle log
#                                          trendline='ols', trendline_color_override="red")
#                 fig_corr_rg.update_layout(yaxis_title="Recettes (Échelle Log)")
#                 st.plotly_chart(fig_corr_rg, use_container_width=True)
#                 try:
#                     correlation_rg = df_corr_rg['Runtime_Minutes'].corr(df_corr_rg['Gross_Numeric'])
#                     st.metric("Corrélation de Pearson", f"{correlation_rg:.2f}" if pd.notna(correlation_rg) else "N/A")
#                 except Exception:
#                     st.caption("La corrélation n'a pas pu être calculée.")
#             else:
#                 st.info("Aucune donnée valide pour la corrélation Durée vs Recettes.")
#         else:
#             st.warning("Impossible de récupérer les données pour la corrélation durée-recettes.")


#     # --- Autres Requêtes Avancées ---
#     st.divider() # Ajouter un séparateur visuel

#     col_adv1, col_adv2 = st.columns(2)

#     with col_adv1:
#         st.subheader("Très Bien Notés & Populaires (Note >8.0, >500k Votes)")
#         data_hrp = fetch_data("highly-rated-popular-movies")
#         if data_hrp:
#             st.dataframe(pd.DataFrame(data_hrp))
#         else:
#             st.warning("Impossible de récupérer les données des films populaires très bien notés.")

#         st.subheader("Films les Mieux Notés par Genre (Exemple)")
#         data_trbg = fetch_data("top-rated-by-genre") # Peut être volumineux !
#         if data_trbg:
#             df_trbg = pd.DataFrame(data_trbg)
#             with st.expander("Voir les Films les Mieux Notés Groupés par Genre (Grand Jeu de Données)"):
#                  st.dataframe(df_trbg)
#         else:
#             st.warning("Impossible de récupérer les données des mieux notés par genre.")

#         st.subheader("Films avec Recettes ou Durée Manquantes")
#         data_missing = fetch_data("missing-gross-and-runtime")
#         if data_missing:
#              df_missing = pd.DataFrame(data_missing)
#              with st.expander(f"Voir {len(df_missing)} Films avec Recettes ou Durée Manquantes"):
#                   st.dataframe(df_missing)
#         else:
#              st.warning("Impossible de récupérer les données sur les recettes/durées manquantes.")


#     with col_adv2:
#         st.subheader("Film aux Plus Grosses Recettes par Genre")
#         data_tgpg = fetch_data("top-gross-by-genre")
#         if data_tgpg:
#             df_tgpg = pd.DataFrame(data_tgpg)
#             st.dataframe(df_tgpg)
#         else:
#             st.warning("Impossible de récupérer les données des plus grosses recettes par genre.")


#         st.subheader("Film aux Plus Grosses Recettes par Année")
#          # ATTENTION : Votre requête backend pourrait retourner un titre arbitraire si plusieurs films ont les mêmes recettes max
#         data_tgpy = fetch_data("top-gross-by-year")
#         if data_tgpy:
#             df_tgpy = pd.DataFrame(data_tgpy)
#             df_tgpy['Released_Year'] = pd.to_numeric(df_tgpy['Released_Year'], errors='coerce')
#             df_tgpy = df_tgpy.dropna(subset=['Released_Year'])
#             df_tgpy['Released_Year'] = df_tgpy['Released_Year'].astype(int)
#             # Le tri peut être nécessaire si le backend ne trie pas
#             st.dataframe(df_tgpy.sort_values('Released_Year'))
#         else:
#             st.warning("Impossible de récupérer les données des plus grosses recettes par année.")

#         st.subheader("Films Longs et Bien Notés (>120min, Note >8.0)")
#         data_long_high = fetch_data("long-high-rated-movies")
#         if data_long_high:
#             st.dataframe(pd.DataFrame(data_long_high))
#         else:
#             st.warning("Impossible de récupérer les données des films longs et bien notés.")



# # --- Pied de Page ou Informations Supplémentaires ---
# st.sidebar.divider()
# st.sidebar.info(f"🌐 API Backend : {BACKEND_URL}")
# st.sidebar.info("ℹ️ Survolez les graphiques pour les détails. Utilisez les widgets sous les graphiques pour explorer.")







import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from dotenv import load_dotenv
import math
import numpy as np # Importé pour np.nan

# Charger les variables d'environnement (si présentes)
load_dotenv()

# Configuration de l'URL du backend
BACKEND_URL = os.getenv("FASTAPI_BACKEND_URL", "http://127.0.0.1:8000")

# --- Fonction de Récupération des Données avec Cache ---
@st.cache_data(ttl=300) # Cache les données pendant 5 minutes
def fetch_data(endpoint, params=None):
    """Récupère les données depuis le backend FastAPI."""
    url = f"{BACKEND_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=20) # Ajout d'un timeout
        response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP
        # Vérifier si la réponse est vide avant de parser le JSON
        if response.text:
            try:
                data = response.json()
                # Gérer le cas spécifique de extreme-runtime-movies retournant un dict
                # et s'assurer que les autres endpoints retournent bien des listes
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and endpoint == "extreme-runtime-movies":
                     return data # Retourner le dict pour ce cas spécifique
                else:
                    st.warning(f"⚠️ Format de données inattendu depuis {url} (type: {type(data)}). Attendu: list.")
                    return [] # Préférable de retourner vide si format inconnu
            except json.JSONDecodeError as e:
                 st.error(f"❌ Erreur décodage JSON depuis {url}. Statut: {response.status_code}. Réponse: {response.text[:500]}...")
                 return None # Erreur de décodage
        else:
            st.warning(f"⚠️ Réponse vide reçue depuis {url}. Statut: {response.status_code}.")
            return [] # Retourner une liste vide pour les réponses vides valides
    except requests.exceptions.Timeout:
        st.error(f"❌ Timeout lors de la connexion à {url}. Le backend est-il lent ou indisponible ?")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Erreur de connexion à {url}. Le backend est-il lancé et accessible ?")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur réseau lors de la récupération depuis {url}: {e}")
        return None
    except Exception as e: # Capturer toute autre erreur inattendue
        st.error(f"❌ Une erreur inattendue s'est produite lors de la récupération de {url}: {e}")
        return None

# --- Assistants de Traitement de Données (Robustes) ---
def robust_clean_gross(df, column='Gross'):
    """Nettoie la colonne Gross et crée Gross_Numeric. Gère divers formats et erreurs."""
    if column not in df.columns: return df
    df = df.copy()
    df[column + '_Str'] = df[column].fillna('').astype(str)
    df[column + '_Numeric'] = pd.to_numeric(
        df[column + '_Str'].str.replace(',', '', regex=False).str.strip(), errors='coerce')
    return df

def robust_clean_runtime(df, column='Runtime'):
    """Nettoie la colonne Runtime et crée Runtime_Minutes. Gère erreurs et formats."""
    if column not in df.columns: return df
    df = df.copy()
    df[column + '_Str'] = df[column].fillna('').astype(str)
    df[column + '_Minutes'] = pd.to_numeric(
        df[column + '_Str'].str.extract(r'(\d+)\s*min', expand=False), errors='coerce')
    return df

# --- Configuration de la Page Streamlit ---
st.set_page_config(layout="wide", page_title="Explorateur de Films", initial_sidebar_state="expanded")
st.title("🎬 Explorateur de Données Cinématographiques")

# --- Récupération initiale de toutes les données ---
@st.cache_data(ttl=600)
def load_all_movies_data():
    all_data = fetch_data("movies")
    if all_data and isinstance(all_data, list):
        df = pd.DataFrame(all_data)
        df = robust_clean_runtime(df, 'Runtime')
        df = robust_clean_gross(df, 'Gross')
        df['IMDB_Rating'] = pd.to_numeric(df['IMDB_Rating'], errors='coerce')
        df['Meta_score'] = pd.to_numeric(df['Meta_score'], errors='coerce')
        df['No_of_Votes'] = pd.to_numeric(df['No_of_Votes'], errors='coerce')
        df['Released_Year_Numeric'] = pd.to_numeric(df['Released_Year'], errors='coerce')
        # Nettoyage colonnes string/catégorielles
        for col in ['Genre', 'Director', 'Certificate', 'Series_Title', 'Poster_Link']:
             if col in df.columns:
                 df[col] = df[col].fillna('Inconnu' if col != 'Poster_Link' else '')
             else: # Ajouter la colonne si elle manque pour éviter les erreurs futures
                 df[col] = 'Inconnu' if col != 'Poster_Link' else ''
        return df
    elif all_data is None:
        st.error("Erreur critique: Impossible de charger les données initiales depuis le backend.")
        return pd.DataFrame()
    else:
        st.warning("Aucune donnée de film initiale reçue ou format incorrect.")
        return pd.DataFrame()

df_all_movies = load_all_movies_data()

# --- Barre Latérale de Navigation ---
st.sidebar.header("📊 Sections d'Analyse")
analysis_options = [
    "Aperçu Général & Données Brutes",
    "Tendances Annuelles",
    "Analyse par Genre",
    "Classement par Note IMDB",
    "Classement par Recettes",
    "Performance des Réalisateurs",
    "Analyse de la Durée",
    "Distribution des Certificats",
    "Requêtes Complexes & Corrélations"
]
selected_analysis = st.sidebar.selectbox("Choisir une section :", analysis_options, key="main_navigation")

# --- Pied de Page / Infos Sidebar ---
st.sidebar.divider()
st.sidebar.info(f"⚙️ API Backend : {BACKEND_URL}")
st.sidebar.caption("© Projet d'Exploration de Données Cinématographiques")


# --- Affichage de la Section Sélectionnée ---

# 1. Aperçu Général & Données Brutes (Landing Page)
if selected_analysis == "Aperçu Général & Données Brutes":
    st.header("📊 Aperçu Général & Données Brutes")
    st.markdown("Bienvenue ! Voici un résumé des données et la table complète des films.")

    if not df_all_movies.empty:
        # Afficher les métriques
        total_movies = len(df_all_movies)
        unique_genres = df_all_movies['Genre'].nunique()
        avg_rating = df_all_movies['IMDB_Rating'].mean()
        unique_directors = df_all_movies['Director'].nunique()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total des Films", f"{total_movies:,}")
        col2.metric("Genres Uniques", f"{unique_genres}")
        col3.metric("Note IMDB Moyenne", f"{avg_rating:.1f} ⭐" if pd.notna(avg_rating) else "N/A")
        col4.metric("Réalisateurs Uniques", f"{unique_directors}")

        st.divider()
        st.subheader("Table Complète des Données de Films")

        # --- PAGINATION pour la table principale ---
        items_per_page_main = 20
        total_items_main = len(df_all_movies)
        total_pages_main = math.ceil(total_items_main / items_per_page_main) if total_items_main > 0 else 1

        if 'current_page_main' not in st.session_state: st.session_state.current_page_main = 1
        st.session_state.current_page_main = max(1, min(st.session_state.current_page_main, total_pages_main))

        start_idx_main = (st.session_state.current_page_main - 1) * items_per_page_main
        end_idx_main = start_idx_main + items_per_page_main
        df_display_main = df_all_movies.iloc[start_idx_main:end_idx_main]

        # Configuration dynamique des colonnes (si Poster_Link existe)
        column_config_main = {}
        if 'Poster_Link' in df_display_main.columns:
             column_config_main["Poster_Link"] = st.column_config.ImageColumn("Poster", width="small")
             # Optionnel : Cacher la colonne URL brute si l'image est affichée
             # column_config_main["Poster_Link_url"] = None # Ajuster si la colonne URL est différente

        st.dataframe(df_display_main, use_container_width=True, height=(items_per_page_main + 1) * 35 + 3, column_config=column_config_main)


        # --- Contrôles de Pagination ---
        if total_pages_main > 1:
            col_nav1_main, col_nav2_main, col_nav3_main = st.columns([1, 2, 1])
            with col_nav1_main:
                if st.button("⬅️ Précédent", key="prev_main", disabled=(st.session_state.current_page_main <= 1)):
                    st.session_state.current_page_main -= 1
                    st.rerun()
            with col_nav2_main:
                 st.markdown(f"<p style='text-align: center; margin-top: 8px;'>Page {st.session_state.current_page_main} sur {total_pages_main}</p>", unsafe_allow_html=True)
            with col_nav3_main:
                if st.button("Suivant ➡️", key="next_main", disabled=(st.session_state.current_page_main >= total_pages_main)):
                    st.session_state.current_page_main += 1
                    st.rerun()
        # --- FIN PAGINATION ---

    else:
        st.error("Impossible de charger les données principales des films. Vérifiez la connexion au backend.")

# 2. Tendances Annuelles
elif selected_analysis == "Tendances Annuelles":
    st.header("📈 Tendances Annuelles")

    st.subheader("Nombre de Films Sortis par Année")
    data_by_year = fetch_data("movies-by-year")
    if data_by_year:
        df_year = pd.DataFrame(data_by_year)
        df_year['Released_Year_Numeric'] = pd.to_numeric(df_year['Released_Year'], errors='coerce')
        df_year = df_year.dropna(subset=['Released_Year_Numeric'])
        df_year['Released_Year_Numeric'] = df_year['Released_Year_Numeric'].astype(int)
        df_year = df_year.sort_values("Released_Year_Numeric")

        if not df_year.empty:
            fig_year_count = px.line(df_year, x='Released_Year_Numeric', y='number_of_movies',
                                     title="Nombre de Films Sortis au Fil du Temps",
                                     labels={'Released_Year_Numeric': 'Année', 'number_of_movies': 'Nombre de Films'})
            fig_year_count.update_layout(hovermode="x unified")
            st.plotly_chart(fig_year_count, use_container_width=True)

            valid_years = df_year['Released_Year_Numeric'].tolist()
            if valid_years:
                selected_year_explore = st.selectbox("Voir les films pour une année spécifique:", ["--Choisir une Année--"] + sorted(valid_years, reverse=True), key="select_year_explore_trend")
                if selected_year_explore != "--Choisir une Année--" and not df_all_movies.empty:
                    st.write(f"**Films de {selected_year_explore}:**")
                    filtered_movies_year = df_all_movies[df_all_movies['Released_Year_Numeric'] == selected_year_explore]
                    config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in filtered_movies_year.columns else {}
                    st.dataframe(filtered_movies_year[['Poster_Link', 'Series_Title', 'Genre', 'IMDB_Rating', 'Gross']].copy() if 'Poster_Link' in filtered_movies_year.columns else filtered_movies_year[['Series_Title', 'Genre', 'IMDB_Rating', 'Gross']].copy(),
                                 use_container_width=True, column_config=config)
        else: st.warning("Aucune donnée d'année valide trouvée.")
    else: st.warning("Impossible de récupérer les données de films par année.")

    st.subheader("Note IMDB Moyenne par Année")
    data_yearly_avg = fetch_data("yearly-avg-ratings")
    if data_yearly_avg:
        df_yearly = pd.DataFrame(data_yearly_avg)
        df_yearly['Released_Year_Numeric'] = pd.to_numeric(df_yearly['Released_Year'], errors='coerce')
        df_yearly = df_yearly.dropna(subset=['Released_Year_Numeric', 'avg_IMDB_rating'])
        df_yearly['Released_Year_Numeric'] = df_yearly['Released_Year_Numeric'].astype(int)
        df_yearly = df_yearly.sort_values('Released_Year_Numeric')
        if not df_yearly.empty:
            fig_yearly_avg = px.line(df_yearly, x='Released_Year_Numeric', y='avg_IMDB_rating', title="Note IMDB Moyenne au Fil du Temps", labels={'Released_Year_Numeric': 'Année', 'avg_IMDB_rating': 'Note IMDB Moyenne'})
            fig_yearly_avg.update_layout(hovermode="x unified")
            st.plotly_chart(fig_yearly_avg, use_container_width=True)
        else: st.warning("Aucune donnée valide pour le graphique des notes moyennes annuelles.")
    else: st.warning("Impossible de récupérer les données des notes moyennes annuelles.")

    st.subheader("Top 5 des Années avec le Plus de Films")
    data_top_years = fetch_data("top-years-by-movies")
    if data_top_years: st.dataframe(pd.DataFrame(data_top_years))
    else: st.warning("Impossible de récupérer les données des années les plus prolifiques.")

    st.subheader("Film aux Plus Grosses Recettes par Année")
    data_gross_year = fetch_data("top-gross-by-year")
    if data_gross_year:
        df_gross_year = pd.DataFrame(data_gross_year)
        df_gross_year['Released_Year'] = pd.to_numeric(df_gross_year['Released_Year'], errors='coerce')
        df_gross_year = df_gross_year.dropna(subset=['Released_Year']).sort_values('Released_Year')
        df_gross_year['Released_Year'] = df_gross_year['Released_Year'].astype(int)
        if not df_all_movies.empty: df_gross_year_merged = pd.merge(df_gross_year, df_all_movies[['Series_Title', 'Released_Year_Numeric', 'Poster_Link']], left_on=['Series_Title', 'Released_Year'], right_on=['Series_Title', 'Released_Year_Numeric'], how='left')
        else: df_gross_year_merged = df_gross_year.copy(); df_gross_year_merged['Poster_Link'] = ''
        with st.expander("Voir le Film aux Plus Grosses Recettes pour Chaque Année"):
             config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_gross_year_merged.columns else {}
             st.dataframe(df_gross_year_merged[['Released_Year', 'Poster_Link', 'Series_Title', 'Gross']].copy() if 'Poster_Link' in df_gross_year_merged.columns else df_gross_year_merged[['Released_Year', 'Series_Title', 'Gross']].copy(),
                          use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer le film aux plus grosses recettes par année.")


# 3. Analyse par Genre
elif selected_analysis == "Analyse par Genre":
    st.header("🎭 Analyse par Genre")

    st.subheader("Nombre de Films par Genre")
    data_genre_count = fetch_data("movies-by-genre")
    if data_genre_count:
        df_genre = pd.DataFrame(data_genre_count).sort_values("genre_count", ascending=False)
        df_genre['Genre'] = df_genre['Genre'].fillna('Inconnu')
        if not df_genre.empty:
            fig_genre_count = px.bar(df_genre.head(25).sort_values('genre_count', ascending=True), y='Genre', x='genre_count', orientation='h', title="Nombre de Films par Genre (Top 25)", labels={'genre_count': 'Nombre de Films'}, text_auto=True)
            fig_genre_count.update_layout(yaxis_title="Genre", xaxis_title="Nombre de Films", height=600)
            st.plotly_chart(fig_genre_count, use_container_width=True)

            genres_list = df_genre['Genre'].unique().tolist()
            selected_genre_explore = st.selectbox("Voir les films pour un genre spécifique:", ["--Choisir un Genre--"] + genres_list, key="select_genre_explore_genre")
            if selected_genre_explore != "--Choisir un Genre--" and not df_all_movies.empty:
                st.write(f"**Films du genre '{selected_genre_explore}' (triés par note):**")
                filtered_movies_genre = df_all_movies[df_all_movies['Genre'] == selected_genre_explore].sort_values('IMDB_Rating', ascending=False)
                config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in filtered_movies_genre.columns else {}
                st.dataframe(filtered_movies_genre[['Poster_Link', 'Series_Title', 'IMDB_Rating', 'Released_Year', 'Director', 'Gross']].copy() if 'Poster_Link' in filtered_movies_genre.columns else filtered_movies_genre[['Series_Title', 'IMDB_Rating', 'Released_Year', 'Director', 'Gross']].copy(),
                             use_container_width=True, column_config=config)
        else: st.warning("Aucune donnée de genre trouvée.")
    else: st.warning("Impossible de récupérer les données de films par genre.")

    st.subheader("Top 10 Genres par Nombre Total de Votes")
    data_popular_genres = fetch_data("popular-genres-by-votes")
    if data_popular_genres:
        df_popular_g = pd.DataFrame(data_popular_genres)
        df_popular_g['total_votes'] = pd.to_numeric(df_popular_g['total_votes'], errors='coerce')
        df_popular_g = df_popular_g.dropna(subset=['total_votes']).sort_values('total_votes', ascending=False)
        if not df_popular_g.empty:
             fig_popular_g = px.bar(df_popular_g.head(10), x='Genre', y='total_votes', title="Top 10 des Genres par Total de Votes", labels={'total_votes': 'Nombre Total de Votes'})
             st.plotly_chart(fig_popular_g, use_container_width=True)
    else: st.warning("Impossible de récupérer les données des genres populaires par votes.")

    st.subheader("Durée Moyenne par Genre")
    data_avg_runtime = fetch_data("avg-runtime-by-genre")
    if data_avg_runtime:
        df_avg_rt = pd.DataFrame(data_avg_runtime)
        df_avg_rt['avg_runtime_minutes'] = pd.to_numeric(df_avg_rt['avg_runtime_minutes'], errors='coerce')
        df_avg_rt = df_avg_rt.dropna(subset=['avg_runtime_minutes']).sort_values("avg_runtime_minutes", ascending=False)
        if not df_avg_rt.empty:
            fig_avg_rt = px.bar(df_avg_rt, x='Genre', y='avg_runtime_minutes', title="Durée Moyenne des Films par Genre", labels={'avg_runtime_minutes': 'Durée Moyenne (Minutes)'}, text_auto=True)
            fig_avg_rt.update_xaxes(categoryorder='total descending')
            st.plotly_chart(fig_avg_rt, use_container_width=True)
    else: st.warning("Impossible de récupérer les données de durée moyenne par genre.")

    st.subheader("Film aux Plus Grosses Recettes par Genre")
    data_gross_genre = fetch_data("top-gross-by-genre")
    if data_gross_genre:
        df_gross_g = pd.DataFrame(data_gross_genre)
        if not df_all_movies.empty: df_gross_g_merged = pd.merge(df_gross_g, df_all_movies[['Series_Title', 'Genre', 'Poster_Link']].drop_duplicates(['Series_Title', 'Genre']), on=['Series_Title', 'Genre'], how='left')
        else: df_gross_g_merged = df_gross_g.copy(); df_gross_g_merged['Poster_Link'] = ''
        df_gross_g_merged['max_gross_Str'] = df_gross_g_merged['max_gross'].fillna('').astype(str)
        df_gross_g_numeric = robust_clean_gross(df_gross_g_merged, 'max_gross')
        df_gross_g_numeric = df_gross_g_numeric.dropna(subset=['max_gross_Numeric']).sort_values('max_gross_Numeric', ascending=False)
        with st.expander("Voir le Film aux Plus Grosses Recettes pour Chaque Genre"):
             config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small"), "max_gross_Str": "Recette Max"} if 'Poster_Link' in df_gross_g_numeric.columns else {"max_gross_Str": "Recette Max"}
             st.dataframe(df_gross_g_numeric[['Genre', 'Poster_Link', 'Series_Title', 'max_gross_Str']].copy() if 'Poster_Link' in df_gross_g_numeric.columns else df_gross_g_numeric[['Genre', 'Series_Title', 'max_gross_Str']].copy(),
                          use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer le film aux plus grosses recettes par genre.")

    st.subheader("Films les Mieux Notés par Genre (Table Complète)")
    data_top_rated_genre = fetch_data("top-rated-by-genre")
    if data_top_rated_genre:
        df_top_rg = pd.DataFrame(data_top_rated_genre)
        with st.expander("Afficher tous les films triés par genre puis par note (peut être long)"):
            if not df_all_movies.empty: df_top_rg_merged = pd.merge(df_top_rg, df_all_movies[['Series_Title', 'Genre', 'Poster_Link']].drop_duplicates(['Series_Title', 'Genre']), on=['Series_Title', 'Genre'], how='left')
            else: df_top_rg_merged = df_top_rg.copy(); df_top_rg_merged['Poster_Link'] = ''
            config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_top_rg_merged.columns else {}
            st.dataframe(df_top_rg_merged[['Genre', 'Poster_Link', 'Series_Title', 'IMDB_Rating']].copy() if 'Poster_Link' in df_top_rg_merged.columns else df_top_rg_merged[['Genre', 'Series_Title', 'IMDB_Rating']].copy(),
                         use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer les films les mieux notés par genre.")


# 4. Classement par Note IMDB
elif selected_analysis == "Classement par Note IMDB":
    st.header("⭐ Classement par Note IMDB")

    st.subheader("Distribution des Notes IMDB")
    if not df_all_movies.empty and 'IMDB_Rating' in df_all_movies.columns:
        df_rating_valid_hist = df_all_movies.dropna(subset=['IMDB_Rating'])
        if not df_rating_valid_hist.empty:
            fig_hist_rate = px.histogram(df_rating_valid_hist, x='IMDB_Rating', nbins=30, title="Distribution des Notes IMDB", labels={'IMDB_Rating': 'Note IMDB'})
            st.plotly_chart(fig_hist_rate, use_container_width=True)
        else: st.warning("Aucune note IMDB valide trouvée pour l'histogramme.")
    else: st.warning("Données IMDB non disponibles pour la distribution.")

    st.subheader("Top 10 des Films les Mieux Notés")
    data_top_10 = fetch_data("top-movies")
    if data_top_10:
        df_top_10 = pd.DataFrame(data_top_10)
        if not df_all_movies.empty: df_top_10_merged = pd.merge(df_top_10, df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
        else: df_top_10_merged = df_top_10.copy(); df_top_10_merged['Poster_Link'] = ''
        df_top_10_merged['IMDB_Rating'] = pd.to_numeric(df_top_10_merged['IMDB_Rating'], errors='coerce')
        df_top_10_merged = robust_clean_gross(df_top_10_merged, 'Gross')
        df_top_10_merged = df_top_10_merged.dropna(subset=['IMDB_Rating']).sort_values('IMDB_Rating', ascending=False)

        if not df_top_10_merged.empty:
            fig_top_10 = px.bar(df_top_10_merged.sort_values('IMDB_Rating', ascending=True), x='IMDB_Rating', y='Series_Title', orientation='h', title="Top 10 des Films par Note IMDB", labels={'IMDB_Rating': 'Note IMDB', 'Series_Title': 'Titre du Film'}, text='IMDB_Rating', hover_data=['Gross'])
            fig_top_10.update_traces(textposition='outside')
            fig_top_10.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top_10, use_container_width=True)
            config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_top_10_merged.columns else {}
            st.dataframe(df_top_10_merged[['Poster_Link', 'Series_Title', 'IMDB_Rating', 'Gross']].copy() if 'Poster_Link' in df_top_10_merged.columns else df_top_10_merged[['Series_Title', 'IMDB_Rating', 'Gross']].copy(),
                         use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer le top 10 des films.")

    st.subheader("Films avec Notes Moyennes (7.0 à 8.0)")
    data_mid_range = fetch_data("mid-range-ratings")
    if data_mid_range:
         df_mid = pd.DataFrame(data_mid_range)
         if not df_all_movies.empty: df_mid_merged = pd.merge(df_mid, df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
         else: df_mid_merged = df_mid.copy(); df_mid_merged['Poster_Link'] = ''
         with st.expander(f"Voir les {len(df_mid_merged)} Films avec une Note IMDB entre 7.0 et 8.0"):
              config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_mid_merged.columns else {}
              st.dataframe(df_mid_merged[['Poster_Link', 'Series_Title', 'IMDB_Rating']].copy() if 'Poster_Link' in df_mid_merged.columns else df_mid_merged[['Series_Title', 'IMDB_Rating']].copy(),
                           use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer les données des films de note moyenne.")

    st.subheader("Top 5 des Films à Faibles Recettes avec Bonne Note (> 7.0)")
    data_low_gross = fetch_data("low-gross-high-rating")
    if data_low_gross:
         df_low_gross = pd.DataFrame(data_low_gross)
         if not df_all_movies.empty: df_low_gross_merged = pd.merge(df_low_gross, df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
         else: df_low_gross_merged = df_low_gross.copy(); df_low_gross_merged['Poster_Link'] = ''
         df_low_gross_merged['IMDB_Rating'] = pd.to_numeric(df_low_gross_merged['IMDB_Rating'], errors='coerce')
         df_low_gross_merged = robust_clean_gross(df_low_gross_merged, 'Gross')
         config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_low_gross_merged.columns else {}
         st.dataframe(df_low_gross_merged[['Poster_Link', 'Series_Title', 'Gross', 'IMDB_Rating']].copy() if 'Poster_Link' in df_low_gross_merged.columns else df_low_gross_merged[['Series_Title', 'Gross', 'IMDB_Rating']].copy(),
                      use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer les données des films à faibles recettes / haute note.")


# 5. Classement par Recettes
elif selected_analysis == "Classement par Recettes":
    st.header("💰 Classement par Recettes Brutes")
    st.caption("Note : L'unité des recettes (Millions USD, etc.) est supposée.")

    st.subheader("Top 5 des Films aux Plus Grosses Recettes")
    data_top_gross = fetch_data("top-grossing-movies")
    if data_top_gross:
        df_top_gross = pd.DataFrame(data_top_gross)
        if not df_all_movies.empty: df_top_gross_merged = pd.merge(df_top_gross, df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
        else: df_top_gross_merged = df_top_gross.copy(); df_top_gross_merged['Poster_Link'] = ''
        df_top_gross_merged = robust_clean_gross(df_top_gross_merged, 'Gross')
        df_top_gross_merged = df_top_gross_merged.dropna(subset=['Gross_Numeric']).sort_values('Gross_Numeric', ascending=False)

        if not df_top_gross_merged.empty:
            fig_top_gross = px.bar(df_top_gross_merged.head(5).sort_values('Gross_Numeric', ascending=True), x='Gross_Numeric', y='Series_Title', orientation='h', title="Top 5 des Films par Recettes Brutes", labels={'Gross_Numeric': 'Recettes Brutes', 'Series_Title': 'Titre du Film'}, text='Gross')
            fig_top_gross.update_layout(xaxis_title="Recettes Brutes", yaxis_title="Titre du Film", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top_gross, use_container_width=True)
            config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_top_gross_merged.columns else {}
            st.dataframe(df_top_gross_merged.head(5)[['Poster_Link', 'Series_Title', 'Gross']].copy() if 'Poster_Link' in df_top_gross_merged.columns else df_top_gross_merged.head(5)[['Series_Title', 'Gross']].copy(),
                         use_container_width=True, column_config=config)
        else: st.info("Aucune donnée de recettes valide trouvée.")
    else: st.warning("Impossible de récupérer les films aux plus grosses recettes.")

    st.subheader("Films Très Bien Notés (>8.5) avec Hautes Recettes (>50M Estimé)")
    data_hrhg = fetch_data("top-rated-high-gross")
    if data_hrhg:
        df_hrhg = pd.DataFrame(data_hrhg)
        if not df_all_movies.empty: df_hrhg_merged = pd.merge(df_hrhg, df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
        else: df_hrhg_merged = df_hrhg.copy(); df_hrhg_merged['Poster_Link'] = ''
        df_hrhg_merged = robust_clean_gross(df_hrhg_merged, 'Gross')
        df_hrhg_merged['IMDB_Rating'] = pd.to_numeric(df_hrhg_merged['IMDB_Rating'], errors='coerce')
        df_hrhg_merged = df_hrhg_merged.dropna(subset=['Gross_Numeric', 'IMDB_Rating'])
        df_hrhg_merged = df_hrhg_merged.sort_values(['IMDB_Rating', 'Gross_Numeric'], ascending=[False, False])
        with st.expander(f"Voir les {len(df_hrhg_merged)} Films avec Note > 8.5 et Recettes > 50M (Estimé)"):
             config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_hrhg_merged.columns else {}
             st.dataframe(df_hrhg_merged[['Poster_Link', 'Series_Title', 'IMDB_Rating', 'Gross']].copy() if 'Poster_Link' in df_hrhg_merged.columns else df_hrhg_merged[['Series_Title', 'IMDB_Rating', 'Gross']].copy(),
                          use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer les films bien notés et à hautes recettes.")

    # --- CORRECTION APPLIQUÉE ICI ---
    st.subheader("Explorer les films dépassant un seuil de recettes")
    if not df_all_movies.empty and 'Gross_Numeric' in df_all_movies.columns:
        df_gross_valid_exp = df_all_movies.dropna(subset=['Gross_Numeric'])
        if not df_gross_valid_exp.empty:
            max_gross_val = df_gross_valid_exp['Gross_Numeric'].max()
            min_gross_val = df_gross_valid_exp['Gross_Numeric'].min()

            slider_min = int(min_gross_val / 1_000_000) if pd.notna(min_gross_val) else 0
            if pd.notna(max_gross_val) and max_gross_val > 0:
                 slider_max = max(slider_min, int(max_gross_val / 1_000_000))
                 if slider_max == 0 and max_gross_val > 0 and slider_min == 0: slider_max = 1
            else: slider_max = slider_min

            filtered_gross_movies = pd.DataFrame() # Initialiser

            if slider_min < slider_max:
                 slider_default = min(100, slider_max) if slider_max > 0 else slider_min
                 slider_default = max(slider_min, slider_default)
                 slider_step = max(1, (slider_max - slider_min) // 20)

                 gross_threshold = st.slider("Afficher les films avec des recettes supérieures à (M$):", min_value=slider_min, max_value=slider_max, value=slider_default, step=slider_step, key="slider_gross_explore_recettes")
                 threshold_numeric = gross_threshold * 1_000_000
                 filtered_gross_movies = df_gross_valid_exp[df_gross_valid_exp['Gross_Numeric'] >= threshold_numeric].sort_values('Gross_Numeric', ascending=False)
                 st.write(f"**{len(filtered_gross_movies)} films trouvés avec des recettes >= {gross_threshold}M:**")
            else:
                 st.info(f"Impossible de créer un curseur (Min: {slider_min}M, Max: {slider_max}M). Affichage de tous les films avec recettes valides.")
                 filtered_gross_movies = df_gross_valid_exp.sort_values('Gross_Numeric', ascending=False)
                 st.write(f"**{len(filtered_gross_movies)} films trouvés avec des recettes valides:**")

            if not filtered_gross_movies.empty:
                 config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in filtered_gross_movies.columns else {}
                 st.dataframe(filtered_gross_movies[['Poster_Link', 'Series_Title', 'Gross', 'IMDB_Rating', 'Released_Year']].copy() if 'Poster_Link' in filtered_gross_movies.columns else filtered_gross_movies[['Series_Title', 'Gross', 'IMDB_Rating', 'Released_Year']].copy(),
                              use_container_width=True, column_config=config)

        else: st.info("Aucune donnée de recette valide pour l'exploration.")
    else: st.warning("Données de recettes non disponibles pour l'exploration.")
    # --- FIN DE LA CORRECTION ---

# 6. Performance des Réalisateurs
elif selected_analysis == "Performance des Réalisateurs":
    st.header("🎬 Performance des Réalisateurs")

    st.subheader("Top 10 par Nombre de Films")
    data_top_directors = fetch_data("movies-by-director")
    if data_top_directors:
        df_directors = pd.DataFrame(data_top_directors)
        df_directors['count'] = pd.to_numeric(df_directors['count'], errors='coerce')
        df_directors = df_directors.dropna(subset=['count']).sort_values('count', ascending=False)
        if not df_directors.empty:
            fig_dir_count = px.bar(df_directors.head(10).sort_values('count'), x='count', y='Director', orientation='h', title="Top 10 des Réalisateurs par Nombre de Films", labels={'count': 'Nombre de Films'}, text='count')
            fig_dir_count.update_layout(yaxis_title="Réalisateur", xaxis_title="Nombre de Films", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_dir_count, use_container_width=True)

            directors_list_all = sorted(df_all_movies['Director'].unique().tolist()) if not df_all_movies.empty else []
            selected_director_explore = st.selectbox("Voir les films pour un réalisateur spécifique:", ["--Choisir un Réalisateur--"] + directors_list_all, key="select_director_explore_perf")
            if selected_director_explore != "--Choisir un Réalisateur--" and not df_all_movies.empty:
                st.write(f"**Films de {selected_director_explore} (triés par année):**")
                filtered_movies_director = df_all_movies[df_all_movies['Director'] == selected_director_explore].sort_values('Released_Year_Numeric', ascending=False)
                config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in filtered_movies_director.columns else {}
                st.dataframe(filtered_movies_director[['Poster_Link', 'Series_Title', 'Released_Year', 'Genre', 'IMDB_Rating', 'Gross', 'Runtime']].copy() if 'Poster_Link' in filtered_movies_director.columns else filtered_movies_director[['Series_Title', 'Released_Year', 'Genre', 'IMDB_Rating', 'Gross', 'Runtime']].copy(),
                             use_container_width=True, column_config=config)
        else: st.info("Aucune donnée sur les réalisateurs trouvée.")
    else: st.warning("Impossible de récupérer les données des réalisateurs.")

    st.subheader("Réalisateurs avec >= 3 Films Notés > 8.0")
    data_high_rated = fetch_data("top-directors-by-rating")
    if data_high_rated:
        df_high_rated = pd.DataFrame(data_high_rated)
        df_high_rated['avg_IMDB_rating'] = pd.to_numeric(df_high_rated['avg_IMDB_rating'], errors='coerce').round(1)
        df_high_rated['number_of_movies'] = pd.to_numeric(df_high_rated['number_of_movies'], errors='coerce')
        df_high_rated = df_high_rated.dropna()
        st.dataframe(df_high_rated.sort_values(['avg_IMDB_rating', 'number_of_movies'], ascending=[False, False]), use_container_width=True)
    else: st.warning("Impossible de récupérer les données.")

    st.subheader("Réalisateurs Ayant Réalisé des Films dans Plusieurs Genres")
    data_multi_genre = fetch_data("directors-multiple-genres")
    if data_multi_genre:
        df_multi_genre = pd.DataFrame(data_multi_genre)
        df_multi_genre['genre_count'] = pd.to_numeric(df_multi_genre['genre_count'], errors='coerce')
        df_multi_genre = df_multi_genre.dropna().sort_values("genre_count", ascending=False)
        with st.expander(f"Voir les {len(df_multi_genre)} réalisateurs avec plus d'un genre"):
            st.dataframe(df_multi_genre, use_container_width=True)
    else: st.warning("Impossible de récupérer les données.")

    st.subheader("Film le Mieux Noté par Réalisateur (Top 50)")
    data_top_rated_dir = fetch_data("top-rated-by-director")
    if data_top_rated_dir:
         df_top_rated_dir = pd.DataFrame(data_top_rated_dir)
         if not df_all_movies.empty: df_top_rated_dir_merged = pd.merge(df_top_rated_dir, df_all_movies[['Series_Title', 'Director', 'Poster_Link']].drop_duplicates(['Series_Title', 'Director']), on=['Series_Title', 'Director'], how='left')
         else: df_top_rated_dir_merged = df_top_rated_dir.copy(); df_top_rated_dir_merged['Poster_Link'] = ''
         df_top_rated_dir_merged['max_rating'] = pd.to_numeric(df_top_rated_dir_merged['max_rating'], errors='coerce')
         df_top_rated_dir_merged = df_top_rated_dir_merged.dropna().sort_values('max_rating', ascending=False)
         with st.expander("Voir le Film le Mieux Noté par Réalisateur (Top 50)"):
              config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_top_rated_dir_merged.columns else {}
              st.dataframe(df_top_rated_dir_merged.head(50)[['Director', 'Poster_Link', 'Series_Title', 'max_rating']].copy() if 'Poster_Link' in df_top_rated_dir_merged.columns else df_top_rated_dir_merged.head(50)[['Director', 'Series_Title', 'max_rating']].copy(),
                           use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer les données.")


# 7. Analyse de la Durée
elif selected_analysis == "Analyse de la Durée":
    st.header("⏱️ Analyse de la Durée")

    st.subheader("Distribution des Durées des Films")
    if not df_all_movies.empty and 'Runtime_Minutes' in df_all_movies.columns:
        df_runtime_valid_hist = df_all_movies.dropna(subset=['Runtime_Minutes'])
        if not df_runtime_valid_hist.empty:
            fig_hist_runtime = px.histogram(df_runtime_valid_hist, x='Runtime_Minutes', nbins=50, title="Distribution des Durées des Films", labels={'Runtime_Minutes': 'Durée (Minutes)'})
            st.plotly_chart(fig_hist_runtime, use_container_width=True)

            min_rt, max_rt = int(df_runtime_valid_hist['Runtime_Minutes'].min()), int(df_runtime_valid_hist['Runtime_Minutes'].max())
            if min_rt <= max_rt:
                selected_runtime_range = st.slider("Voir les films dans une plage de durée (minutes):", min_value=min_rt, max_value=max_rt, value=(min_rt, max_rt), key="slider_runtime_explore_duree")
                start_rt, end_rt = selected_runtime_range
                filtered_runtime = df_runtime_valid_hist[ (df_runtime_valid_hist['Runtime_Minutes'] >= start_rt) & (df_runtime_valid_hist['Runtime_Minutes'] <= end_rt)].sort_values('Runtime_Minutes')
                st.write(f"**{len(filtered_runtime)} films trouvés entre {start_rt} et {end_rt} minutes:**")
                config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in filtered_runtime.columns else {}
                st.dataframe(filtered_runtime[['Poster_Link', 'Series_Title', 'Runtime', 'IMDB_Rating', 'Genre']].copy() if 'Poster_Link' in filtered_runtime.columns else filtered_runtime[['Series_Title', 'Runtime', 'IMDB_Rating', 'Genre']].copy(),
                             use_container_width=True, column_config=config)
            else: st.info("Plage de durée invalide.")
        else: st.warning("Aucune donnée de durée valide.")
    else: st.warning("Données de durée non disponibles.")

    st.subheader("Films les Plus Courts et les Plus Longs")
    data_extreme = fetch_data("extreme-runtime-movies")
    if data_extreme and isinstance(data_extreme, dict):
        shortest_movies = data_extreme.get("shortest", [])
        longest_movies = data_extreme.get("longest", [])
        if not df_all_movies.empty:
             df_shortest_merged = pd.merge(pd.DataFrame(shortest_movies), df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
             df_longest_merged = pd.merge(pd.DataFrame(longest_movies), df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
        else:
             df_shortest_merged = pd.DataFrame(shortest_movies); df_shortest_merged['Poster_Link'] = ''
             df_longest_merged = pd.DataFrame(longest_movies); df_longest_merged['Poster_Link'] = ''
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Top 5 Plus Courts**")
            config_short = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_shortest_merged.columns else {}
            st.dataframe(df_shortest_merged[['Poster_Link', 'Series_Title', 'Runtime']].copy() if 'Poster_Link' in df_shortest_merged.columns else df_shortest_merged[['Series_Title', 'Runtime']].copy(),
                         use_container_width=True, column_config=config_short)
        with col2:
            st.write("**Top 5 Plus Longs**")
            config_long = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_longest_merged.columns else {}
            st.dataframe(df_longest_merged[['Poster_Link', 'Series_Title', 'Runtime']].copy() if 'Poster_Link' in df_longest_merged.columns else df_longest_merged[['Series_Title', 'Runtime']].copy(),
                         use_container_width=True, column_config=config_long)
    else: st.warning("Impossible de récupérer les données.")

    st.subheader("Top 10 des Durées les Plus Fréquentes")
    data_freq_runtime = fetch_data("movies-by-runtime")
    if data_freq_runtime:
        df_freq = pd.DataFrame(data_freq_runtime).sort_values('count', ascending=False)
        st.dataframe(df_freq.head(10), use_container_width=True)
    else: st.warning("Impossible de récupérer les données.")

    st.subheader("Films Longs (>120min) et Bien Notés (>8.0)")
    data_long_high = fetch_data("long-high-rated-movies")
    if data_long_high:
         df_long_high = pd.DataFrame(data_long_high)
         if not df_all_movies.empty: df_long_high_merged = pd.merge(df_long_high, df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
         else: df_long_high_merged = df_long_high.copy(); df_long_high_merged['Poster_Link'] = ''
         df_long_high_merged = robust_clean_runtime(df_long_high_merged, 'Runtime')
         df_long_high_merged['IMDB_Rating'] = pd.to_numeric(df_long_high_merged['IMDB_Rating'], errors='coerce')
         with st.expander(f"Voir les {len(df_long_high_merged)} Films Longs et Très Bien Notés"):
              config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_long_high_merged.columns else {}
              st.dataframe(df_long_high_merged[['Poster_Link', 'Series_Title', 'Runtime', 'IMDB_Rating']].copy() if 'Poster_Link' in df_long_high_merged.columns else df_long_high_merged[['Series_Title', 'Runtime', 'IMDB_Rating']].copy(),
                           use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer les données.")


# 8. Distribution des Certificats
elif selected_analysis == "Distribution des Certificats":
    st.header("📜 Distribution des Certificats")

    st.subheader("Nombre de Films par Certificat")
    data_cert_count = fetch_data("movies-by-certificate")
    if data_cert_count:
        df_cert = pd.DataFrame(data_cert_count)
        df_cert['Certificate'] = df_cert['Certificate'].fillna('Non Classé').replace('', 'Non Classé')
        df_cert['count'] = pd.to_numeric(df_cert['count'], errors='coerce')
        df_cert = df_cert.dropna().sort_values("count", ascending=False)
        if not df_cert.empty:
            fig_cert = px.pie(df_cert, values='count', names='Certificate', title="Répartition des Films par Certificat", hole=.3)
            fig_cert.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_cert, use_container_width=True)

            certs_list = df_cert['Certificate'].unique().tolist()
            selected_cert_explore = st.selectbox("Voir les films pour un certificat spécifique:", ["--Choisir un Certificat--"] + certs_list, key="select_cert_explore_cert")
            if selected_cert_explore != "--Choisir un Certificat--" and not df_all_movies.empty:
                 st.write(f"**Films avec certificat '{selected_cert_explore}' (triés par note):**")
                 filtered_movies_cert = df_all_movies[df_all_movies['Certificate'] == selected_cert_explore].sort_values('IMDB_Rating', ascending=False)
                 config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in filtered_movies_cert.columns else {}
                 st.dataframe(filtered_movies_cert[['Poster_Link', 'Series_Title', 'IMDB_Rating', 'Genre', 'Released_Year']].copy() if 'Poster_Link' in filtered_movies_cert.columns else filtered_movies_cert[['Series_Title', 'IMDB_Rating', 'Genre', 'Released_Year']].copy(),
                              use_container_width=True, column_config=config)
        else: st.info("Aucune donnée de certificat trouvée.")
    else: st.warning("Impossible de récupérer le nombre de films par certificat.")

    st.subheader("Film le Mieux Noté par Certificat")
    data_top_cert = fetch_data("top-rated-by-certificate")
    if data_top_cert:
        df_top_cert = pd.DataFrame(data_top_cert)
        if not df_all_movies.empty: df_top_cert_merged = pd.merge(df_top_cert, df_all_movies[['Series_Title', 'Certificate', 'Poster_Link']].drop_duplicates(['Series_Title', 'Certificate']), on=['Series_Title', 'Certificate'], how='left')
        else: df_top_cert_merged = df_top_cert.copy(); df_top_cert_merged['Poster_Link'] = ''
        df_top_cert_merged['Certificate'] = df_top_cert_merged['Certificate'].fillna('Non Classé').replace('', 'Non Classé')
        df_top_cert_merged['max_rating'] = pd.to_numeric(df_top_cert_merged['max_rating'], errors='coerce')
        df_top_cert_merged = df_top_cert_merged.dropna().sort_values('max_rating', ascending=False)
        config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_top_cert_merged.columns else {}
        st.dataframe(df_top_cert_merged[['Certificate', 'Poster_Link', 'Series_Title', 'max_rating']].copy() if 'Poster_Link' in df_top_cert_merged.columns else df_top_cert_merged[['Certificate', 'Series_Title', 'max_rating']].copy(),
                     use_container_width=True, column_config=config)
    else: st.warning("Impossible de récupérer le film le mieux noté par certificat.")


# 9. Requêtes Complexes & Corrélations
elif selected_analysis == "Requêtes Complexes & Corrélations":
    st.header("🔍 Requêtes Complexes & Corrélations")
    st.markdown("Exploration des relations entre différentes métriques.")
    col_corr1, col_corr2, col_corr3 = st.columns(3)

    with col_corr1:
        st.subheader("Votes vs Recettes")
        data_corr_vg = fetch_data("votes-gross-correlation")
        if data_corr_vg:
            df_corr_vg = pd.DataFrame(data_corr_vg)
            df_corr_vg = robust_clean_gross(df_corr_vg, 'Gross')
            df_corr_vg['No_of_Votes'] = pd.to_numeric(df_corr_vg['No_of_Votes'], errors='coerce')
            df_corr_vg = df_corr_vg.dropna(subset=['Gross_Numeric', 'No_of_Votes'])
            if not df_corr_vg.empty and len(df_corr_vg) > 1:
                fig_corr_vg = px.scatter(df_corr_vg, x='No_of_Votes', y='Gross_Numeric', title="Votes vs Recettes Brutes", labels={'No_of_Votes': 'Votes', 'Gross_Numeric': 'Recettes (Estimées)'}, trendline='ols', trendline_color_override="red", log_x=True, log_y=True)
                fig_corr_vg.update_layout(xaxis_title="Votes (Log)", yaxis_title="Recettes (Log)")
                st.plotly_chart(fig_corr_vg, use_container_width=True)
                try: st.metric("Corrélation Pearson", f"{df_corr_vg['No_of_Votes'].corr(df_corr_vg['Gross_Numeric']):.2f}")
                except Exception: st.caption("Corrélation non calculable.")
            elif not df_corr_vg.empty: st.info("Pas assez de données.")
            else: st.info("Aucune donnée valide.")
        else: st.warning("Impossible de récupérer les données.")

    with col_corr2:
        st.subheader("Durée vs Note")
        data_corr_rr = fetch_data("runtime-vs-rating")
        if data_corr_rr:
            df_corr_rr = pd.DataFrame(data_corr_rr)
            df_corr_rr = robust_clean_runtime(df_corr_rr, 'Runtime')
            df_corr_rr['IMDB_Rating'] = pd.to_numeric(df_corr_rr['IMDB_Rating'], errors='coerce')
            df_corr_rr = df_corr_rr.dropna(subset=['Runtime_Minutes', 'IMDB_Rating'])
            if not df_corr_rr.empty and len(df_corr_rr) > 1:
                fig_corr_rr = px.scatter(df_corr_rr, x='Runtime_Minutes', y='IMDB_Rating', title="Durée vs Note IMDB", labels={'Runtime_Minutes': 'Durée (Min)', 'IMDB_Rating': 'Note'}, trendline='ols', trendline_color_override="red")
                st.plotly_chart(fig_corr_rr, use_container_width=True)
                try: st.metric("Corrélation Pearson", f"{df_corr_rr['Runtime_Minutes'].corr(df_corr_rr['IMDB_Rating']):.2f}")
                except Exception: st.caption("Corrélation non calculable.")
            elif not df_corr_rr.empty: st.info("Pas assez de données.")
            else: st.info("Aucune donnée valide.")
        else: st.warning("Impossible de récupérer les données.")

    with col_corr3:
        st.subheader("Durée vs Recettes")
        data_corr_rg = fetch_data("runtime-vs-gross")
        if data_corr_rg:
            df_corr_rg = pd.DataFrame(data_corr_rg)
            df_corr_rg = robust_clean_runtime(df_corr_rg, 'Runtime')
            df_corr_rg = robust_clean_gross(df_corr_rg, 'Gross')
            df_corr_rg = df_corr_rg.dropna(subset=['Runtime_Minutes', 'Gross_Numeric'])
            if not df_corr_rg.empty and len(df_corr_rg) > 1:
                fig_corr_rg = px.scatter(df_corr_rg, x='Runtime_Minutes', y='Gross_Numeric', title="Durée vs Recettes Brutes", labels={'Runtime_Minutes': 'Durée (Min)', 'Gross_Numeric': 'Recettes (Estimées)'}, log_y=True, trendline='ols', trendline_color_override="red")
                fig_corr_rg.update_layout(yaxis_title="Recettes (Log)")
                st.plotly_chart(fig_corr_rg, use_container_width=True)
                try: st.metric("Corrélation Pearson", f"{df_corr_rg['Runtime_Minutes'].corr(df_corr_rg['Gross_Numeric']):.2f}")
                except Exception: st.caption("Corrélation non calculable.")
            elif not df_corr_rg.empty: st.info("Pas assez de données.")
            else: st.info("Aucune donnée valide.")
        else: st.warning("Impossible de récupérer les données.")

    st.divider()
    st.subheader("Autres Résultats Complexes")
    col_adv1, col_adv2 = st.columns(2)

    with col_adv1:
        st.write("**Très Bien Notés & Populaires (>8.0, >500k Votes)**")
        data_hrp = fetch_data("highly-rated-popular-movies")
        if data_hrp:
            df_hrp = pd.DataFrame(data_hrp)
            if not df_all_movies.empty: df_hrp_merged = pd.merge(df_hrp, df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
            else: df_hrp_merged = df_hrp.copy(); df_hrp_merged['Poster_Link'] = ''
            config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_hrp_merged.columns else {}
            st.dataframe(df_hrp_merged[['Poster_Link', 'Series_Title', 'IMDB_Rating', 'No_of_Votes']].copy() if 'Poster_Link' in df_hrp_merged.columns else df_hrp_merged[['Series_Title', 'IMDB_Rating', 'No_of_Votes']].copy(),
                         height=250, use_container_width=True, column_config=config)
        else: st.warning("Données indisponibles.")

        st.write("**Film aux Plus Grosses Recettes par Genre**")
        data_tgpg = fetch_data("top-gross-by-genre")
        if data_tgpg:
             df_gross_g = pd.DataFrame(data_tgpg)
             if not df_all_movies.empty: df_gross_g_merged = pd.merge(df_gross_g, df_all_movies[['Series_Title', 'Genre', 'Poster_Link']].drop_duplicates(['Series_Title', 'Genre']), on=['Series_Title', 'Genre'], how='left')
             else: df_gross_g_merged = df_gross_g.copy(); df_gross_g_merged['Poster_Link'] = ''
             df_gross_g_merged['max_gross_Str'] = df_gross_g_merged['max_gross'].fillna('').astype(str)
             df_gross_g_numeric = robust_clean_gross(df_gross_g_merged, 'max_gross')
             df_gross_g_numeric = df_gross_g_numeric.dropna(subset=['max_gross_Numeric']).sort_values('max_gross_Numeric', ascending=False)
             config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small"), "max_gross_Str": "Recette Max"} if 'Poster_Link' in df_gross_g_numeric.columns else {"max_gross_Str": "Recette Max"}
             st.dataframe(df_gross_g_numeric[['Genre', 'Poster_Link', 'Series_Title', 'max_gross_Str']].copy() if 'Poster_Link' in df_gross_g_numeric.columns else df_gross_g_numeric[['Genre', 'Series_Title', 'max_gross_Str']].copy(),
                          height=250, use_container_width=True, column_config=config)
        else: st.warning("Données indisponibles.")

    with col_adv2:
        st.write("**Films Longs et Bien Notés (>120min, >8.0)**")
        data_long_high = fetch_data("long-high-rated-movies")
        if data_long_high:
            df_long_high = pd.DataFrame(data_long_high)
            if not df_all_movies.empty: df_long_high_merged = pd.merge(df_long_high, df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
            else: df_long_high_merged = df_long_high.copy(); df_long_high_merged['Poster_Link'] = ''
            df_long_high_merged = robust_clean_runtime(df_long_high_merged, 'Runtime')
            df_long_high_merged['IMDB_Rating'] = pd.to_numeric(df_long_high_merged['IMDB_Rating'], errors='coerce')
            config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_long_high_merged.columns else {}
            st.dataframe(df_long_high_merged[['Poster_Link', 'Series_Title', 'Runtime', 'IMDB_Rating']].copy() if 'Poster_Link' in df_long_high_merged.columns else df_long_high_merged[['Series_Title', 'Runtime', 'IMDB_Rating']].copy(),
                         height=250, use_container_width=True, column_config=config)
        else: st.warning("Données indisponibles.")

        st.write("**Films avec Recettes ou Durée Manquantes**")
        data_missing = fetch_data("missing-gross-and-runtime")
        if data_missing:
             df_missing = pd.DataFrame(data_missing)
             with st.expander(f"Afficher {len(df_missing)} films avec données manquantes"):
                  if not df_all_movies.empty: df_missing_merged = pd.merge(df_missing, df_all_movies[['Series_Title', 'Poster_Link']].drop_duplicates('Series_Title'), on='Series_Title', how='left')
                  else: df_missing_merged = df_missing.copy(); df_missing_merged['Poster_Link'] = ''
                  config = {"Poster_Link": st.column_config.ImageColumn("Poster", width="small")} if 'Poster_Link' in df_missing_merged.columns else {}
                  st.dataframe(df_missing_merged[['Poster_Link','Series_Title']].copy() if 'Poster_Link' in df_missing_merged.columns else df_missing_merged[['Series_Title']].copy(),
                               use_container_width=True, column_config=config)
        else: st.warning("Données indisponibles ou aucune donnée manquante.")

# Fin du script