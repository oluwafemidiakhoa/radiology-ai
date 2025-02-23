import os
import logging
import httpx

logger = logging.getLogger("PubMed")
logger.setLevel(logging.INFO)

# Read PubMed API key from environment
PUBMED_API_KEY = os.getenv("PUB_MED_API")
if not PUBMED_API_KEY:
    logger.error("PUB_MED_API is not set in the environment. PubMed references will not be fetched.")

def fetch_pubmed_articles(query, max_results=5):
    """
    Fetches relevant PubMed articles based on the given query.
    Returns a list of formatted references.
    """
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "api_key": PUBMED_API_KEY
    }
    
    try:
        logger.info(f"Searching PubMed with query: {query}")
        response = httpx.get(esearch_url, params=params)
        response.raise_for_status()
        data = response.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            logger.info("No relevant article IDs found for query.")
            return ["No relevant PubMed articles found."]
        return fetch_article_details(id_list)
    except Exception as e:
        logger.error(f"Error fetching PubMed articles: {e}")
        return [f"Error retrieving PubMed references: {str(e)}"]

def fetch_article_details(article_ids):
    """
    Retrieves detailed information for PubMed articles (title, journal, pubdate, link).
    Returns a list of formatted reference strings.
    """
    if not article_ids:
        return ["No relevant PubMed references found."]
    
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(article_ids),
        "retmode": "json",
        "api_key": PUBMED_API_KEY
    }
    
    try:
        response = httpx.get(esummary_url, params=params)
        response.raise_for_status()
        data = response.json()
        result = data.get("result", {})
        references = []
        for pid in article_ids:
            article = result.get(pid)
            if article:
                title = article.get("title", "No title available")
                journal = article.get("source", "Unknown journal")
                pubdate = article.get("pubdate", "Unknown date")
                link = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
                references.append(f"**{title}** - {journal} ({pubdate}) [Read more]({link})")
        if not references:
            return ["No relevant PubMed articles found."]
        return references
    except Exception as e:
        logger.error(f"Error fetching article details: {e}")
        return [f"Error retrieving PubMed references: {str(e)}"]

# Optional asynchronous functions for enhanced performance
async def async_fetch_pubmed_articles(query, max_results=5):
    """
    Asynchronously fetches relevant PubMed articles based on the given query.
    Returns a list of formatted references.
    """
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "api_key": PUBMED_API_KEY
    }
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Async searching PubMed with query: {query}")
            response = await client.get(esearch_url, params=params)
            response.raise_for_status()
            data = response.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                logger.info("No relevant article IDs found for query.")
                return ["No relevant PubMed articles found."]
            return await async_fetch_article_details(id_list)
        except Exception as e:
            logger.error(f"Async error fetching PubMed articles: {e}")
            return [f"Error retrieving PubMed references: {str(e)}"]

async def async_fetch_article_details(article_ids):
    """
    Asynchronously retrieves detailed information for PubMed articles.
    Returns a list of formatted reference strings.
    """
    if not article_ids:
        return ["No relevant PubMed references found."]
    
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(article_ids),
        "retmode": "json",
        "api_key": PUBMED_API_KEY
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(esummary_url, params=params)
            response.raise_for_status()
            data = response.json()
            result = data.get("result", {})
            references = []
            for pid in article_ids:
                article = result.get(pid, {})
                title = article.get("title", "No title available")
                pubdate = article.get("pubdate", "Unknown date")
                source = article.get("source", "Unknown source")
                link = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
                references.append(f"**{title}** - {source} ({pubdate}) [Read more]({link})")
            if not references:
                return ["No relevant PubMed articles found."]
            return references
        except Exception as e:
            logger.error(f"Async error fetching article details: {e}")
            return [f"Error retrieving PubMed references: {str(e)}"]
