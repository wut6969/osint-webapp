import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.google_search import generate_google_dorks_with_preview
from app.result_verifier import verify_public_records, verify_multiple_sources, get_status_icon, get_status_text
from app.username_checker import check_username_probability

def investigate_name(first_name, last_name, email=None):
    full_name = f"{first_name} {last_name}"
    
    results = {
        'full_name': full_name,
        'first_name': first_name,
        'last_name': last_name,
        'potential_emails': generate_email_patterns(first_name, last_name),
        'potential_phones': generate_phone_patterns(first_name, last_name),
        'social_media': search_social_by_name(first_name, last_name),
        'professional': search_professional_sites(first_name, last_name),
        'dark_web': search_dark_web_by_name(full_name, email),
        'paste_sites': search_pastes_by_name(full_name),
        'public_records': generate_public_record_links(full_name),
        'legal_records': search_legal_records(full_name),
        'business_records': search_business_records(full_name),
        'crypto_wallets': search_crypto_addresses(full_name, email),
        'archives': search_archives(full_name),
        'google_dorks': generate_name_dorks(full_name),
        'username_variations': generate_username_variations(first_name, last_name)
    }
    
    if email:
        results['email_match'] = check_name_email_match(first_name, last_name, email)
    
    return results

def generate_email_patterns(first, last):
    first_lower = first.lower()
    last_lower = last.lower()
    first_initial = first_lower[0]
    last_initial = last_lower[0]
    
    patterns = [
        f"{first_lower}.{last_lower}",
        f"{first_lower}{last_lower}",
        f"{first_initial}{last_lower}",
        f"{first_lower}{last_initial}",
        f"{first_lower}_{last_lower}",
        f"{last_lower}.{first_lower}",
        f"{first_lower}-{last_lower}"
    ]
    
    common_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com', 'icloud.com', 'protonmail.com', 'aol.com']
    
    email_patterns = []
    for pattern in patterns[:5]:
        for domain in common_domains[:4]:
            email_patterns.append(f"{pattern}@{domain}")
    
    return {
        'patterns': email_patterns,
        'note': 'Potential email addresses based on common patterns'
    }

def generate_phone_patterns(first, last):
    full_name = f"{first} {last}"
    
    return {
        'search_links': [
            {'name': 'TrueCaller', 'url': f'https://www.truecaller.com/search/us/{full_name.replace(" ", "%20")}', 'description': 'Phone number lookup'},
            {'name': 'WhitePages Phone', 'url': f'https://www.whitepages.com/name/{full_name.replace(" ", "-")}', 'description': 'Phone and address search'}
        ],
        'note': 'Search these sites to find phone numbers'
    }

def search_social_by_name(first, last):
    full_name = f"{first} {last}"
    full_name_nospace = f"{first}{last}"
    
    platforms = [
        {'name': 'LinkedIn', 'url': f'https://www.linkedin.com/search/results/people/?keywords={first}%20{last}', 'description': 'Professional network'},
        {'name': 'Facebook', 'url': f'https://www.facebook.com/search/people/?q={first}%20{last}', 'description': 'Social network'},
        {'name': 'Twitter/X', 'url': f'https://twitter.com/search?q={first}%20{last}&f=user', 'description': 'Microblogging'},
        {'name': 'Instagram', 'url': f'https://www.instagram.com/explore/tags/{full_name_nospace}/', 'description': 'Photo sharing'},
        {'name': 'TikTok', 'url': f'https://www.tiktok.com/search/user?q={first}%20{last}', 'description': 'Video platform'},
        {'name': 'Snapchat', 'url': f'https://story.snapchat.com/search?q={first}%20{last}', 'description': 'Messaging app'}
    ]
    
    return {'platforms': platforms, 'note': 'Manual verification required'}

def search_professional_sites(first, last):
    full_name = f"{first} {last}"
    
    sites = [
        {'name': 'GitHub', 'url': f'https://github.com/search?q={first}+{last}&type=users', 'type': 'Developer platform'},
        {'name': 'Stack Overflow', 'url': f'https://stackoverflow.com/users?tab=Users&search={first}%20{last}', 'type': 'Q&A'},
        {'name': 'Medium', 'url': f'https://medium.com/search?q={first}%20{last}', 'type': 'Blogging'},
        {'name': 'Behance', 'url': f'https://www.behance.net/search/users?search={first}%20{last}', 'type': 'Creative portfolios'},
        {'name': 'AngelList', 'url': f'https://angel.co/search?q={first}%20{last}', 'type': 'Startup community'},
        {'name': 'ResearchGate', 'url': f'https://www.researchgate.net/search/researcher?q={first}%20{last}', 'type': 'Academic research'}
    ]
    
    return sites

def search_dark_web_by_name(full_name, email=None):
    search_query = full_name if not email else f"{full_name} {email}"
    
    return {
        'search_engines': [
            {'name': 'Intelligence X', 'url': f'https://intelx.io/?s={full_name.replace(" ", "+")}', 'description': 'Dark web search'},
            {'name': 'DarkSearch', 'url': f'https://darksearch.io/?query={full_name.replace(" ", "+")}', 'description': 'Tor search'},
            {'name': 'Ahmia', 'url': f'https://ahmia.fi/search/?q={full_name.replace(" ", "+")}', 'description': 'Hidden services'}
        ],
        'leak_databases': [
            {'name': 'DeHashed', 'url': f'https://dehashed.com/search?query={search_query.replace(" ", "+")}', 'note': '$4.99/month'},
            {'name': 'LeakCheck', 'url': f'https://leakcheck.io/search?query={full_name.replace(" ", "+")}', 'note': 'Free basic'},
            {'name': 'SnusBase', 'url': 'https://snusbase.com', 'note': 'Paid'}
        ],
        'note': 'Manual verification required'
    }

def search_pastes_by_name(full_name):
    return {
        'search_links': [
            {'name': 'Psbdmp', 'url': f'https://psbdmp.ws/?q={full_name.replace(" ", "+")}', 'description': 'Pastebin dump search'},
            {'name': 'Pastebin Search', 'url': f'https://www.google.com/search?q=site:pastebin.com+"{full_name}"', 'description': 'Google search'},
            {'name': 'Ghostbin', 'url': f'https://www.google.com/search?q=site:ghostbin.com+"{full_name}"', 'description': 'Alt paste site'}
        ],
        'note': 'Check for data leaks'
    }

def generate_public_record_links(full_name):
    encoded_name = full_name.replace(' ', '+')
    
    databases = [
        {'name': 'Whitepages', 'url': f'https://www.whitepages.com/name/{full_name.replace(" ", "-")}', 'description': 'Phone & addresses'},
        {'name': 'TruePeopleSearch', 'url': f'https://www.truepeoplesearch.com/results?name={encoded_name}', 'description': 'Free people search'},
        {'name': 'FastPeopleSearch', 'url': f'https://www.fastpeoplesearch.com/name/{full_name.replace(" ", "-")}', 'description': 'Public records'},
        {'name': 'Spokeo', 'url': f'https://www.spokeo.com/{full_name.replace(" ", "-")}', 'description': 'Premium search'},
        {'name': 'BeenVerified', 'url': f'https://www.beenverified.com/people/{full_name.replace(" ", "-")}', 'description': 'Background check'},
        {'name': 'Instant Checkmate', 'url': f'https://www.instantcheckmate.com/?firstName={full_name.split()[0]}&lastName={full_name.split()[1]}', 'description': 'Criminal records'}
    ]
    
    verified_databases = verify_public_records(full_name, databases)
    
    return {
        'databases': verified_databases,
        'warning': 'Some services require payment',
        'verified_count': len([d for d in verified_databases if d.get('verification_status') == 'found'])
    }

def search_legal_records(full_name):
    return {
        'court_records': [
            {'name': 'PACER', 'url': 'https://pacer.uscourts.gov/', 'description': 'Federal courts (requires account)'},
            {'name': 'UniCourt', 'url': f'https://unicourt.com/search?q={full_name.replace(" ", "+")}', 'description': 'Legal case search'},
            {'name': 'CourtListener', 'url': f'https://www.courtlistener.com/?q={full_name.replace(" ", "+")}', 'description': 'Free legal opinions'}
        ],
        'property_records': [
            {'name': 'Zillow', 'url': f'https://www.zillow.com/homes/{full_name.replace(" ", "-")}_rb/', 'description': 'Property ownership'},
            {'name': 'PropertyShark', 'url': f'https://www.propertyshark.com/mason/Search/Search?search={full_name.replace(" ", "+")}', 'description': 'Real estate records'}
        ],
        'note': 'Federal records require PACER account'
    }

def search_business_records(full_name):
    return {
        'business_searches': [
            {'name': 'OpenCorporates', 'url': f'https://opencorporates.com/officers?q={full_name.replace(" ", "+")}', 'description': 'Corporate officer search'},
            {'name': 'Secretary of State', 'url': 'https://www.nass.org/business-services/corporate-registration', 'description': 'State registrations'},
            {'name': 'BBB', 'url': f'https://www.bbb.org/search?find_text={full_name.replace(" ", "+")}', 'description': 'Business complaints'}
        ],
        'professional_licenses': [
            {'name': 'License Lookup', 'url': f'https://www.google.com/search?q="{full_name}"+professional+license', 'description': 'Licensing boards'},
            {'name': 'USPTO Patent', 'url': f'https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&f=S&l=50&d=PTXT&Query=IN/{full_name.split()[0]}+AND+IN/{full_name.split()[1]}', 'description': 'Patent search'},
            {'name': 'Trademark', 'url': 'https://www.uspto.gov/trademarks/search', 'description': 'USPTO'}
        ]
    }

def search_crypto_addresses(full_name, email=None):
    search_term = email if email else full_name
    
    return {
        'blockchain_searches': [
            {'name': 'Bitcoin Who\'s Who', 'url': f'https://bitcoinwhoswho.com/search/?q={search_term.replace(" ", "+")}', 'description': 'Bitcoin scam database'},
            {'name': 'Wallet Explorer', 'url': 'https://www.walletexplorer.com/', 'description': 'Bitcoin clustering'},
            {'name': 'Etherscan', 'url': f'https://etherscan.io/searchHandler?term={search_term.replace(" ", "+")}', 'description': 'Ethereum blockchain'}
        ],
        'note': 'Works best with wallet addresses or email'
    }

def search_archives(full_name):
    return {
        'archive_sites': [
            {'name': 'Wayback Machine', 'url': f'https://web.archive.org/web/*/{full_name.replace(" ", "")}', 'description': 'Archived websites'},
            {'name': 'Archive.today', 'url': f'https://archive.ph/{full_name.replace(" ", "+")}', 'description': 'Recent archives'},
            {'name': 'Google Cache', 'url': f'https://www.google.com/search?q=cache:"{full_name}"', 'description': 'Cached pages'}
        ],
        'note': 'Useful for deleted profiles'
    }

def generate_name_dorks(full_name):
    return generate_google_dorks_with_preview(full_name, is_email=False)

def generate_username_variations(first, last):
    first_lower = first.lower()
    last_lower = last.lower()
    first_initial = first_lower[0]
    last_initial = last_lower[0]
    
    variations = [
        f"{first_lower}{last_lower}",
        f"{first_lower} {last_lower}",
        f"{first_lower}.{last_lower}",
        f"{first_lower}_{last_lower}",
        f"{first_lower}-{last_lower}",
        f"{last_lower}{first_lower}",
        f"{last_lower}.{first_lower}",
        f"{last_lower}_{first_lower}",
        f"{first_initial}{last_lower}",
        f"{first_lower}{last_initial}",
        f"{first_initial}.{last_lower}",
        f"{first_initial}_{last_lower}",
        f"{last_lower}{first_initial}",
        f"{first_lower}{last_lower}1",
        f"{first_lower}{last_lower}123",
        f"{first_lower}.{last_lower}1",
        f"{first_lower}_{last_lower}1",
        f"{first_lower}{last_lower}99",
        f"{first_lower}{last_lower}00",
        f"{first_lower.capitalize()}{last_lower.capitalize()}",
    ]
    
    seen = set()
    unique = []
    for v in variations:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    
    return unique[:15]

def check_name_email_match(first, last, email):
    first_lower = first.lower()
    last_lower = last.lower()
    email_lower = email.lower().split('@')[0]
    
    matches = []
    
    if first_lower in email_lower:
        matches.append(f"First name '{first}' found in email")
    if last_lower in email_lower:
        matches.append(f"Last name '{last}' found in email")
    if f"{first_lower}.{last_lower}" == email_lower or f"{first_lower}{last_lower}" == email_lower:
        matches.append("Email follows common name pattern")
    
    return {
        'matches_found': len(matches) > 0,
        'details': matches if matches else ['No obvious pattern match'],
        'confidence': 'High' if len(matches) >= 2 else 'Medium' if len(matches) == 1 else 'Low'
    }

def investigate_username_deep(username):
    return check_username_probability(username)
