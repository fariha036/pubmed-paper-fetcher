import requests
from typing import List, Dict, Optional, Any
import csv
import re

PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Heuristics for non-academic affiliations
NON_ACADEMIC_KEYWORDS = [
    "pharma", "pharmaceutical", "biotech", "inc", "ltd", "gmbh", "corp", "company", "co.", "llc", "plc", "s.a.", "s.p.a.", "industries", "laboratories", "labs", "biosciences", "therapeutics", "genomics", "diagnostics"
]
ACADEMIC_KEYWORDS = [
    "university", "college", "institute", "school", "faculty", "hospital", "center", "centre", "department", "academy"
]

def is_non_academic_affiliation(affiliation: str) -> bool:
    """Return True if the affiliation is likely non-academic (pharma/biotech)."""
    affil = affiliation.lower()
    if any(word in affil for word in NON_ACADEMIC_KEYWORDS):
        if not any(word in affil for word in ACADEMIC_KEYWORDS):
            return True
    return False

def fetch_pubmed_ids(query: str, retmax: int = 100, debug: bool = False) -> List[str]:
    """Fetch PubMed IDs for a given query using the esearch API."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json"
    }
    resp = requests.get(PUBMED_API_URL, params=params)
    if debug:
        print(f"[DEBUG] ESearch URL: {resp.url}")
        print(f"[DEBUG] ESearch Response: {resp.text[:500]}")
    resp.raise_for_status()
    data = resp.json()
    return data["esearchresult"]["idlist"]

def fetch_pubmed_details(pubmed_ids: List[str], debug: bool = False) -> List[Dict[str, Any]]:
    """Fetch details for a list of PubMed IDs using the efetch API (returns XML)."""
    if not pubmed_ids:
        return []
    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml"
    }
    resp = requests.get(PUBMED_FETCH_URL, params=params)
    if debug:
        print(f"[DEBUG] EFetch URL: {resp.url}")
        print(f"[DEBUG] EFetch Response: {resp.text[:500]}")
    resp.raise_for_status()
    # Parse XML
    import xml.etree.ElementTree as ET
    root = ET.fromstring(resp.text)
    results = []
    for article in root.findall(".//PubmedArticle"):
        try:
            pmid = article.findtext(".//PMID")
            title = article.findtext(".//ArticleTitle")
            pub_date_elem = article.find(".//PubDate")
            if pub_date_elem is not None:
                year = pub_date_elem.findtext("Year") or ""
                month = pub_date_elem.findtext("Month") or ""
                day = pub_date_elem.findtext("Day") or ""
                pub_date = f"{year}-{month}-{day}".strip("-")
            else:
                pub_date = ""
            authors = []
            companies = set()
            non_academic_authors = []
            corresponding_email = None
            for author in article.findall(".//Author"):
                name = []
                forename = author.findtext("ForeName")
                lastname = author.findtext("LastName")
                if forename:
                    name.append(forename)
                if lastname:
                    name.append(lastname)
                fullname = " ".join(name)
                affiliation_info = author.findall("AffiliationInfo")
                for affil in affiliation_info:
                    affil_text = affil.findtext("Affiliation") or ""
                    if is_non_academic_affiliation(affil_text):
                        non_academic_authors.append(fullname)
                        companies.add(affil_text)
                    # Try to extract email
                    email_match = re.search(r"[\w\.-]+@[\w\.-]+", affil_text)
                    if email_match and not corresponding_email:
                        corresponding_email = email_match.group(0)
            results.append({
                "PubmedID": pmid,
                "Title": title,
                "Publication Date": pub_date,
                "Non-academicAuthor(s)": "; ".join(non_academic_authors),
                "CompanyAffiliation(s)": "; ".join(companies),
                "Corresponding Author Email": corresponding_email or ""
            })
        except Exception as e:
            if debug:
                print(f"[DEBUG] Error parsing article: {e}")
            continue
    return results

def filter_papers_with_non_academic_authors(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only papers with at least one non-academic author."""
    return [p for p in papers if p["Non-academicAuthor(s)"]]

def save_papers_to_csv(papers: List[Dict[str, Any]], filename: str) -> None:
    """Save the list of papers to a CSV file with the required columns."""
    if not papers:
        return
    fieldnames = [
        "PubmedID",
        "Title",
        "Publication Date",
        "Non-academicAuthor(s)",
        "CompanyAffiliation(s)",
        "Corresponding Author Email"
    ]
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper) 