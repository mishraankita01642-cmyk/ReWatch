import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_api_key():
    """Read the TMDB key from Streamlit secrets or .env."""

    # Try Streamlit secrets first.
    try:
        key = st.secrets.get("TMDB_API_KEY")
        if key and key.strip():
            return key.strip()
    except Exception:
        pass

    # Fall back to the .env file.
    key = os.getenv("TMDB_API_KEY", "")

    if key and key.strip():
        return key.strip()

    return None

def get_api_key():
    """Read the TMDB key from Streamlit secrets or .env."""

    try:
        key = st.secrets.get("TMDB_API_KEY")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("TMDB_API_KEY")


def api_request(endpoint, params=None):
    """Send a request to TMDB and report useful errors."""

    api_key = get_api_key()

    if not api_key or api_key == "YOUR_TMDB_API_KEY":
        raise RuntimeError(
            "TMDB API key is missing. Check .env and secrets.toml."
        )

    request_params = dict(params or {})
    request_params["api_key"] = api_key

    url = f"{BASE_URL}/{endpoint.lstrip('/')}"

    try:
        response = requests.get(
            url,
            params=request_params,
            timeout=20,
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as exc:
        status = (
            exc.response.status_code
            if exc.response is not None
            else "unknown"
        )

        if status in (401, 403):
            raise RuntimeError(
                "TMDB rejected the API key. Check that it is valid "
                "and active."
            ) from exc

        raise RuntimeError(
            f"TMDB returned HTTP error {status}."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "TMDB request timed out. Please try again."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "Could not connect to TMDB. Check your internet connection."
        ) from exc

def normalise_title(item, media_type=None):
    """Standardise movie and TV show information."""

    item_type = media_type or item.get("media_type")

    if item_type not in ("movie", "tv"):
        return None

    title = item.get("title") or item.get("name")

    if not title:
        return None

    return {
        "id": item.get("id"),
        "media_type": item_type,
        "title": title,
        "overview": item.get("overview") or "",
        "release_date": (
            item.get("release_date")
            or item.get("first_air_date")
            or ""
        ),
        "poster_path": item.get("poster_path"),
        "backdrop_path": item.get("backdrop_path"),
        "genre_ids": item.get("genre_ids") or [],
        "vote_average": item.get("vote_average") or 0,
    }


def search_titles(query):
    """Search movies and TV shows by title."""

    query = query.strip()

    if not query:
        return []

    data = api_request(
        "search/multi",
        {
            "query": query,
            "include_adult": False,
            "page": 1,
        },
    )

    results = []

    for item in data.get("results", []):
        title = normalise_title(item)

        if title:
            results.append(title)

    return results


def get_title_details(title_id, media_type):
    """Retrieve complete details for a movie or TV show."""

    if media_type not in ("movie", "tv"):
        raise ValueError("Media type must be 'movie' or 'tv'.")

    data = api_request(
        f"{media_type}/{title_id}",
        {"language": "en-US"},
    )

    genres = data.get("genres") or []

    return {
        "id": data.get("id"),
        "media_type": media_type,
        "title": data.get("title") or data.get("name") or "Unknown",
        "overview": data.get("overview") or "",
        "release_date": (
            data.get("release_date")
            or data.get("first_air_date")
            or ""
        ),
        "poster_path": data.get("poster_path"),
        "backdrop_path": data.get("backdrop_path"),
        "genres": [
            genre.get("name", "")
            for genre in genres
        ],
        "genre_ids": [
            genre["id"]
            for genre in genres
            if genre.get("id") is not None
        ],
        "vote_average": data.get("vote_average") or 0,
        "runtime": data.get("runtime"),
        "number_of_seasons": data.get("number_of_seasons"),
    }


def get_similar_titles(title_id, media_type):
    """Fetch similar titles from TMDB."""

    if media_type not in ("movie", "tv"):
        raise ValueError("Media type must be 'movie' or 'tv'.")

    data = api_request(
        f"{media_type}/{title_id}/similar",
        {
            "language": "en-US",
            "page": 1,
        },
    )

    results = []

    for item in data.get("results", []):
        title = normalise_title(item, media_type)

        if title and title["id"] != title_id:
            results.append(title)

    return results


def get_popular_titles(media_type="movie", language=None, page=1):
    """Fetch popular movies, TV shows, or Korean dramas."""

    if media_type not in ("movie", "tv"):
        raise ValueError("Media type must be 'movie' or 'tv'.")

    params = {
        "language": "en-US",
        "page": page,
    }

    if language:
        params["with_original_language"] = language
        params["sort_by"] = "popularity.desc"
        endpoint = f"discover/{media_type}"
    else:
        endpoint = f"{media_type}/popular"

    data = api_request(endpoint, params)

    results = []

    for item in data.get("results", []):
        title = normalise_title(item, media_type)

        if title:
            results.append(title)

    return results


def get_poster_url(poster_path):
    """Generate the full poster image URL."""

    if not poster_path:
        return None

    return f"{IMAGE_BASE_URL}{poster_path}"