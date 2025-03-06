"""
PubMed-related utility functions (Updated)

Provides synchronous and optional asynchronous methods to fetch article references from PubMed.
Requires the 'PUB_MED_API' key in .env or environment variables.
"""

import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()  # Ensure environment variables are loaded

logger = logging.getLogger("PubMed")
logger.setLevel(logging.INFO)

PUBMED_API_KEY = os.getenv("PUB_MED_API")
if not PUBMED_API_KEY:
    logger.warning("PUB_MED_API is not set in the environment. PubMed references may be unavailable.")

def fetch_pubmed_articles_sync(query: str, max_results: int = 5):
    """
    Synchronous function to fetch relevant PubMed articles based on a given query.
    Returns a list of formatted references.
    """
    if not PUBMED_API_KEY:
        return ["No PubMed API key provided."]

    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

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
            logger.info("No relevant article IDs found for query.")
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


# Optional Async Implementation
async def async_fetch_pubmed_articles(query: str, max_results: int = 5):
    """
    Asynchronously fetches relevant PubMed articles based on the given query.
    Returns a list of formatted references.
    """
    if not PUBMED_API_KEY:
        return ["No PubMed API key provided."]

    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Async searching PubMed with query: '{query}'")
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
                logger.info("No relevant article IDs found for query.")
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
