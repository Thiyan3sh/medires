import requests
from elasticsearch import Elasticsearch
import re

# API Base URLs
PUBMED_API_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
CLINICAL_TRIALS_API_BASE = "https://clinicaltrials.gov/api/query/study_fields"
MESH_API_BASE = "https://id.nlm.nih.gov/mesh/lookup/lookup.json"
ELASTICSEARCH_URL = "http://localhost:9200"

# Connect to Elasticsearch
es = Elasticsearch([ELASTICSEARCH_URL])

# Fetch papers from PubMed using the Entrez API (esearch)
def search_pubmed(query):
    params = {
        'db': 'pubmed',
        'term': query,
        'retmode': 'json',
        'retmax': 10  # Retrieve only the top 10 results (can be adjusted)
    }
    response = requests.get(PUBMED_API_BASE, params=params)
    data = response.json()
    
    # Return list of PubMed paper IDs
    return data['esearchresult']['idlist']

# Fetch full paper details from PubMed using efetch
def get_pubmed_details(paper_ids):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    ids = ",".join(paper_ids)
    
    params = {
        'db': 'pubmed',
        'id': ids,
        'retmode': 'xml',  # We prefer XML format for easy parsing
    }
    
    response = requests.get(base_url, params=params)
    data = response.text  # Raw XML response
    
    return data

# Fetch clinical trials from ClinicalTrials.gov API
def search_clinical_trials(query):
    params = {
        'expr': query,
        'fields': 'NCTId,Title,Condition,Status',
        'max_rnk': 10  # Limit results to 10 trials
    }
    response = requests.get(CLINICAL_TRIALS_API_BASE, params=params)
    data = response.json()
    trials = data.get('StudyFieldsResponse', {}).get('StudyFields', [])
    return trials

# Fetch related terms from MeSH API
def get_related_terms(term):
    url = f"{MESH_API_BASE}?term={term}"
    response = requests.get(url)
    data = response.json()
    related_terms = [entry['label'] for entry in data['meshTermList']]
    return related_terms

# Function to index documents (papers, trials, etc.) into Elasticsearch
def index_document(index, doc_type, doc_id, body):
    es.index(index=index, doc_type=doc_type, id=doc_id, body=body)

# Function to search Elasticsearch index with a query
def search_elasticsearch(index, query):
    body = {
        "query": {
            "match": {
                "_all": query
            }
        }
    }
    result = es.search(index=index, body=body)
    return result['hits']['hits']

# Basic query parser to handle AND, OR, and NOT
def parse_boolean_query(query):
    query = query.lower().replace('and', 'AND').replace('or', 'OR').replace('not', 'NOT')
    return query

# Test the functions
if __name__ == "__main__":
    print("hi")
    # Test PubMed Search
    query = 'cancer immunotherapy'
    paper_ids = search_pubmed(query)
    print(f"PubMed Paper IDs: {paper_ids}")
    
    # Test PubMed Details Fetch
    print(get_pubmed_details(paper_ids))

    # Test Clinical Trials Search
    trials = search_clinical_trials(query)
    for trial in trials:
        print(f"Trial ID: {trial['NCTId'][0]}, Title: {trial['Title'][0]}")
    
    # Test MeSH Related Terms Fetch
    term = 'cancer'
    related_terms = get_related_terms(term)
    print(f"Related terms for 'cancer': {related_terms}")
