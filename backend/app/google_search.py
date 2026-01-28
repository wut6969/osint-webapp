import requests
import re

def get_google_result_count(query):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f'https://www.google.com/search?q={query}'
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            match = re.search(r'About ([\d,]+) results', response.text)
            if match:
                return match.group(1)
            
            if 'did not match' in response.text.lower():
                return '0'
            
            return '~Unknown'
        return '~Unknown'
    except:
        return '~Unknown'

def generate_google_dorks_with_preview(email_or_name, is_email=True):
    if is_email:
        dorks = [
            {'query': f'"{email_or_name}" site:.uk', 'description': 'UK domains', 'priority': 'high', 'region': 'UK'},
            {'query': f'"{email_or_name}" site:.eu', 'description': 'EU domains', 'priority': 'high', 'region': 'EU'},
            {'query': f'"{email_or_name}" site:companies-house.gov.uk', 'description': 'UK Companies House', 'priority': 'high', 'region': 'UK'},
            {'query': f'"{email_or_name}" site:linkedin.com', 'description': 'LinkedIn', 'priority': 'high', 'region': 'Global'},
            {'query': f'"{email_or_name}" "password" OR "leaked"', 'description': 'Leaks', 'priority': 'high', 'region': 'Global'},
            {'query': f'"{email_or_name}" site:github.com', 'description': 'GitHub', 'priority': 'medium', 'region': 'Global'},
            {'query': f'"{email_or_name}" site:pastebin.com', 'description': 'Pastebin', 'priority': 'medium', 'region': 'Global'},
            {'query': f'"{email_or_name}" filetype:pdf', 'description': 'PDFs', 'priority': 'medium', 'region': 'Global'},
            {'query': f'"{email_or_name}" site:.com', 'description': 'US domains', 'priority': 'low', 'region': 'US'}
        ]
    else:
        dorks = [
            {'query': f'"{email_or_name}" site:.uk', 'description': 'UK sites', 'priority': 'high', 'region': 'UK'},
            {'query': f'"{email_or_name}" site:companies-house.gov.uk', 'description': 'UK Companies', 'priority': 'high', 'region': 'UK'},
            {'query': f'"{email_or_name}" site:192.com', 'description': 'UK people', 'priority': 'high', 'region': 'UK'},
            {'query': f'"{email_or_name}" site:.eu', 'description': 'EU sites', 'priority': 'high', 'region': 'EU'},
            {'query': f'"{email_or_name}" United Kingdom', 'description': 'UK refs', 'priority': 'high', 'region': 'UK'},
            {'query': f'"{email_or_name}" site:linkedin.com UK', 'description': 'UK LinkedIn', 'priority': 'high', 'region': 'UK'},
            {'query': f'"{email_or_name}" Europe', 'description': 'EU mentions', 'priority': 'medium', 'region': 'EU'},
            {'query': f'"{email_or_name}" CV filetype:pdf', 'description': 'CVs', 'priority': 'medium', 'region': 'Global'},
            {'query': f'"{email_or_name}" site:.com', 'description': 'US domains', 'priority': 'low', 'region': 'US'}
        ]
    
    for dork in dorks[:3]:
        dork['result_count'] = get_google_result_count(dork['query'])
    
    return {
        'dorks': dorks,
        'google_search_url': f'https://www.google.com/search?q={email_or_name}',
        'note': 'UK/Europe prioritized with result counts',
        'regions': {
            'uk_eu_count': len([d for d in dorks if d['region'] in ['UK', 'EU']]),
            'us_count': len([d for d in dorks if d['region'] == 'US'])
        }
    }
