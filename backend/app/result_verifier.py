import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def verify_search_result(url, search_term):
    """
    Verify if a search URL actually returns results
    Returns: 'found', 'not_found', or 'check_manually'
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        
        if response.status_code != 200:
            return 'check_manually'
        
        content_lower = response.text.lower()
        
        # Check for common "no results" indicators
        no_result_indicators = [
            'no results',
            'no matches',
            'not found',
            '0 results',
            'did not match',
            'no data found',
            'nothing found',
            'no records',
            'no entries',
            'your search did not return'
        ]
        
        for indicator in no_result_indicators:
            if indicator in content_lower:
                return 'not_found'
        
        # Check if search term appears in results
        search_lower = search_term.lower()
        if search_lower in content_lower:
            return 'found'
        
        # If we can't determine, require manual check
        return 'check_manually'
        
    except Exception as e:
        return 'error'

def verify_multiple_sources(sources_list, search_term):
    """
    Verify multiple sources concurrently
    sources_list: list of dicts with 'name' and 'url'
    Returns: updated list with 'status' field
    """
    results = []
    
    def check_source(source):
        status = verify_search_result(source['url'], search_term)
        return {**source, 'verification_status': status}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(check_source, source): source for source in sources_list[:10]}  # Limit to 10
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                time.sleep(0.3)  # Rate limiting
            except:
                source = futures[future]
                results.append({**source, 'verification_status': 'error'})
    
    return sorted(results, key=lambda x: (
        0 if x['verification_status'] == 'found' else
        1 if x['verification_status'] == 'not_found' else
        2
    ))

def verify_public_records(name, databases):
    """Verify public record databases for results"""
    search_term = name
    verified = []
    
    for db in databases[:5]:  # Check first 5
        status = verify_search_result(db['url'], search_term)
        verified.append({
            **db,
            'verification_status': status,
            'status_icon': get_status_icon(status)
        })
        time.sleep(0.5)
    
    # Add rest without verification
    for db in databases[5:]:
        verified.append({
            **db,
            'verification_status': 'not_checked',
            'status_icon': '⏳'
        })
    
    return verified

def get_status_icon(status):
    """Get emoji icon for status"""
    icons = {
        'found': '✅',
        'not_found': '❌',
        'check_manually': '🔍',
        'error': '⚠️',
        'not_checked': '⏳'
    }
    return icons.get(status, '❓')

def get_status_text(status):
    """Get human-readable status text"""
    texts = {
        'found': 'Results Found',
        'not_found': 'No Results',
        'check_manually': 'Manual Check Required',
        'error': 'Error Checking',
        'not_checked': 'Not Checked'
    }
    return texts.get(status, 'Unknown')
