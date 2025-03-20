"""
PubMed-related utility functions (Ultra-Advanced Edition)

Synchronous and asynchronous methods for fetching PubMed article references.
Requires 'PUB_MED_API' set in the environment (via .env or system variables).
"""

import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()  # Ensures environment variables from .env are available

logger = logging.getLogger("PubMed")
logger.setLevel(logging.INFO)

# Retrieve the PubMed API key
PUBMED_API_KEY = os.getenv("PUB_MED_API")
if not PUBMED_API_KEY:
    logger.warning(
        "PUB_MED_API is not found in the environment. PubMed references will be unavailable."
    )

###############################################################################
# Synchronous Fetch
###############################################################################

def fetch_pubmed_articles_sync(query: str, max_results: int = 5) -> list:
    """
    Retrieves relevant PubMed articles synchronously based on the provided query.

    Args:
        query (str): Search term(s) compatible with PubMed query language.
        max_results (int): Maximum number of article references to retrieve.

    Returns:
        list: A list of formatted article references. Each entry contains:
            - Title
            - Publication date
            - Source (journal/publisher)
            - Direct PubMed link

    Raises:
        None explicitly (errors are caught and returned as a single-item list).
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
        logger.info(f"Performing synchronous PubMed search with query: '{query}'")
        search_resp = httpx.get(esearch_url, params=search_params)
        search_resp.raise_for_status()

        data = search_resp.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            logger.info("No article IDs returned by PubMed for this query.")
            return ["No relevant PubMed articles found."]

        # Retrieve summaries for each article ID
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
        logger.error(f"Error during synchronous PubMed search: {e}")
        return [f"Error retrieving PubMed references: {str(e)}"]

###############################################################################
# Asynchronous Fetch
###############################################################################

async def async_fetch_pubmed_articles(query: str, max_results: int = 5) -> list:
    """
    Retrieves PubMed articles asynchronously based on the provided query.

    Args:
        query (str): Search term(s).
        max_results (int): Maximum number of article references to retrieve.

    Returns:
        list: A list of formatted article references, including title, date,
              source, and a direct PubMed link.

    Raises:
        None explicitly (errors are caught and returned as a single-item list).
    """
    if not PUBMED_API_KEY:
        return ["No PubMed API key provided."]

    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Performing asynchronous PubMed search with query: '{query}'")
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
                logger.info("No article IDs returned by PubMed for this query.")
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
            logger.error(f"Async error during PubMed search: {e}")
            return [f"Error retrieving PubMed references: {str(e)}"]
