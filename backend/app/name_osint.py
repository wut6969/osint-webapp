import re
temp_content = open('app/name_osint.py', 'r').read()

# Find and replace the generate_username_variations function
old_func_start = temp_content.find('def generate_username_variations(first, last):
    """Generate extensive username variations"""
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

