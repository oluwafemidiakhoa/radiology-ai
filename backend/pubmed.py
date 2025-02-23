import requests
import os

# PubMed API Key
PUBMED_API_KEY = os.getenv("PUB_MED_API")  # Ensure it's set in your environment

def fetch_pubmed_articles(query, max_results=5):
    """
    Fetches relevant PubMed articles based on the given query.
    Returns a list of formatted references.
    """
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "api_key": PUBMED_API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    if "esearchresult" in data and "idlist" in data["esearchresult"]:
        article_ids = data["esearchresult"]["idlist"]
        return fetch_article_details(article_ids)
    return []

def fetch_article_details(article_ids):
    """
    Retrieves detailed information (title, authors, journal, link) for PubMed articles.
    """
    if not article_ids:
        return ["No relevant PubMed references found."]
    
    details_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(article_ids),
        "retmode": "json",
        "api_key": PUBMED_API_KEY
    }

    response = requests.get(details_url, params=params)
    data = response.json()
    
    articles = []
    for article_id in article_ids:
        if article_id in data["result"]:
            article = data["result"][article_id]
            title = article.get("title", "No title available")
            journal = article.get("source", "Unknown journal")
            pubdate = article.get("pubdate", "Unknown date")
            link = f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/"

            articles.append(f"{title} - {journal} ({pubdate}) [Read more]({link})")

    return articles
