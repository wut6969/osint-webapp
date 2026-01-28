import requests
import re
from app.google_search import generate_google_dorks_with_preview
from concurrent.futures import ThreadPoolExecutor, as_completed

def investigate_name(first_name, last_name, email=None):
    """Comprehensive name-based OSINT investigation"""
    
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
    """Generate potential phone number search patterns"""
    full_name = f"{first} {last}"
    
    return {
        'search_links': [
            {
                'name': 'TrueCaller',
                'url': f'https://www.truecaller.com/search/us/{full_name.replace(" ", "%20")}',
                'description': 'Phone number lookup'
            },
            {
                'name': 'WhitePages Phone',
                'url': f'https://www.whitepages.com/name/{full_name.replace(" ", "-")}',
                'description': 'Phone and address search'
            }
        ],
        'note': 'Search these sites to find phone numbers associated with this name'
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
            'description': 'Microblogging'
        },
        {
            'name': 'Instagram',
            'url': f'https://www.instagram.com/explore/tags/{full_name_nospace}/',
            'description': 'Photo sharing'
        },
        {
            'name': 'TikTok',
            'url': f'https://www.tiktok.com/search/user?q={first}%20{last}',
            'description': 'Video platform'
        },
        {
            'name': 'Snapchat',
            'url': f'https://story.snapchat.com/search?q={first}%20{last}',
            'description': 'Messaging app'
        }
    ]
    
    return {
        'platforms': platforms,
        'note': 'Manual verification required - multiple people may share this name'
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
            'type': 'Blogging'
        },
        {
            'name': 'Behance',
            'url': f'https://www.behance.net/search/users?search={first}%20{last}',
            'type': 'Creative portfolios'
        },
        {
            'name': 'AngelList',
            'url': f'https://angel.co/search?q={first}%20{last}',
            'type': 'Startup community'
        },
        {
            'name': 'ResearchGate',
            'url': f'https://www.researchgate.net/search/researcher?q={first}%20{last}',
            'type': 'Academic research'
        }
    ]
    
    return sites

def search_dark_web_by_name(full_name, email=None):
    """Search dark web and leak databases by name"""
    search_query = full_name if not email else f"{full_name} {email}"
    
    return {
        'search_engines': [
            {
                'name': 'Intelligence X (Name)',
                'url': f'https://intelx.io/?s={full_name.replace(" ", "+")}',
                'description': 'Dark web search engine'
            },
            {
                'name': 'DarkSearch (Name)',
                'url': f'https://darksearch.io/?query={full_name.replace(" ", "+")}',
                'description': 'Tor search'
            },
            {
                'name': 'Ahmia (Name)',
                'url': f'https://ahmia.fi/search/?q={full_name.replace(" ", "+")}',
                'description': 'Hidden services'
            }
        ],
        'leak_databases': [
            {
                'name': 'DeHashed',
                'url': f'https://dehashed.com/search?query={search_query.replace(" ", "+")}',
                'note': 'Comprehensive breach database ($4.99/month)'
            },
            {
                'name': 'LeakCheck',
                'url': f'https://leakcheck.io/search?query={full_name.replace(" ", "+")}',
                'note': 'Free basic search'
            },
            {
                'name': 'SnusBase',
                'url': 'https://snusbase.com',
                'note': 'Leaked database search (paid)'
            }
        ],
        'note': 'Dark web results require manual verification and may take time'
    }

def search_pastes_by_name(full_name):
    """Search paste sites for name mentions"""
    return {
        'search_links': [
            {
                'name': 'Psbdmp (Name)',
                'url': f'https://psbdmp.ws/?q={full_name.replace(" ", "+")}',
                'description': 'Pastebin dump search'
            },
            {
                'name': 'Pastebin Search',
                'url': f'https://www.google.com/search?q=site:pastebin.com+"{full_name}"',
                'description': 'Google search of Pastebin'
            },
            {
                'name': 'Ghostbin',
                'url': f'https://www.google.com/search?q=site:ghostbin.com+"{full_name}"',
                'description': 'Alternative paste site'
            }
        ],
        'note': 'Check for data leaks in paste dumps'
    }

def generate_public_record_links(full_name):
    """Generate links to public record databases"""
    encoded_name = full_name.replace(' ', '+')
    
    databases = [
        {
            'name': 'Whitepages',
            'url': f'https://www.whitepages.com/name/{full_name.replace(" ", "-")}',
            'description': 'Phone & addresses'
        },
        {
            'name': 'TruePeopleSearch',
            'url': f'https://www.truepeoplesearch.com/results?name={encoded_name}',
            'description': 'Free people search'
        },
        {
            'name': 'FastPeopleSearch',
            'url': f'https://www.fastpeoplesearch.com/name/{full_name.replace(" ", "-")}',
            'description': 'Public records'
        },
        {
            'name': 'Spokeo',
            'url': f'https://www.spokeo.com/{full_name.replace(" ", "-")}',
            'description': 'Premium search'
        },
        {
            'name': 'BeenVerified',
            'url': f'https://www.beenverified.com/people/{full_name.replace(" ", "-")}',
            'description': 'Background check'
        },
        {
            'name': 'Instant Checkmate',
            'url': f'https://www.instantcheckmate.com/?firstName={full_name.split()[0]}&lastName={full_name.split()[1]}',
            'description': 'Criminal records'
        }
    ]
    
    return {
        'databases': databases,
        'warning': 'Some services require payment for full results'
    }

def search_legal_records(full_name):
    """Search court and legal records"""
    return {
        'court_records': [
            {
                'name': 'PACER (Federal Courts)',
                'url': 'https://pacer.uscourts.gov/',
                'description': 'Federal court records (requires account)'
            },
            {
                'name': 'UniCourt',
                'url': f'https://unicourt.com/search?q={full_name.replace(" ", "+")}',
                'description': 'Legal case search'
            },
            {
                'name': 'CourtListener',
                'url': f'https://www.courtlistener.com/?q={full_name.replace(" ", "+")}',
                'description': 'Free legal opinions'
            }
        ],
        'property_records': [
            {
                'name': 'Zillow Public Records',
                'url': f'https://www.zillow.com/homes/{full_name.replace(" ", "-")}_rb/',
                'description': 'Property ownership'
            },
            {
                'name': 'PropertyShark',
                'url': f'https://www.propertyshark.com/mason/Search/Search?search={full_name.replace(" ", "+")}',
                'description': 'Real estate records'
            }
        ],
        'note': 'Federal records require PACER account; state records vary by jurisdiction'
    }

def search_business_records(full_name):
    """Search business registrations and licenses"""
    return {
        'business_searches': [
            {
                'name': 'OpenCorporates',
                'url': f'https://opencorporates.com/officers?q={full_name.replace(" ", "+")}',
                'description': 'Corporate officer search'
            },
            {
                'name': 'Secretary of State Search',
                'url': 'https://www.nass.org/business-services/corporate-registration',
                'description': 'State business registrations'
            },
            {
                'name': 'Better Business Bureau',
                'url': f'https://www.bbb.org/search?find_text={full_name.replace(" ", "+")}',
                'description': 'Business complaints'
            }
        ],
        'professional_licenses': [
            {
                'name': 'License Lookup',
                'url': f'https://www.google.com/search?q="{full_name}"+professional+license',
                'description': 'Professional licensing boards'
            },
            {
                'name': 'USPTO Patent Search',
                'url': f'https://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&f=S&l=50&d=PTXT&Query=IN/{full_name.split()[0]}+AND+IN/{full_name.split()[1]}',
                'description': 'Patent inventor search'
            },
            {
                'name': 'Trademark Search',
                'url': f'https://www.uspto.gov/trademarks/search',
                'description': 'USPTO trademark database'
            }
        ]
    }

def search_crypto_addresses(full_name, email=None):
    """Search for crypto wallet addresses"""
    search_term = email if email else full_name
    
    return {
        'blockchain_searches': [
            {
                'name': 'Bitcoin Who\'s Who',
                'url': f'https://bitcoinwhoswho.com/search/?q={search_term.replace(" ", "+")}',
                'description': 'Bitcoin scam database'
            },
            {
                'name': 'Wallet Explorer',
                'url': 'https://www.walletexplorer.com/',
                'description': 'Bitcoin wallet clustering'
            },
            {
                'name': 'Etherscan Search',
                'url': f'https://etherscan.io/searchHandler?term={search_term.replace(" ", "+")}',
                'description': 'Ethereum blockchain'
            }
        ],
        'note': 'Crypto searches work best with known wallet addresses or email'
    }

def search_archives(full_name):
    """Search archived web content"""
    return {
        'archive_sites': [
            {
                'name': 'Wayback Machine',
                'url': f'https://web.archive.org/web/*/{full_name.replace(" ", "")}',
                'description': 'Archived websites'
            },
            {
                'name': 'Archive.today',
                'url': f'https://archive.ph/{full_name.replace(" ", "+")}',
                'description': 'Recent archives'
            },
            {
                'name': 'Google Cache',
                'url': f'https://www.google.com/search?q=cache:"{full_name}"',
                'description': 'Cached pages'
            }
        ],
        'note': 'Useful for finding deleted profiles or old information'
    }

def generate_name_dorks(full_name):
    """Use new UK/EU focused Google search with previews"""
    return generate_google_dorks_with_preview(full_name, is_email=False)

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
        f"{first_lower}{last_lower[0]}",
        f"{first_lower}{last_lower}123",
        f"{first_lower}{last_lower[0]}1"
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
