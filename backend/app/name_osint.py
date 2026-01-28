import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def investigate_name(first_name, last_name, email=None):
    """Comprehensive name-based OSINT investigation"""
    
    full_name = f"{first_name} {last_name}"
    
    results = {
        'full_name': full_name,
        'first_name': first_name,
        'last_name': last_name,
        'potential_emails': generate_email_patterns(first_name, last_name),
        'social_media': search_social_by_name(first_name, last_name),
        'professional': search_professional_sites(first_name, last_name),
        'public_records': generate_public_record_links(full_name),
        'google_dorks': generate_name_dorks(full_name),
        'username_variations': generate_username_variations(first_name, last_name)
    }
    
    # If email provided, cross-reference
    if email:
        results['email_match'] = check_name_email_match(first_name, last_name, email)
    
    return results

def generate_email_patterns(first, last):
    """Generate common email patterns"""
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
    
    common_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com', 'icloud.com', 'protonmail.com']
    
    email_patterns = []
    for pattern in patterns[:5]:  # Top 5 patterns
        for domain in common_domains[:3]:  # Top 3 domains
            email_patterns.append(f"{pattern}@{domain}")
    
    return {
        'patterns': email_patterns,
        'note': 'These are potential email addresses based on common patterns'
    }

def search_social_by_name(first, last):
    """Search social media by full name"""
    full_name = f"{first} {last}"
    full_name_nospace = f"{first}{last}"
    
    platforms = [
        {
            'name': 'LinkedIn',
            'url': f'https://www.linkedin.com/search/results/people/?keywords={first}%20{last}',
            'description': 'Professional network'
        },
        {
            'name': 'Facebook',
            'url': f'https://www.facebook.com/search/people/?q={first}%20{last}',
            'description': 'Social network'
        },
        {
            'name': 'Twitter/X',
            'url': f'https://twitter.com/search?q={first}%20{last}&f=user',
            'description': 'Microblogging platform'
        },
        {
            'name': 'Instagram',
            'url': f'https://www.instagram.com/explore/tags/{full_name_nospace}/',
            'description': 'Photo sharing'
        }
    ]
    
    return {
        'platforms': platforms,
        'note': 'Manual verification required - these searches may return multiple people with the same name'
    }

def search_professional_sites(first, last):
    """Search professional and developer platforms"""
    full_name = f"{first} {last}"
    
    sites = [
        {
            'name': 'GitHub',
            'url': f'https://github.com/search?q={first}+{last}&type=users',
            'type': 'Developer platform'
        },
        {
            'name': 'Stack Overflow',
            'url': f'https://stackoverflow.com/users?tab=Users&search={first}%20{last}',
            'type': 'Q&A for developers'
        },
        {
            'name': 'Medium',
            'url': f'https://medium.com/search?q={first}%20{last}',
            'type': 'Blogging platform'
        },
        {
            'name': 'Behance',
            'url': f'https://www.behance.net/search/users?search={first}%20{last}',
            'type': 'Creative portfolios'
        }
    ]
    
    return sites

def generate_public_record_links(full_name):
    """Generate links to public record databases"""
    encoded_name = full_name.replace(' ', '+')
    
    databases = [
        {
            'name': 'Whitepages',
            'url': f'https://www.whitepages.com/name/{full_name.replace(" ", "-")}',
            'description': 'Phone numbers and addresses'
        },
        {
            'name': 'TruePeopleSearch',
            'url': f'https://www.truepeoplesearch.com/results?name={encoded_name}',
            'description': 'People search engine'
        },
        {
            'name': 'FastPeopleSearch',
            'url': f'https://www.fastpeoplesearch.com/name/{full_name.replace(" ", "-")}',
            'description': 'Public records'
        },
        {
            'name': 'Spokeo',
            'url': f'https://www.spokeo.com/{full_name.replace(" ", "-")}',
            'description': 'People search (premium)'
        }
    ]
    
    return {
        'databases': databases,
        'warning': 'Some services require payment for full results'
    }

def generate_name_dorks(full_name):
    """Generate Google dork queries for name searches"""
    dorks = [
        f'"{full_name}"',
        f'"{full_name}" site:linkedin.com',
        f'"{full_name}" site:facebook.com',
        f'"{full_name}" site:twitter.com',
        f'"{full_name}" email OR contact',
        f'"{full_name}" phone OR mobile',
        f'"{full_name}" resume OR CV',
        f'"{full_name}" filetype:pdf',
        f'"{full_name}" "about me"',
        f'"{full_name}" company OR work'
    ]
    
    return {
        'dorks': dorks,
        'google_search_url': f'https://www.google.com/search?q={full_name.replace(" ", "+")}',
        'note': 'Use these in Google for targeted searches'
    }

def generate_username_variations(first, last):
    """Generate possible username variations"""
    first_lower = first.lower()
    last_lower = last.lower()
    
    variations = [
        f"{first_lower}{last_lower}",
        f"{first_lower}.{last_lower}",
        f"{first_lower}_{last_lower}",
        f"{first_lower}-{last_lower}",
        f"{first_lower[0]}{last_lower}",
        f"{last_lower}{first_lower}",
        f"{last_lower}.{first_lower}",
        f"{first_lower}{last_lower[0]}"
    ]
    
    return variations

def check_name_email_match(first, last, email):
    """Check if name matches email pattern"""
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
        'details': matches if matches else ['No obvious name-email pattern match'],
        'confidence': 'High' if len(matches) >= 2 else 'Medium' if len(matches) == 1 else 'Low'
    }
