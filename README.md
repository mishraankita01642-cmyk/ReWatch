# ReWatch 🎬

ReWatch is a movie and TV drama recommendation website that helps
users discover stories similar to the titles they already enjoy.

# 🌐 Live Website

Explore ReWatch: [Visit the Live Website]

(https://rewatch.streamlit.app/)
## Features

- Search movies and TV shows.
- Display posters, ratings, release dates and descriptions.
- Retrieve similar titles from TMDB.
- Rank recommendations using storyline and genre similarity.
- Use Gemini embeddings for semantic text similarity.
- Fall back to TF-IDF when Gemini is unavailable.
- Responsive dark-themed interface built with Streamlit.

## Technologies

- Python
- Streamlit
- TMDB API
- Google Gemini Embeddings
- Scikit-learn
- TF-IDF and cosine similarity

## Project Structure

    ReWatch/
    ├── .streamlit/
    │   └── secrets.toml
    ├── app.py
    ├── tmdb_api.py
    ├── recommender.py
    ├── requirements.txt
    ├── .env
    ├── .gitignore
    └── README.md

## Run Locally

1. Clone or download this repository.
2. Create a virtual environment.
3. Install the packages:

       python -m pip install -r requirements.txt

4. Add your TMDB API key to `.env`:

       TMDB_API_KEY=your_tmdb_api_key

5. Optionally add your Gemini key:

       GEMINI_API_KEY=your_gemini_api_key

6. Start the website:

       python -m streamlit run app.py

## Recommendation Method

ReWatch retrieves candidate titles from TMDB and ranks them using
storyline text similarity and genre overlap.

When configured and available, Gemini embeddings are used for
semantic similarity. TF-IDF provides a local fallback.

The displayed similarity percentage is a relative algorithmic score,
not a guarantee that two stories are alike.

## API Attribution

This product uses the TMDB API but is not endorsed or certified by TMDB.

TMDB:
https://www.themoviedb.org/

## Privacy

API keys should be stored in local environment variables or the
deployment platform's secret manager. Never publish API keys in
source code or commit them to GitHub.
