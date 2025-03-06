"""
pubmed.py (Updated)

PubMed-related utility functions for Radiology, Cardiology, and Oncology references.
Includes both synchronous and optional asynchronous methods to query PubMed.

Environment variable required:
- PUB_MED_API: Your NCBI PubMed API key

Usage:
    from pubmed import fetch_pubmed_articles_sync, async_fetch_pubmed_articles
    ...
    references = fetch_pubmed_articles_sync("breast cancer imaging fibroadenoma")
"""

import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env if present

logger = logging.getLogger("PubMed")
logger.setLevel(logging.INFO)

PUBMED_API_KEY = os.getenv("PUB_MED_API")
if not PUBMED_API_KEY:
    logger.warning(
        "PUB_MED_API environment variable is not set. "
        "PubMed references may not be properly fetched."
    )


def fetch_pubmed_articles_sync(query: str, max_results: int = 5):
    """
    Synchronous function to fetch relevant PubMed articles based on a given query string.
    This can be used for Radiology, Cardiology, or Oncology topics.

    Args:
        query (str): The search query (e.g., 'breast cancer imaging fibroadenoma').
        max_results (int): Maximum number of articles to fetch.

    Returns:
        List[str]: A list of formatted reference strings.
    """
    if not PUBMED_API_KEY:
        return ["No PubMed API key provided or set in environment."]

    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    # Define your query parameters
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "api_key": PUBMED_API_KEY
    }

    try:
        logger.info(f"Searching PubMed with query: '{query}'")
        search_resp = httpx.get(esearch_url, params=search_params)
        search_resp.raise_for_status()

        data = search_resp.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            logger.info("No relevant article IDs found for this query.")
            return ["No relevant PubMed articles found."]

        summary_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json",
            "api_key": PUBMED_API_KEY
        }

        summary_resp = httpx.get(esummary_url, params=summary_params)
        summary_resp.raise_for_status()

        sum_data = summary_resp.json().get("result", {})
        references = []
        for pid in ids:
            article = sum_data.get(pid, {})
            title = article.get("title", "No title")
            pubdate = article.get("pubdate", "Unknown date")
            source = article.get("source", "Unknown source")
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
            references.append(f"**{title}** ({pubdate}, {source}) [Read more]({link})")

        return references if references else ["No relevant PubMed articles found."]
    except Exception as e:
        logger.error(f"Error fetching PubMed articles: {e}")
        return [f"Error retrieving PubMed references: {str(e)}"]


# Optional: Asynchronous version
async def async_fetch_pubmed_articles(query: str, max_results: int = 5):
    """
    Asynchronously fetch relevant PubMed articles for a given query.
    Suited for multi-domain usage (oncology, cardiology, radiology).

    Args:
        query (str): The search query (e.g. "cardiac pacemaker complications").
        max_results (int): Maximum number of articles to retrieve.

    Returns:
        List[str]: A list of formatted reference strings.
    """
    if not PUBMED_API_KEY:
        return ["No PubMed API key provided or set in environment."]

    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Async PubMed search with query: '{query}'")
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": max_results,
                "api_key": PUBMED_API_KEY
            }
            search_resp = await client.get(esearch_url, params=search_params)
            search_resp.raise_for_status()
            data = search_resp.json()

            ids = data.get("esearchresult", {}).get("idlist", [])
            if not ids:
                logger.info("No relevant article IDs found for this query.")
                return ["No relevant PubMed articles found."]

            summary_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "json",
                "api_key": PUBMED_API_KEY
            }
            summary_resp = await client.get(esummary_url, params=summary_params)
            summary_resp.raise_for_status()

            sum_data = summary_resp.json().get("result", {})
            references = []
            for pid in ids:
                article = sum_data.get(pid, {})
                title = article.get("title", "No title")
                pubdate = article.get("pubdate", "Unknown date")
                source = article.get("source", "Unknown source")
                link = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
                references.append(f"**{title}** ({pubdate}, {source}) [Read more]({link})")

            return references if references else ["No relevant PubMed articles found."]
        except Exception as e:
            logger.error(f"Async error fetching PubMed articles: {e}")
            return [f"Error retrieving PubMed references: {str(e)}"]
