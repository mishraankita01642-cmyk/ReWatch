import streamlit as st

from tmdb_api import (
    search_titles as tmdb_search_titles,
    get_popular_titles,
    get_title_details,
    get_similar_titles,
    get_poster_url,
)

try:
    from recommender import recommend_similar
except ImportError:
    recommend_similar = None


def scroll_to_details():
    st.components.v1.html(
        """
        <script>
        function scrollToDetails() {
            const target =
                window.parent.document.getElementById("title-details");

            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        }

        setTimeout(scrollToDetails, 300);
        setTimeout(scrollToDetails, 800);
        setTimeout(scrollToDetails, 1500);
        </script>
        """,
        height=0,
    )
    
# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ReWatch | Discover Your Next Favourite",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "search_media_filter" not in st.session_state:
    st.session_state.search_media_filter = "All"
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "selected_title" not in st.session_state:
    st.session_state.selected_title = None

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []


# --------------------------------------------------
# THEME AND CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(91, 33, 182, 0.18),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(37, 99, 235, 0.13),
                transparent 30%
            ),
            #080910;
        color: #f5f5f7;
    }

    [data-testid="stSidebar"] {
        background: #0d0e18;
        border-right: 1px solid #25253a;
    }

    h1, h2, h3 {
        color: #ffffff !important;
    }

    p, label, span {
        color: #dedee8;
    }

    .rewatch-logo {
        font-size: 34px;
        font-weight: 900;
        letter-spacing: -1px;
        color: white;
    }

    .rewatch-logo span {
        color: #a78bfa;
    }

    .hero {
        padding: 35px;
        border-radius: 22px;
        background:
            linear-gradient(
                110deg,
                rgba(42, 22, 80, 0.98),
                rgba(13, 22, 49, 0.97)
            );
        border: 1px solid #373052;
        margin-bottom: 28px;
    }

    .hero-label {
        color: #c4b5fd;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .hero-title {
        font-size: 42px;
        line-height: 1.15;
        font-weight: 900;
        margin: 12px 0;
        color: white;
    }

    .hero-text {
        font-size: 16px;
        line-height: 1.7;
        color: #dedcf0;
        max-width: 700px;
    }

    .section-subtitle {
        color: #aaaac0;
        margin-top: -10px;
        margin-bottom: 20px;
    }

    .movie-card {
        background: #11121e;
        border: 1px solid #28283c;
        border-radius: 15px;
        padding: 10px;
        height: 100%;
    }

    .movie-title {
        color: white;
        font-size: 15px;
        font-weight: 750;
        margin-top: 10px;
        margin-bottom: 4px;
    }

    .movie-meta {
        color: #aaaac0;
        font-size: 12px;
        margin-bottom: 8px;
    }

    .detail-panel {
        background: #11121e;
        border: 1px solid #34314f;
        padding: 24px;
        border-radius: 18px;
        margin-top: 30px;
        margin-bottom: 25px;
    }

    .detail-overview {
        font-size: 15px;
        line-height: 1.8;
        color: #d8d8e6;
    }

    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #6250a5;
        background: #292044;
        color: white;
        font-weight: 650;
        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #a78bfa;
        background: #403064;
        color: white;
    }

    div[data-testid="stTextInput"] input {
        background: #121321;
        color: white;
        border: 1px solid #383850;
        border-radius: 10px;
    }

    div[data-testid="stSelectbox"] div {
        border-radius: 8px;
    }

    .footer {
        text-align: center;
        color: #77778f;
        padding: 25px 0 10px 0;
        font-size: 12px;
    }

    hr {
        border-color: #29293c;
    }
/* ========================================
   REWATCH - STREAMING STYLE SEARCH
======================================== */

.search-header {
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 6px;
}

.search-subtitle {
    color: #aaaac0;
    font-size: 15px;
    margin-bottom: 24px;
}

div[data-testid="stTextInput"]:has(input[aria-label="Search ReWatch"]) {
    margin-bottom: 12px;
}

div[data-testid="stTextInput"]:has(input[aria-label="Search ReWatch"]) input {
    background: #171827 !important;
    color: #ffffff !important;
    border: 1px solid #35374d !important;
    border-radius: 14px !important;
    min-height: 56px !important;
    padding-left: 18px !important;
    font-size: 17px !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}

div[data-testid="stTextInput"]:has(input[aria-label="Search ReWatch"]) input:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
}

div[data-testid="stTextInput"]:has(input[aria-label="Search ReWatch"]) input::placeholder {
    color: #85869e !important;
}

.search-chip-label {
    color: #b9b9cc;
    font-size: 13px;
    margin-top: 18px;
    margin-bottom: 10px;
}

.search-chip {
    background: #1c1d30;
    border: 1px solid #34354d;
    border-radius: 20px;
    padding: 9px 15px;
    color: #eeeeff;
    text-align: center;
}

.search-result-heading {
    font-size: 22px;
    font-weight: 750;
    color: white;
    margin-top: 28px;
    margin-bottom: 16px;
}

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SAFE HELPERS
# --------------------------------------------------

def safe_text(value, default=""):
    """Return readable text even when a field is missing."""
    if value is None:
        return default
    return str(value)


def get_title_id(item):
    """Get a title ID from a result dictionary."""
    if not isinstance(item, dict):
        return None
    return item.get("id") or item.get("movie_id") or item.get("tv_id")


def get_media_type(item, default="movie"):
    """Determine whether a result is a movie or TV show."""
    if not isinstance(item, dict):
        return default

    media_type = item.get("media_type") or item.get("type")

    if media_type in ("movie", "tv"):
        return media_type

    if item.get("first_air_date") and not item.get("release_date"):
        return "tv"

    return default


def get_title_name(item):
    """Support common TMDB and custom result field names."""
    if not isinstance(item, dict):
        return "Untitled"

    return (
        item.get("title")
        or item.get("name")
        or item.get("original_title")
        or item.get("original_name")
        or "Untitled"
    )


def get_year(item):
    """Extract the year from the available release date."""
    if not isinstance(item, dict):
        return ""

    date_value = (
        item.get("release_date")
        or item.get("first_air_date")
        or ""
    )

    if isinstance(date_value, str) and len(date_value) >= 4:
        return date_value[:4]

    return ""


def get_rating(item):
    """Return a readable rating."""
    if not isinstance(item, dict):
        return "N/A"

    rating = item.get("vote_average")

    if rating is None:
        rating = item.get("rating")

    try:
        rating = float(rating)
        if rating > 0:
            return f"{rating:.1f}/10"
    except (ValueError, TypeError):
        pass

    return "Not rated"


def get_overview(item):
    """Get the synopsis or overview."""
    if not isinstance(item, dict):
        return "No storyline is available."

    return (
        item.get("overview")
        or item.get("storyline")
        or item.get("description")
        or "No storyline is available for this title."
    )


def get_poster(item):
    """Get a poster URL while supporting different API formats."""
    if not isinstance(item, dict):
        return None

    poster = (
        item.get("poster_url")
        or item.get("poster")
        or item.get("image")
    )

    if isinstance(poster, str) and poster.startswith("http"):
        return poster

    poster_path = item.get("poster_path")

    if poster_path:
        try:
            return get_poster_url(poster_path)
        except Exception:
            if isinstance(poster_path, str) and poster_path.startswith("http"):
                return poster_path

    # Some versions of get_poster_url() accept a whole title object.
    try:
        return get_poster_url(item)
    except Exception:
        return None


def normalize_results(results, media_type=None):
    """Convert API results to a consistent list of title dictionaries."""
    if results is None:
        return []

    if isinstance(results, dict):
        if isinstance(results.get("results"), list):
            results = results["results"]
        else:
            results = [results]

    if not isinstance(results, (list, tuple)):
        return []

    normalized = []

    for item in results:
        if not isinstance(item, dict):
            continue

        title_id = get_title_id(item)

        if title_id is None:
            continue

        title = dict(item)
        title["id"] = title_id
        title["title"] = get_title_name(item)
        title["media_type"] = media_type or get_media_type(item)
        normalized.append(title)

    return normalized


def search_titles(query, media_type=None):
    """Search TMDB safely and optionally filter by content type."""
    try:
        results = tmdb_search_titles(query)
        results = normalize_results(results)

        if media_type:
            results = [
                item for item in results
                if item.get("media_type") == media_type
            ]

        return results

    except Exception as e:
        st.error(f"Search error: {type(e).__name__}: {e}")
        print(f"Search error: {type(e).__name__}: {e}")
        return []


def load_details(title_id, media_type):
    """Load full details for a selected title."""
    try:
        details = get_title_details(title_id, media_type)

        if isinstance(details, dict):
            details = dict(details)
            details["id"] = details.get("id", title_id)
            details["media_type"] = media_type
            details["title"] = get_title_name(details)
            return details

    except Exception as error:
        print(f"Title details error: {error}")

    return None


def open_title(item):
    if not item or item.get("id") is None:
        st.error("Unable to open this title.")
        return

    st.session_state.selected_title = {
        "id": item["id"],
        "media_type": item.get("media_type", "movie"),
        "title": item.get("title") or item.get("name", "Selected title"),
    }

    st.session_state.recommendations = []
    st.session_state.page = "Title Details"
    st.rerun()

def get_recommendations(details):
    """Get recommendations using the existing project functions."""
    title_id = get_title_id(details)
    media_type = get_media_type(details)

    # First, try the existing recommendation module.
    if recommend_similar is not None:
        try:
            results = recommend_similar(details)
            results = normalize_results(results)

            results = [
                item for item in results
                if str(get_title_id(item)) != str(title_id)
            ]

            if results:
                return results[:8]

        except Exception as error:
            print(f"Local recommender error: {error}")

    # Fall back to TMDB similar titles.
    try:
        results = get_similar_titles(title_id, media_type)
        results = normalize_results(results, media_type)

        results = [
            item for item in results
            if str(get_title_id(item)) != str(title_id)
        ]

        return results[:8]

    except Exception as error:
        print(f"Similar titles error: {error}")
        return []
def save_search_history(query):
    query = query.strip()

    if not query:
        return

    history = st.session_state.get("search_history", [])

    # Move repeated searches to the top.
    history = [
        item for item in history
        if item.lower() != query.lower()
    ]

    history.insert(0, query)

    # Keep the latest 8 searches.
    st.session_state.search_history = history[:8]



# --------------------------------------------------
# TITLE CARD
# --------------------------------------------------

def render_title_card(item, section_key):
    """Display a poster and a working About / Explore button."""
    title_id = get_title_id(item)

    if title_id is None:
        return

    title = get_title_name(item)
    year = get_year(item)
    rating = get_rating(item)
    poster_url = get_poster(item)

    with st.container(border=True):
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.markdown(
                """
                <div style="
                    height:250px;
                    background:#19192a;
                    border-radius:10px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:#aaaac0;
                    text-align:center;
                ">
                    Poster unavailable
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<div class='movie-title'>{title}</div>",
            unsafe_allow_html=True,
        )

        metadata = " • ".join(
            part for part in [year, rating] if part
        )

        st.markdown(
            f"<div class='movie-meta'>{metadata or 'Details unavailable'}</div>",
            unsafe_allow_html=True,
        )

        if st.button(
            "About / Explore",
            key=f"{section_key}_{item.get('media_type')}_{title_id}_{title}",
            use_container_width=True,
        ):
            open_title(item)


def render_title_grid(items, section_key, columns=5):
    """Display title cards in a responsive row-based grid."""
    items = normalize_results(items)

    if not items:
        st.info("No titles to display right now.")
        return

    # Give each grid rendered on this page a unique identifier.
    if "_grid_render_counter" not in globals():
        globals()["_grid_render_counter"] = 0

    globals()["_grid_render_counter"] += 1
    unique_section_key = (
        f"{section_key}_{globals()['_grid_render_counter']}"
    )

    for start in range(0, len(items), columns):
        row_items = items[start:start + columns]
        cols = st.columns(columns)

        for index, item in enumerate(row_items):
            with cols[index]:
                render_title_card(
                    item,
                    f"{unique_section_key}_{start}_{index}",
                )
# --------------------------------------------------
# TITLE DETAILS / ABOUT THIS TITLE
# --------------------------------------------------

def show_details():
    """Show full details for the currently selected movie or drama."""
    selected = st.session_state.selected_title

    if not selected:
        return

    title_id = selected.get("id")
    media_type = selected.get("media_type", "movie")

    st.markdown("---")
    st.markdown('<div id="title-details"></div>',unsafe_allow_html=True)

    st.markdown("## About this title")

    details = load_details(title_id, media_type)

    if not details:
        st.warning(
            "The title was selected, but its details could not be loaded. "
            "Check your TMDB API key and the get_title_details() function "
            "in tmdb_api.py."
        )

        if st.button("Close details", key="close_failed_details"):
            st.session_state.selected_title = None
            st.rerun()

        return

    title = get_title_name(details)
    poster = get_poster(details)
    year = get_year(details)
    rating = get_rating(details)
    overview = get_overview(details)

    left, right = st.columns([1, 2.3])

    with left:
        if poster:
            st.image(poster, use_container_width=True)
        else:
            st.info("Poster unavailable.")

    with right:
        st.markdown(f"# {title}")

        details_line = []

        if year:
            details_line.append(year)

        details_line.append(
            "Movie" if media_type == "movie" else "Drama / TV Show"
        )

        details_line.append(f"⭐ {rating}")

        st.caption("  •  ".join(details_line))

        genres = details.get("genres", [])

        if isinstance(genres, list) and genres:
            genre_names = []

            for genre in genres:
                if isinstance(genre, dict):
                    name = genre.get("name")
                    if name:
                        genre_names.append(name)
                elif isinstance(genre, str):
                    genre_names.append(genre)

            if genre_names:
                st.write("**Genres:** " + ", ".join(genre_names))

        st.markdown("### Storyline")
        st.markdown(
            f"<div class='detail-overview'>{overview}</div>",
            unsafe_allow_html=True,
        )

        st.write("")

        watchlist_key = f"{media_type}_{title_id}"

        is_saved = any(
            f"{entry.get('media_type')}_{entry.get('id')}" == watchlist_key
            for entry in st.session_state.watchlist
        )

        if is_saved:
            st.success("Added to your watchlist")
        elif st.button(
            "＋ Add to Watchlist",
            key=f"add_watchlist_{watchlist_key}",
        ):
            st.session_state.watchlist.append(
                {
                    "id": title_id,
                    "title": title,
                    "media_type": media_type,
                    "poster_path": details.get("poster_path"),
                    "poster_url": get_poster(details),
                    "release_date": details.get("release_date"),
                    "first_air_date": details.get("first_air_date"),
                    "vote_average": details.get("vote_average"),
                }
            )
            st.success(f"{title} added to your watchlist!")
            st.rerun()

        if st.button(
            "Find Similar Stories",
            key=f"similar_{watchlist_key}",
        ):
            st.session_state.recommendations = get_recommendations(details)

    recommendations = st.session_state.recommendations

    if recommendations:
        st.markdown("### Because you explored this title")
        render_title_grid(
            recommendations,
            f"recommendations_{title_id}",
            columns=4,
        )

    if st.button("Close title details", key=f"close_{watchlist_key}"):
        st.session_state.selected_title = None
        st.session_state.recommendations = []
        st.rerun()

        

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        "<div class='rewatch-logo'>Re<span>Watch</span> 🎬</div>",
        unsafe_allow_html=True,
    )

    st.caption("Find your next favourite story.")
    st.markdown("---")

    pages = [
        "Home",
        "Search",
        "Movies",
        "Dramas",
        "Watchlist",
        "About",
    ]
    
    if st.session_state.get("selected_title"):
        pages.append("Title Details")

    for page_name in pages:
        if st.button(
            page_name,
            key=f"nav_{page_name}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.page == page_name
                else "secondary"
            ),
        ):
            st.session_state.page = page_name
            st.rerun()

    st.markdown("---")
    st.caption("Discover • Explore • ReWatch")


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if st.session_state.page == "Home":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">Your next story starts here</div>
            <div class="hero-title">
                Every story deserves<br>another watch.
            </div>
            <div class="hero-text">
                Discover movies and dramas, explore their stories,
                and find your next favourite through ReWatch.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Popular right now")
    st.markdown(
        "<div class='section-subtitle'>"
        "Explore movies and shows people are watching."
        "</div>",
        unsafe_allow_html=True,
    )

    popular_titles = []

    # Use popular titles if your API module supports them.
    try:
        from tmdb_api import get_popular_titles

        popular_titles = normalize_results(get_popular_titles())

    except (ImportError, AttributeError):
        popular_titles = []

    except Exception as error:
        print(f"Popular titles error: {error}")

    # Fallback: search for well-known titles.
    if not popular_titles:
        fallback_queries = [
            "Spider-Man",
            "Interstellar",
            "Inception",
            "Stranger Things",
            "Wednesday",
        ]

        for query in fallback_queries:
            results = search_titles(query)

            for item in results:
                if not any(
                    str(get_title_id(existing)) == str(get_title_id(item))
                    and existing.get("media_type") == item.get("media_type")
                    for existing in popular_titles
                ):
                    popular_titles.append(item)

                if len(popular_titles) >= 15:
                    break

            if len(popular_titles) >= 15:
                break

    render_title_grid(popular_titles[:10], "home_popular", columns=5)

    st.markdown("---")
    st.markdown("## Find something to watch")

    quick_query = st.text_input(
        "Search movies and dramas",
        placeholder="Try Spider-Man, Wednesday, Interstellar...",
        key="home_search",
    )

    if st.button("Search titles", key="home_search_button"):
        st.session_state.search_query = quick_query.strip()
        st.session_state.page = "Search"
        st.rerun()
    
    # Important: keep this outside the catalogue-loading code.
    show_details()
    

# --------------------------------------------------
# SEARCH PAGE
# --------------------------------------------------

elif st.session_state.page == "Search":

    st.markdown(
        """
        <div class="search-header">Search</div>
        <div class="search-subtitle">
            Discover movies, series, and stories worth watching.
        </div>
        """,
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Search ReWatch",
        value=st.session_state.search_query,
        placeholder="Search for movies, dramas, actors, or titles...",
        key="search_page_input",
        label_visibility="collapsed",
    )

    # Update the stored query as the user types.
    new_query = query.strip()

    if new_query:
            st.session_state.search_query = new_query

    # Content filters

    st.markdown("### Explore by type")

    if "search_media_filter" not in st.session_state:
        st.session_state.search_media_filter = "All"

    filter_options = ["All", "Movies", "Dramas / TV Shows"]
    filter_cols = st.columns(3)

    for index, option in enumerate(filter_options):
        with filter_cols[index]:
            if st.button(
                option,
                key=f"filter_{index}",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.search_media_filter == option
                    else "secondary"
                ),
            ):
                st.session_state.search_media_filter = option
                st.rerun()

    media_filter = st.session_state.search_media_filter

    # Trending / suggested searches

    if not query.strip():

        st.markdown("### Recent searches")

        history = st.session_state.get("search_history", [])

        if history:
            for index, term in enumerate(history):
                col1, col2 = st.columns([5, 1])

                with col1:
                    if st.button(
                        f"↻  {term}",
                        key=f"history_{index}",
                        use_container_width=True,
                    ):
                        st.session_state.search_query = term
                        save_search_history(term)
                        st.rerun()

                with col2:
                    if st.button(
                        "✕",
                        key=f"remove_history_{index}",
                        help="Remove from search history",
                    ):
                        st.session_state.search_history = [
                            item for item in history
                            if item != term
                        ]
                        st.rerun()

            if st.button("Clear search history", key="clear_search_history"):
                st.session_state.search_history = []
                st.rerun()

        else:
            st.info(
                "Your search history is empty. Search for a movie or drama "
                "and it will appear here."
            )

        st.markdown(
            "<div class='search-result-heading'>Popular searches</div>",
            unsafe_allow_html=True,
        )

        popular_results = []

        for media_type in ["movie", "tv"]:
            try:
                titles = get_popular_titles(media_type)
                popular_results.extend(titles)

                if not titles:
                    st.warning(
                        f"TMDB returned no popular titles for {media_type}."
                    )

            except Exception as e:
                st.error(
                    f"Could not load popular {media_type} titles: {e}"
                )
                print(f"Popular {media_type} error: {type(e).__name__}: {e}")
        if popular_results:
            unique_titles = {}

            for item in popular_results:
                title_id = get_title_id(item)
                media_type = item.get("media_type", "movie")

                if title_id is not None:
                    unique_titles[(media_type, str(title_id))] = item

            popular_results = list(unique_titles.values())

            render_title_grid(
                popular_results[:10],
                "search_popular",
                columns=5,
            )
        else:
            st.info("Popular titles are temporarily unavailable.")


    else:
        results = search_titles(query)

        if media_filter == "Movies":
            results = [
                item for item in results
                if item.get("media_type") == "movie"
            ]

        elif media_filter == "Dramas / TV Shows":
            results = [
                item for item in results
                if item.get("media_type") == "tv"
            ]

        if query.strip():
            save_search_history(query)
    
        if results:
            st.markdown(
                f"<div class='search-result-heading'>"
                f"Results for {query}</div>",
                unsafe_allow_html=True,
            )

            render_title_grid(
                results[:20],
                "search_results",
                columns=5,
            )

        else:
            st.markdown("### No titles found")
            st.write(
                "Try another title, check the spelling, "
                "or explore one of the trending searches above."
            )

    show_details()

# --------------------------------------------------
# MOVIES PAGE
# --------------------------------------------------

elif st.session_state.page == "Movies":

    st.title("Movies")
    st.write("Explore movies and open any title to read its storyline.")

    movie_query = st.text_input(
        "Find a movie",
        placeholder="Search for movies...",
        key="movies_query",
    )

    if st.button("Find Movies", key="movies_search_button"):
        st.session_state.movies_search = movie_query.strip()
        st.session_state.selected_title = None
        st.rerun()

    stored_query = st.session_state.get("movies_search", "")

    if stored_query:
        movie_results = search_titles(stored_query, "movie")
    else:
        movie_results = []

        for query in ["Interstellar", "Spider-Man", "Inception"]:
            movie_results.extend(search_titles(query, "movie"))

        # Remove duplicate movie IDs.
        unique = {}
        for item in movie_results:
            unique[str(get_title_id(item))] = item

        movie_results = list(unique.values())

    render_title_grid(movie_results[:20], "movies", columns=5)
    show_details()


# --------------------------------------------------
# DRAMAS PAGE
# --------------------------------------------------

elif st.session_state.page == "Dramas":

    st.title("Dramas & TV Shows")
    st.write("Discover series, dramas, and stories worth watching.")

    drama_query = st.text_input(
        "Find a drama",
        placeholder="Search for a drama or TV show...",
        key="dramas_query",
    )

    if st.button("Find Dramas", key="dramas_search_button"):
        st.session_state.dramas_search = drama_query.strip()
        st.session_state.selected_title = None
        st.rerun()

    stored_query = st.session_state.get("dramas_search", "")

    if stored_query:
        drama_results = search_titles(stored_query, "tv")
    else:
        drama_results = []

        for query in ["Wednesday", "Stranger Things", "The Last of Us"]:
            drama_results.extend(search_titles(query, "tv"))

        unique = {}
        for item in drama_results:
            unique[str(get_title_id(item))] = item

        drama_results = list(unique.values())

    render_title_grid(drama_results[:20], "dramas", columns=5)
    show_details()


# --------------------------------------------------
# WATCHLIST PAGE
# --------------------------------------------------

elif st.session_state.page == "Watchlist":

    st.title("My Watchlist")
    st.write("Your saved titles for your next movie or drama night.")

    if not st.session_state.watchlist:
        st.info(
            "Your watchlist is empty. Open a title and select "
            "'Add to Watchlist' to save it."
        )

    else:
        render_title_grid(
            st.session_state.watchlist,
            "watchlist",
            columns=5,
        )

        st.markdown("---")

        if st.button("Clear Watchlist", key="clear_watchlist"):
            st.session_state.watchlist = []
            st.rerun()

    show_details()


# --------------------------------------------------
# ABOUT PAGE
# --------------------------------------------------

elif st.session_state.page == "About":

    st.title("About ReWatch")

    st.markdown(
        """
        <div class="detail-panel">
            <h2>Discover stories. Find your next favourite.</h2>
            <p class="detail-overview">
                ReWatch is a movie and drama discovery website designed
                to help users explore titles, read storylines, and find
                similar content.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### What you can do")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎬 Explore")
        st.write("Browse movies, dramas, posters, ratings, and release years.")

        st.markdown("#### 🔎 Search")
        st.write("Search for a title and open its details.")

    with col2:
        st.markdown("#### 📖 Read storylines")
        st.write("Learn about a title before deciding to watch it.")

        st.markdown("#### ⭐ Watchlist")
        st.write("Save titles you want to watch during your current session.")

    st.markdown("---")
    st.caption(
        "Movie metadata and posters are retrieved through The Movie Database (TMDB)."
    )


# --------------------------------------------------
# TITLE DETAILS PAGE
# --------------------------------------------------

elif st.session_state.page == "Title Details":

    if st.button("← Back to previous page", key="details_back"):
        st.session_state.page = "Home"
        st.session_state.selected_title = None
        st.session_state.recommendations = []
        st.rerun()

    show_details()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        ReWatch · Discover your next favourite story
    </div>
    """,
    unsafe_allow_html=True,
)