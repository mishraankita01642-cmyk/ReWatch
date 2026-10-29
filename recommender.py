import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

MODEL_NAME = "gemini-embedding-001"


def get_gemini_api_key():
    """Read the Gemini API key."""

    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY")


@st.cache_resource
def get_gemini_client(api_key):
    """Create a reusable Gemini client."""

    return genai.Client(api_key=api_key)


@st.cache_data(ttl=86400, max_entries=500)
def generate_embeddings(texts, api_key):
    """Generate and cache semantic embeddings."""

    client = get_gemini_client(api_key)

    response = client.models.embed_content(
        model=MODEL_NAME,
        contents=list(texts),
        config=types.EmbedContentConfig(
            task_type="SEMANTIC_SIMILARITY",
            output_dimensionality=768,
        ),
    )

    if not response.embeddings:
        raise RuntimeError("Gemini returned no embeddings.")

    if len(response.embeddings) != len(texts):
        raise RuntimeError("Unexpected number of embeddings.")

    return [item.values for item in response.embeddings]


def genre_similarity(source, candidate):
    """Calculate genre overlap using Jaccard similarity."""

    first = set(source.get("genre_ids", []))
    second = set(candidate.get("genre_ids", []))

    if not first or not second:
        return 0.0

    return len(first & second) / len(first | second)


def tfidf_scores(source_text, candidate_texts):
    """Calculate text similarity locally without Gemini."""

    if not candidate_texts:
        return []

    documents = [source_text] + candidate_texts

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
        )

        matrix = vectorizer.fit_transform(documents)

        scores = cosine_similarity(
            matrix[0:1],
            matrix[1:],
        )[0]

        return [float(score) for score in scores]

    except ValueError:
        return [0.0] * len(candidate_texts)


def recommend_similar(source, candidates, limit=10):
    """Rank candidates by storyline and genre similarity."""

    if not candidates:
        return []

    source_text = (
        source.get("overview") or source.get("title", "")
    ).strip()

    candidate_texts = [
        (item.get("overview") or item.get("title", "")).strip()
        for item in candidates
    ]

    all_texts = [
        source_text or source.get("title", "Unknown title")
    ]

    for index, text in enumerate(candidate_texts):
        all_texts.append(
            text or candidates[index].get("title", "Unknown title")
        )

    method = "Gemini semantic embeddings"

    try:
        api_key = get_gemini_api_key()

        if not api_key or api_key == "YOUR_GEMINI_API_KEY":
            raise RuntimeError("Gemini API key is not configured.")

        vectors = generate_embeddings(tuple(all_texts), api_key)

        scores = cosine_similarity(
            [vectors[0]],
            vectors[1:],
        )[0]

        plot_scores = [float(score) for score in scores]

    except Exception as exc:
        # Keep the recommendation system usable without Gemini.
        print(f"Gemini unavailable; using TF-IDF: {exc}")

        plot_scores = tfidf_scores(
            all_texts[0],
            all_texts[1:],
        )

        method = "TF-IDF local fallback"

    results = []

    for candidate, plot_score in zip(candidates, plot_scores):
        genre_score = genre_similarity(source, candidate)

        final_score = (
            0.80 * max(0.0, min(1.0, plot_score))
            + 0.20 * genre_score
        )

        result = dict(candidate)
        result["plot_similarity"] = round(plot_score, 4)
        result["genre_similarity"] = round(genre_score, 4)
        result["similarity_score"] = round(final_score, 4)
        result["matching_method"] = method

        results.append(result)

    results.sort(
        key=lambda item: item["similarity_score"],
        reverse=True,
    )

    return results[:limit]