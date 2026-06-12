from scholarly import scholarly, ProxyGenerator
import json
from datetime import datetime
import os
from scholarly._proxy_generator import MaxTriesExceededException

try:
    print("Fetching author information...")
    
    # 1. Attempt to set up free proxies safely
    pg = ProxyGenerator()
    try:
        print("Attempting to fetch free proxies...")
        pg.FreeProxies()
        scholarly.use_proxy(pg)
        print("Proxies configured successfully.")
    except Exception as proxy_error:
        # Catches the StopIteration and any other scraping failures
        print(f"Warning: Failed to fetch free proxies ({proxy_error}).")
        print("Falling back to a direct, unproxied connection...")
    
    # 2. Fetch author by Google Scholar ID
    # Using .get() prevents a fatal KeyError if the secret isn't loaded correctly
    scholar_id = os.environ.get('GOOGLE_SCHOLAR_ID')
    if not scholar_id:
         raise ValueError("GOOGLE_SCHOLAR_ID environment variable is missing!")
         
    author: dict = scholarly.search_author_id(scholar_id)

except MaxTriesExceededException as e:
    print(f"Google Scholar blocked the request (MaxTriesExceeded): {e}")
except Exception as e:
    print(f"A general error occurred: {e}")
else:
    print("Filling author details...")
    scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
    name = author['name']
    author['updated'] = str(datetime.now())
    author['publications'] = {v['author_pub_id']:v for v in author['publications']}
    print(json.dumps(author, indent=2))
    os.makedirs('results', exist_ok=True)

    print("Saving author data...")
    with open('results/gs_data.json', 'w') as outfile:
        json.dump(author, outfile, ensure_ascii=False)

    print("Generating Shields.io data...")
    shieldio_data = {
        "schemaVersion": 1,
        "label": "citations",
        "message": str(author.get('citedby', 0)),
    }

    print("Saving Shields.io data...")
    with open('results/gs_data_shieldsio.json', 'w') as outfile:
        json.dump(shieldio_data, outfile, ensure_ascii=False)