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
        'breaches': check_breaches(email),
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

def check_breaches(email):
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
            return {'found': False, 'count': 0, 'message': 'No breaches found'}
        else:
            return {'error': f'API returned status {response.status_code}'}
    except Exception as e:
        return {'error': f'Connection failed: {str(e)}'}

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
    """Check Pastebin and paste dump sites for email mentions"""
    results = {
        'pastebin_search': f'https://psbdmp.ws/api/search/{email}',
        'found_pastes': [],
        'total_found': 0
    }
    
    try:
        # Psbdmp.ws - Free pastebin dump search
        response = requests.get(f'https://psbdmp.ws/api/search/{email}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and 'data' in data:
                pastes = data['data'][:5]  # Get first 5 results
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
    """Check for dark web and leaked database mentions"""
    results = {
        'intelligence_x_url': f'https://intelx.io/?s={email}',
        'search_engines': [
            {
                'name': 'Intelligence X',
                'url': f'https://intelx.io/?s={email}',
                'description': 'Dark web search engine'
            },
            {
                'name': 'DarkSearch',
                'url': f'https://darksearch.io/?query={email}',
                'description': 'Tor search engine'
            },
            {
                'name': 'Ahmia',
                'url': f'https://ahmia.fi/search/?q={email}',
                'description': 'Tor hidden services search'
            }
        ],
        'leak_databases': [
            {
                'name': 'DeHashed (Paid)',
                'url': 'https://dehashed.com',
                'note': 'Comprehensive breach database ($4.99/month)'
            },
            {
                'name': 'LeakCheck',
                'url': f'https://leakcheck.io/search?query={email}',
                'note': 'Free basic search available'
            }
        ],
        'note': 'These searches require manual verification. Dark web results may take time to appear.'
    }
    
    return results

def verify_profile_exists(platform_name, url, username):
    """Check if a profile actually exists on a platform"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        
        if platform_name == 'GitHub':
            exists = response.status_code == 200 and 'Not Found' not in response.text
        elif platform_name == 'Reddit':
            exists = response.status_code == 200 and f'/user/{username}' in response.text
        elif platform_name == 'Medium':
            exists = response.status_code == 200 and username.lower() in response.text.lower()
        elif platform_name in ['Instagram', 'Twitter/X', 'TikTok', 'LinkedIn']:
            exists = None  # These block automated requests
        else:
            exists = response.status_code == 200
            
        return {
            'name': platform_name,
            'url': url,
            'exists': exists,
            'status': 'found' if exists else ('not_found' if exists == False else 'check_manually')
        }
    except:
        return {
            'name': platform_name,
            'url': url,
            'exists': None,
            'status': 'error'
        }

def check_social_media_verified(username):
    """Check social media accounts with automatic verification"""
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
        futures = {
            executor.submit(verify_profile_exists, p['name'], p['url'], username): p 
            for p in platforms
        }
        
        for future in as_completed(futures):
            result = future.result()
            verified_platforms.append(result)
    
    found_count = sum(1 for p in verified_platforms if p['exists'] == True)
    manual_check = [p for p in verified_platforms if p['exists'] is None]
    
    return {
        'platforms_checked': len(platforms),
        'verified_found': found_count,
        'manual_check_required': len(manual_check),
        'platforms': sorted(verified_platforms, key=lambda x: (x['status'] != 'found', x['name']))
    }

def check_username_sites_verified(username):
    """Verify username across multiple sites"""
    sites = [
        {'name': 'Stack Overflow', 'url': f'https://stackoverflow.com/users/{username}'},
        {'name': 'Keybase', 'url': f'https://keybase.io/{username}'},
        {'name': 'Tumblr', 'url': f'https://{username}.tumblr.com'},
        {'name': 'Pinterest', 'url': f'https://pinterest.com/{username}'},
        {'name': 'Twitch', 'url': f'https://twitch.tv/{username}'},
    ]
    
    verified_sites = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(verify_profile_exists, s['name'], s['url'], username): s 
            for s in sites
        }
        
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
            potential_names.append({
                'type': 'firstname.lastname',
                'first': parts[0].capitalize(),
                'last': parts[1].capitalize()
            })
    
    if '_' in username:
        parts = username.split('_')
        if len(parts) == 2:
            potential_names.append({
                'type': 'first_last',
                'first': parts[0].capitalize(),
                'last': parts[1].capitalize()
            })
    
    numbers = re.findall(r'\d+', username)
    if numbers:
        potential_names.append({
            'type': 'username_with_numbers',
            'username_base': re.sub(r'\d+', '', username),
            'numbers': numbers,
            'note': 'Numbers might be birth year, age, or significant dates'
        })
    
    return potential_names if potential_names else [{'note': 'No obvious name patterns detected'}]

def generate_google_dorks(email):
    dorks = [
        f'"{email}"',
        f'"{email}" site:pastebin.com',
        f'"{email}" site:linkedin.com',
        f'"{email}" site:twitter.com',
        f'"{email}" filetype:pdf',
        f'"{email}" "password" OR "leaked"',
        f'"{email}" site:github.com',
        f'intext:"{email}" site:facebook.com',
        f'"{email}" inurl:admin',
        f'"{email}" site:archive.org',
        f'"{email}" site:reddit.com',
        f'"{email}" "database" OR "dump"'
    ]
    
    return {
        'dorks': dorks,
        'google_search_url': f'https://www.google.com/search?q={email}',
        'note': 'Copy these dorks into Google for deep searches'
    }
