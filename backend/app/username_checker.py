import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_username_probability(username):
    platforms = [
        {'name': 'GitHub', 'url': f'https://github.com/{username}', 'weight': 10},
        {'name': 'Reddit', 'url': f'https://reddit.com/user/{username}', 'weight': 10},
        {'name': 'Twitter', 'url': f'https://twitter.com/{username}', 'weight': 8},
        {'name': 'Instagram', 'url': f'https://instagram.com/{username}', 'weight': 8},
        {'name': 'Medium', 'url': f'https://medium.com/@{username}', 'weight': 7},
        {'name': 'Dev.to', 'url': f'https://dev.to/{username}', 'weight': 6},
        {'name': 'GitLab', 'url': f'https://gitlab.com/{username}', 'weight': 6},
        {'name': 'Pastebin', 'url': f'https://pastebin.com/u/{username}', 'weight': 5},
    ]
    
    results = []
    found_count = 0
    total_weight = 0
    found_weight = 0
    
    def check_platform(platform):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(platform['url'], headers=headers, timeout=5, allow_redirects=True)
            
            exists = False
            if platform['name'] == 'GitHub':
                exists = response.status_code == 200 and 'Not Found' not in response.text
            elif platform['name'] == 'Reddit':
                exists = response.status_code == 200 and f'/user/{username}' in response.text
            elif platform['name'] in ['Twitter', 'Instagram']:
                exists = None
            else:
                exists = response.status_code == 200
            
            return {
                'platform': platform['name'],
                'url': platform['url'],
                'exists': exists,
                'weight': platform['weight'],
                'status': 'found' if exists else ('not_found' if exists == False else 'check_manually')
            }
        except:
            return {
                'platform': platform['name'],
                'url': platform['url'],
                'exists': None,
                'weight': platform['weight'],
                'status': 'error'
            }
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(check_platform, p): p for p in platforms}
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            total_weight += result['weight']
            if result['exists']:
                found_count += 1
                found_weight += result['weight']
    
    probability = int((found_weight / total_weight) * 100) if total_weight > 0 else 0
    confidence = 'High' if probability >= 70 else 'Medium' if probability >= 40 else 'Low'
    
    return {
        'username': username,
        'probability': probability,
        'confidence': confidence,
        'platforms_found': found_count,
        'platforms_checked': len(platforms),
        'details': sorted(results, key=lambda x: (x['status'] != 'found', x['platform']))
    }
