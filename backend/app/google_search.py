import requests
from bs4 import BeautifulSoup
import time

def fetch_google_results(query, num_results=5):
    """Fetch actual Google search results"""
    results = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = f"https://www.google.com/search?q={query}&num={num_results}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for g in soup.find_all('div', class_='g')[:num_results]:
                try:
                    title_elem = g.find('h3')
                    title = title_elem.text if title_elem else 'No title'
                    
                    link_elem = g.find('a')
                    link = link_elem.get('href') if link_elem else '#'
                    
                    snippet_elem = g.find('div', class_='VwiC3b')
                    snippet = snippet_elem.text if snippet_elem else 'No description'
                    
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet[:200] + '...' if len(snippet) > 200 else snippet
                    })
                except:
                    continue
        
        time.sleep(0.5)
        
    except Exception as e:
        results.append({
            'title': 'Search unavailable',
            'url': f"https://www.google.com/search?q={query}",
            'snippet': 'Click to search manually'
        })
    
    return results

def generate_google_dorks_with_preview(email_or_name, is_email=True):
    """Generate dorks with UK/EU focus and preview results"""
    
    if is_email:
        dorks = [
            {
                'query': f'"{email_or_name}" site:.uk',
                'description': 'UK domains',
                'priority': 'high',
                'region': 'UK'
            },
            {
                'query': f'"{email_or_name}" site:.eu',
                'description': 'EU domains',
                'priority': 'high',
                'region': 'EU'
            },
            {
                'query': f'"{email_or_name}" site:companies-house.gov.uk',
                'description': 'UK Companies House',
                'priority': 'high',
                'region': 'UK'
            },
            {
                'query': f'"{email_or_name}" site:linkedin.com/in',
                'description': 'LinkedIn profiles',
                'priority': 'high',
                'region': 'Global'
            },
            {
                'query': f'"{email_or_name}" "password" OR "leaked"',
                'description': 'Potential leaks',
                'priority': 'high',
                'region': 'Global'
            },
            {
                'query': f'"{email_or_name}" site:github.com',
                'description': 'GitHub profiles',
                'priority': 'medium',
                'region': 'Global'
            },
            {
                'query': f'"{email_or_name}" site:pastebin.com',
                'description': 'Pastebin mentions',
                'priority': 'medium',
                'region': 'Global'
            },
            {
                'query': f'"{email_or_name}" filetype:pdf',
                'description': 'PDF documents',
                'priority': 'medium',
                'region': 'Global'
            },
            {
                'query': f'"{email_or_name}" site:.com',
                'description': 'US/.com domains (lower priority)',
                'priority': 'low',
                'region': 'US'
            }
        ]
    else:
        dorks = [
            {
                'query': f'"{email_or_name}" site:.uk',
                'description': 'UK websites',
                'priority': 'high',
                'region': 'UK'
            },
            {
                'query': f'"{email_or_name}" site:companies-house.gov.uk',
                'description': 'UK company directors',
                'priority': 'high',
                'region': 'UK'
            },
            {
                'query': f'"{email_or_name}" site:192.com',
                'description': 'UK people search',
                'priority': 'high',
                'region': 'UK'
            },
            {
                'query': f'"{email_or_name}" site:.eu',
                'description': 'European sites',
                'priority': 'high',
                'region': 'EU'
            },
            {
                'query': f'"{email_or_name}" United Kingdom OR UK',
                'description': 'UK references',
                'priority': 'high',
                'region': 'UK'
            },
            {
                'query': f'"{email_or_name}" site:linkedin.com/in UK OR London',
                'description': 'UK LinkedIn profiles',
                'priority': 'high',
                'region': 'UK'
            },
            {
                'query': f'"{email_or_name}" Europe OR European',
                'description': 'European mentions',
                'priority': 'medium',
                'region': 'EU'
            },
            {
                'query': f'"{email_or_name}" resume OR CV filetype:pdf',
                'description': 'CVs/Resumes',
                'priority': 'medium',
                'region': 'Global'
            },
            {
                'query': f'"{email_or_name}" site:.com',
                'description': 'US domains (lower priority)',
                'priority': 'low',
                'region': 'US'
            }
        ]
    
    # Fetch preview for top 3 high-priority dorks
    high_priority = [d for d in dorks if d['priority'] == 'high'][:3]
    
    for dork in high_priority:
        dork['preview_results'] = fetch_google_results(dork['query'], num_results=3)
    
    return {
        'dorks': dorks,
        'google_search_url': f'https://www.google.com/search?q={email_or_name}',
        'note': 'Prioritized for UK/Europe with live preview results',
        'regions': {
            'uk_eu_count': len([d for d in dorks if d['region'] in ['UK', 'EU']]),
            'us_count': len([d for d in dorks if d['region'] == 'US'])
        }
    }
