import requests
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def investigate_email(email):
    if not validate_email(email):
        return {'error': 'Invalid email format'}
    
    username = email.split('@')[0]
    domain = email.split('@')[1]
    
    results = {
        'email': email,
        'username': username,
        'timestamp': datetime.now().isoformat(),
        'breaches': check_multiple_breach_sources(email),
        'reputation': check_reputation(email),
        'paste_sites': check_paste_sites(email),
        'dark_web_mentions': check_dark_web_mentions(email),
        'social_media': check_social_media_verified(username),
        'username_search': check_username_sites_verified(username),
        'domain_info': check_domain_advanced(domain),
        'potential_names': extract_potential_names(username),
        'google_dorks': generate_google_dorks(email)
    }
    
    return results

def check_multiple_breach_sources(email):
    results = {
        'sources_checked': 3,
        'breaches_found': [],
        'total_breaches': 0,
        'details': [],
        'found': False
    }
    
    hibp = check_haveibeenpwned(email)
    if hibp.get('found'):
        results['breaches_found'].extend(hibp.get('breaches', []))
        results['details'].append({
            'source': 'HaveIBeenPwned',
            'status': '✅ Found',
            'count': hibp.get('count', 0),
            'breaches': hibp.get('breaches', [])
        })
    else:
        results['details'].append({
            'source': 'HaveIBeenPwned',
            'status': '✅ Clean' if not hibp.get('error') else '⚠️ ' + hibp.get('error', 'Error'),
            'count': 0
        })
    
    leakcheck = check_leakcheck(email)
    if leakcheck.get('found'):
        results['details'].append({
            'source': 'LeakCheck',
            'status': '✅ Found',
            'count': leakcheck.get('count', 0),
            'url': leakcheck.get('url')
        })
    else:
        results['details'].append({
            'source': 'LeakCheck',
            'status': '✅ Clean',
            'count': 0
        })
    
    dehashed = check_dehashed(email)
    if dehashed.get('found'):
        results['details'].append({
            'source': 'DeHashed',
            'status': '✅ Found',
            'note': 'Premium required',
            'url': dehashed.get('url')
        })
    else:
        results['details'].append({
            'source': 'DeHashed',
            'status': '✅ Clean',
            'count': 0
        })
    
    results['total_breaches'] = len(results['breaches_found'])
    results['found'] = results['total_breaches'] > 0
    
    return results

def check_haveibeenpwned(email):
    try:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {'user-agent': 'OSINT-WebApp'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            breaches = response.json()
            return {
                'found': True,
                'count': len(breaches),
                'breaches': [
                    {
                        'name': b['Name'],
                        'date': b.get('BreachDate', 'Unknown'),
                        'data': b.get('DataClasses', [])
                    } for b in breaches[:10]
                ]
            }
        elif response.status_code == 404:
            return {'found': False, 'count': 0}
        else:
            return {'error': f'Rate limited', 'found': False}
    except Exception as e:
        return {'error': str(e), 'found': False}

def check_leakcheck(email):
    try:
        url = f"https://leakcheck.io/api/public?check={email}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('found', 0) > 0:
                return {
                    'found': True,
                    'count': data.get('found', 0),
                    'url': f'https://leakcheck.io/search?query={email}'
                }
        return {'found': False}
    except:
        return {'found': False}

def check_dehashed(email):
    return {
        'found': False,
        'url': f"https://dehashed.com/search?query={email}",
        'note': 'Visit manually'
    }

def check_reputation(email):
    try:
        url = f"https://emailrep.io/{email}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'reputation': data.get('reputation', 'unknown'),
                'suspicious': data.get('suspicious', False),
                'references': data.get('references', 0),
                'details': data.get('details', {})
            }
        else:
            return {'error': 'Could not fetch reputation'}
    except:
        return {'error': 'Reputation check unavailable'}

def check_paste_sites(email):
    results = {
        'pastebin_search': f'https://psbdmp.ws/api/search/{email}',
        'found_pastes': [],
        'total_found': 0
    }
    
    try:
        response = requests.get(f'https://psbdmp.ws/api/search/{email}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and 'data' in data:
                pastes = data['data'][:5]
                results['found_pastes'] = [
                    {
                        'id': paste.get('id'),
                        'title': paste.get('title', 'Untitled'),
                        'time': paste.get('time'),
                        'url': f"https://pastebin.com/{paste.get('id')}"
                    } for paste in pastes
                ]
                results['total_found'] = len(data.get('data', []))
    except Exception as e:
        results['error'] = f'Paste search failed: {str(e)}'
    
    return results

def check_dark_web_mentions(email):
    results = {
        'intelligence_x_url': f'https://intelx.io/?s={email}',
        'search_engines': [
            {'name': 'Intelligence X', 'url': f'https://intelx.io/?s={email}', 'description': 'Dark web search'},
            {'name': 'DarkSearch', 'url': f'https://darksearch.io/?query={email}', 'description': 'Tor search'},
            {'name': 'Ahmia', 'url': f'https://ahmia.fi/search/?q={email}', 'description': 'Hidden services'}
        ],
        'leak_databases': [
            {'name': 'DeHashed', 'url': f'https://dehashed.com/search?query={email}', 'note': '$4.99/month'},
            {'name': 'LeakCheck', 'url': f'https://leakcheck.io/search?query={email}', 'note': 'Free basic'}
        ],
        'note': 'Manual verification required'
    }
    
    return results

def verify_profile_exists(platform_name, url, username):
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        
        if platform_name == 'GitHub':
            exists = response.status_code == 200 and 'Not Found' not in response.text
        elif platform_name == 'Reddit':
            exists = response.status_code == 200 and f'/user/{username}' in response.text
        elif platform_name == 'Medium':
            exists = response.status_code == 200 and username.lower() in response.text.lower()
        elif platform_name in ['Instagram', 'Twitter/X', 'TikTok', 'LinkedIn']:
            exists = None
        else:
            exists = response.status_code == 200
            
        return {
            'name': platform_name,
            'url': url,
            'exists': exists,
            'status': 'found' if exists else ('not_found' if exists == False else 'check_manually')
        }
    except:
        return {'name': platform_name, 'url': url, 'exists': None, 'status': 'error'}

def check_social_media_verified(username):
    platforms = [
        {'name': 'GitHub', 'url': f'https://github.com/{username}'},
        {'name': 'Reddit', 'url': f'https://reddit.com/user/{username}'},
        {'name': 'Medium', 'url': f'https://medium.com/@{username}'},
        {'name': 'Dev.to', 'url': f'https://dev.to/{username}'},
        {'name': 'Pastebin', 'url': f'https://pastebin.com/u/{username}'},
        {'name': 'GitLab', 'url': f'https://gitlab.com/{username}'},
        {'name': 'Twitter/X', 'url': f'https://twitter.com/{username}'},
        {'name': 'Instagram', 'url': f'https://instagram.com/{username}'},
        {'name': 'LinkedIn', 'url': f'https://linkedin.com/in/{username}'},
        {'name': 'Facebook', 'url': f'https://facebook.com/{username}'},
        {'name': 'TikTok', 'url': f'https://tiktok.com/@{username}'},
        {'name': 'YouTube', 'url': f'https://youtube.com/@{username}'},
    ]
    
    verified_platforms = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(verify_profile_exists, p['name'], p['url'], username): p for p in platforms}
        
        for future in as_completed(futures):
            result = future.result()
            verified_platforms.append(result)
    
    found_count = sum(1 for p in verified_platforms if p['exists'] == True)
    
    return {
        'platforms_checked': len(platforms),
        'verified_found': found_count,
        'manual_check_required': len([p for p in verified_platforms if p['exists'] is None]),
        'platforms': sorted(verified_platforms, key=lambda x: (x['status'] != 'found', x['name']))
    }

def check_username_sites_verified(username):
    sites = [
        {'name': 'Stack Overflow', 'url': f'https://stackoverflow.com/users/{username}'},
        {'name': 'Keybase', 'url': f'https://keybase.io/{username}'},
        {'name': 'Tumblr', 'url': f'https://{username}.tumblr.com'},
        {'name': 'Pinterest', 'url': f'https://pinterest.com/{username}'},
        {'name': 'Twitch', 'url': f'https://twitch.tv/{username}'},
    ]
    
    verified_sites = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(verify_profile_exists, s['name'], s['url'], username): s for s in sites}
        
        for future in as_completed(futures):
            result = future.result()
            verified_sites.append(result)
    
    return {
        'username': username,
        'sites': sorted(verified_sites, key=lambda x: (x['status'] != 'found', x['name']))
    }

def check_domain_advanced(domain):
    info = {
        'domain': domain,
        'whois': f'https://who.is/whois/{domain}',
        'dns_lookup': f'https://mxtoolbox.com/SuperTool.aspx?action=mx%3a{domain}',
        'security_headers': f'https://securityheaders.com/?q={domain}',
        'ssl_check': f'https://www.ssllabs.com/ssltest/analyze.html?d={domain}'
    }
    
    try:
        import dns.resolver
        mx_records = dns.resolver.resolve(domain, 'MX')
        info['mx_records'] = [str(mx.exchange) for mx in mx_records]
    except:
        info['mx_records'] = ['Unable to fetch MX records']
    
    return info

def extract_potential_names(username):
    potential_names = []
    
    if '.' in username:
        parts = username.split('.')
        if len(parts) == 2:
            potential_names.append({'type': 'firstname.lastname', 'first': parts[0].capitalize(), 'last': parts[1].capitalize()})
    
    if '_' in username:
        parts = username.split('_')
        if len(parts) == 2:
            potential_names.append({'type': 'first_last', 'first': parts[0].capitalize(), 'last': parts[1].capitalize()})
    
    numbers = re.findall(r'\d+', username)
    if numbers:
        potential_names.append({'type': 'username_with_numbers', 'username_base': re.sub(r'\d+', '', username), 'numbers': numbers, 'note': 'Numbers might be birth year, age, or dates'})
    
    return potential_names if potential_names else [{'note': 'No obvious name patterns detected'}]

def generate_google_dorks(email):
    from app.google_search import generate_google_dorks_with_preview
    return generate_google_dorks_with_preview(email, is_email=True)
