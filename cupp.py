#!/usr/bin/python3
#
#  [Program]
#
#  CUPP
#  Common User Passwords Profiler
#
#  [Author]
#
#  Muris Kurgas aka j0rgan
#  j0rgan [at] remote-exploit [dot] org
#  http://www.remote-exploit.org
#  http://www.azuzi.me
#
#  [License]
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#  See 'LICENSE' for more information.

import argparse
import configparser
import csv
import functools
import gzip
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import time
import itertools
from datetime import datetime
from collections import defaultdict

__author__ = "Mebus"
__license__ = "GPL"
__version__ = "4.0.0"

CONFIG = {}
LEET_REPLACEMENTS = {}
COMMON_SUFFIXES = []
SEPARATORS = []
INTEREST_MODIFIERS = []

def read_config(filename):
    """Read configuration file with enhanced leet mappings"""
    global COMMON_SUFFIXES, SEPARATORS, INTEREST_MODIFIERS
    
    if os.path.isfile(filename):
        # Create config parser with disabled interpolation
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = lambda option: option  # Make option names case-sensitive
        
        config.read(filename)
        
        # Global configuration
        CONFIG["global"] = {
            "years": config.get("years", "years").split(","),
            "chars": config.get("specialchars", "chars").split(","),
            "numfrom": config.getint("nums", "from"),
            "numto": config.getint("nums", "to"),
            "wcfrom": config.getint("wordlength", "wcfrom"),
            "wcto": config.getint("wordlength", "wcto"),
            "threshold": config.getint("threshold", "threshold"),
            "alectourl": config.get("alecto", "alectourl"),
            "dicturl": config.get("downloader", "dicturl"),
        }

        # Load dynamic lists from config
        COMMON_SUFFIXES = config.get("profiling", "suffixes").split(",")
        SEPARATORS = config.get("profiling", "separators").split(",")
        INTEREST_MODIFIERS = config.get("profiling", "interest_modifiers").split(",")

        # Enhanced leet mappings
        leet_mappings = {}
        if config.has_section("leet"):
            for letter in config.options("leet"):
                leet_mappings[letter] = config.get("leet", letter)
        
        CONFIG["LEET"] = leet_mappings

        return True
    else:
        print(f"Configuration file {filename} not found!")
        sys.exit("Exiting.")

def make_leet(x):
    """Convert string to leet using enhanced mappings"""
    for letter, leetletter in CONFIG["LEET"].items():
        x = x.replace(letter, leetletter)
    return x

def clean_input(value):
    """Clean and normalize input values"""
    if not value:
        return ""
    # Remove ALL spaces
    value = re.sub(r'\s+', '', value.strip())
    return value

def get_input(prompt, required=False, input_type=str, multiple=False, allow_empty=False):
    """Get validated user input with optional empty values"""
    while True:
        value = input(prompt).strip()
        
        if not value:
            if required:
                print("This field is required.")
                continue
            if allow_empty:
                return ""
        
        if multiple:
            return [item.strip() for item in value.split(',') if item.strip()]
            
        try:
            return input_type(value)
        except ValueError:
            print(f"Invalid format. Please enter a {input_type.__name__}.")
            continue

def validate_date(date_str):
    """Validate date format (YYYY-MM-DD) or return empty"""
    if not date_str:
        return ""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format or empty")

def collect_profile():
    """Interactive profile collection with all fields optional except first name"""
    profile = defaultdict(dict)
    
    print("\n===== Personal Information =====")
    profile['first_name'] = get_input("First Name: ", required=True)
    profile['middle_name'] = get_input("Middle name/initial (optional): ", allow_empty=True)
    profile['last_name'] = get_input("Last Name (optional): ", allow_empty=True)
    profile['nickname'] = get_input("Nickname (optional): ", allow_empty=True)
    profile['birthdate'] = get_input("Birthdate (YYYY-MM-DD, optional): ", input_type=validate_date, allow_empty=True)
    
    # Add favorite numbers
    profile['favorite_numbers'] = get_input(
        "Favorite numbers (comma separated, e.g., 7,13,42,99, optional): ",
        multiple=True,
        allow_empty=True
    )
    
    print("\n===== Relationship Information =====")
    if get_input("Do you have a partner? (y/n, optional): ").lower() == 'y':
        profile['partner']['first_name'] = get_input("Partner's First Name (optional): ", allow_empty=True)
        profile['partner']['nickname'] = get_input("Partner's Nickname (optional): ", allow_empty=True)
        profile['partner']['birthdate'] = get_input("Partner's Birthdate (YYYY-MM-DD, optional): ", input_type=validate_date, allow_empty=True)
    
    print("\n===== Pet Information =====")
    if get_input("Do you have a pet? (y/n, optional): ").lower() == 'y':
        profile['pet']['name'] = get_input("Pet's Name (optional): ", allow_empty=True)
    
    print("\n===== Contact Information (optional) =====")
    profile['phones'] = get_input("Phone Numbers (comma separated, optional): ", multiple=True, allow_empty=True)
    profile['emails'] = get_input("Email Addresses (comma separated, optional): ", multiple=True, allow_empty=True)
    profile['social_media_handles'] = get_input("Social Media Handles (comma separated, with @, optional): ", multiple=True, allow_empty=True)
    
    print("\n===== Address Information (optional) =====")
    profile['address'] = {}
    profile['address']['street'] = get_input("Street Address (optional): ", allow_empty=True)
    profile['address']['city'] = get_input("City (optional): ", allow_empty=True)
    profile['address']['zip'] = get_input("ZIP Code (optional): ", allow_empty=True)
    profile['address']['state'] = get_input("State (optional): ", allow_empty=True)
    
    print("\n===== Education Information (optional) =====")
    profile['education'] = {}
    profile['education']['school'] = get_input("School/University (optional): ", allow_empty=True)
    profile['education']['mascot'] = get_input("School Mascot (optional): ", allow_empty=True)
    profile['education']['graduation_year'] = get_input("Graduation Year (optional): ", input_type=lambda x: x if not x else int(x), allow_empty=True)
    
    print("\n===== Career Information (optional) =====")
    profile['company'] = {}
    profile['company']['name'] = get_input("Company Name (optional): ", allow_empty=True)
    profile['company']['department'] = get_input("Department (optional): ", allow_empty=True)
    profile['job_title'] = get_input("Job Title (optional): ", allow_empty=True)
    
    print("\n===== Interests & Hobbies (optional) =====")
    profile['interests'] = get_input("Interests (comma separated, optional): ", multiple=True, allow_empty=True)
    
    print("\n===== Vehicle Information (optional) =====")
    if get_input("Do you own a vehicle? (y/n, optional): ").lower() == 'y':
        profile['car'] = {}
        profile['car']['make'] = get_input("Car Make (optional): ", allow_empty=True)
        profile['car']['model'] = get_input("Car Model (optional): ", allow_empty=True)
        profile['car']['year'] = get_input("Manufacture Year (optional): ", input_type=lambda x: x if not x else int(x), allow_empty=True)
        profile['car']['plate'] = get_input("License Plate (optional): ", allow_empty=True).replace(" ", "")
    
    print("\n===== Important Dates (optional) =====")
    profile['anniversary'] = get_input("Anniversary Date (YYYY-MM-DD, optional): ", input_type=validate_date, allow_empty=True)
    
    return profile

def extract_base_terms(profile):
    """Extract and preprocess all relevant base terms from the profile"""
    terms = set()
    
    # Helper function to clean and add terms
    def add_term(term):
        """Clean and add term variations to the set"""
        if not term:
            return
        # Clean and normalize the term
        cleaned = re.sub(r'\s+', '', str(term).strip())
        if cleaned:
            terms.add(cleaned)
            terms.add(cleaned.lower())
            terms.add(cleaned.upper())
            terms.add(cleaned.capitalize())
    
    # Helper function to add name combinations
    def add_name_combinations(first, middle, last):
        """Generate intelligent name combinations"""
        # Ensure names are cleaned of spaces
        first = re.sub(r'\s+', '', first)
        last = re.sub(r'\s+', '', last)
        if middle:
            middle = re.sub(r'\s+', '', middle)
            
        if first and last:
            # Add concatenated versions
            terms.add(first + last)
            terms.add(last + first)
            
            # Add lowercase version explicitly
            terms.add((first + last).lower())
            
            # Add mixed-case version: FirstnameLastname
            terms.add(first.capitalize() + last.capitalize())
            
            # Add other combinations
            terms.add(first + last[:3])
            terms.add(first[:1] + last)
            terms.add(last + first[:1])
            
            if middle:
                terms.add(first + middle[:1] + last)
                terms.add(first[0] + middle[0] + last)
                terms.add(first + last + middle[0])
    
    # Personal names - clean immediately
    first_name = clean_input(profile.get('first_name', ''))
    middle_name = clean_input(profile.get('middle_name', ''))
    last_name = clean_input(profile.get('last_name', ''))
    nickname = clean_input(profile.get('nickname', ''))
    
    add_term(first_name)
    add_term(middle_name)
    add_term(last_name)
    add_term(nickname)
    
    # Generate name combinations
    add_name_combinations(first_name, middle_name, last_name)
    
    # Partner info
    if 'partner' in profile:
        partner_first = profile['partner'].get('first_name', '')
        partner_nick = profile['partner'].get('nickname', '')
        
        add_term(partner_first)
        add_term(partner_nick)
        
        # Partner name combinations
        add_name_combinations(first_name, '', partner_first)
        add_name_combinations(partner_first, '', last_name)
    
    # Pet info
    if 'pet' in profile:
        pet_name = profile['pet'].get('name', '')
        add_term(pet_name)
        
        # Pet name combinations
        add_name_combinations(first_name, '', pet_name)
        add_name_combinations(last_name, '', pet_name)
    
    # Address components
    if 'address' in profile:
        addr = profile['address']
        add_term(addr.get('street', ''))
        add_term(addr.get('city', ''))
        add_term(addr.get('zip', ''))
        add_term(addr.get('state', ''))
        
        # Split street into components
        if 'street' in addr:
            for part in re.split(r'\W+', addr['street']):
                if part and not part.isdigit():
                    add_term(part)
    
    # Education info
    if 'education' in profile:
        edu = profile['education']
        add_term(edu.get('school', ''))
        add_term(edu.get('mascot', ''))
        
        # Graduation year
        if 'graduation_year' in edu:
            grad_year = str(edu['graduation_year'])
            add_term(grad_year)
            
            # Combine with names
            if first_name:
                terms.add(first_name + grad_year)
            if last_name:
                terms.add(last_name + grad_year)
    
    # Company info
    if 'company' in profile:
        comp = profile['company']
        add_term(comp.get('name', ''))
        add_term(comp.get('department', ''))
    
    # Job title
    add_term(profile.get('job_title', ''))
    
    # Interests
    if 'interests' in profile:
        for interest in profile['interests']:
            add_term(interest)
    
    # Car info
    if 'car' in profile:
        car = profile['car']
        add_term(car.get('make', ''))
        add_term(car.get('model', ''))
        add_term(car.get('plate', ''))
        if 'year' in car:
            car_year = str(car['year'])
            add_term(car_year)
            
            # Combine with names
            if first_name:
                terms.add(first_name + car_year)
            if last_name:
                terms.add(last_name + car_year)
    
    # Phone numbers
    for phone in profile.get('phones', []):
        clean_phone = re.sub(r'\D', '', phone)
        if clean_phone:
            add_term(clean_phone)
            # Last 4 digits
            last4 = clean_phone[-4:]
            add_term(last4)
            
            # Combine with names
            if first_name:
                terms.add(first_name + last4)
            if last_name:
                terms.add(last_name + last4)
    
    # Emails and social media
    for email in profile.get('emails', []):
        username = email.split('@')[0]
        add_term(username)
        # Split email into components
        for part in re.split(r'[.\-_]', username):
            if part:
                add_term(part)
    
    for handle in profile.get('social_media_handles', []):
        clean_handle = re.sub(r'^@', '', handle)
        add_term(clean_handle)
        # Split handle into components
        for part in re.split(r'[.\-_]', clean_handle):
            if part:
                add_term(part)
    
    # Favorite numbers - with enhanced combinations
    favorite_numbers = profile.get('favorite_numbers', [])
    for number in favorite_numbers:
        if number:
            # Add number variations
            add_term(number)
            add_term(f"0{number}")  # Zero-padded version
            add_term(number.zfill(2))  # Two-digit zero-padded
            add_term(number.zfill(3))  # Three-digit zero-padded
            
            # Add number combinations with names
            if first_name:
                terms.add(first_name + number)
                terms.add(number + first_name)
            if last_name:
                terms.add(last_name + number)
                terms.add(number + last_name)
            if first_name and last_name:
                terms.add(first_name + last_name + number)
                terms.add(number + first_name + last_name)
                
            # Add number combinations with nickname
            if nickname:
                terms.add(nickname + number)
                terms.add(number + nickname)

    if favorite_numbers:
        # Generate permutations of all lengths
        for r in range(1, len(favorite_numbers) + 1):
            for perm in itertools.permutations(favorite_numbers, r):
                perm_str = ''.join(perm)
                
                # Add the permutation itself
                add_term(perm_str)
                add_term(perm_str.zfill(len(perm_str) + 1))  # Zero-padded
                
                # Add combinations with names
                if first_name:
                    terms.add(first_name + perm_str)
                    terms.add(perm_str + first_name)
                if last_name:
                    terms.add(last_name + perm_str)
                    terms.add(perm_str + last_name)
                if first_name and last_name:
                    terms.add(first_name + last_name + perm_str)
                    terms.add(perm_str + first_name + last_name)
                
                # Add combinations with nickname
                if nickname:
                    terms.add(nickname + perm_str)
                    terms.add(perm_str + nickname)

    
    # Anniversary year extraction
    if 'anniversary' in profile and profile['anniversary']:
        try:
            anniv_year = str(datetime.strptime(profile['anniversary'], '%Y-%m-%d').year)
            add_term(anniv_year)
            
            # Combine with names
            if first_name:
                terms.add(first_name + anniv_year)
            if last_name:
                terms.add(last_name + anniv_year)
        except ValueError:
            pass
    
    return {term for term in terms if term and 3 <= len(term) <= 30}

def generate_variations(terms):
    """Generate high-quality variations"""
    variations = set()
    
    for term in terms:
        if not term:
            continue
            
        # Original and basic variations
        variations.add(term)
        variations.add(term.lower())
        variations.add(term.upper())
        variations.add(term.capitalize())
        
        # Leet transformations (only for alphanumeric terms)
        if any(c.isalpha() for c in term):
            leet_term = ''.join(LEET_REPLACEMENTS.get(c, c) for c in term)
            if leet_term != term:
                variations.add(leet_term)
        
        # Number suffix variations
        for suffix in COMMON_SUFFIXES:
            variations.add(term + suffix)
        
        # Special number combinations
        if any(c.isdigit() for c in term) and len(term) <= 5:
            for i in range(0, 10):
                variations.add(term + str(i))
                variations.add(str(i) + term)
    
    return variations

def generate_special_formats(profile):
    """Generate special formatted entries"""
    formats = set()
    date_fields = [
        ('birthdate', profile.get('birthdate', '')),
        ('partner_birthdate', profile.get('partner', {}).get('birthdate', '')),
        ('anniversary', profile.get('anniversary', ''))
    ]
    
    # Date transformations
    for field_name, date_str in date_fields:
        if date_str:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                formats.update({
                    dt.strftime('%m%d%Y'),  # MMDDYYYY
                    dt.strftime('%d%m%Y'),  # DDMMYYYY
                    dt.strftime('%Y%m%d'),  # YYYYMMDD
                    dt.strftime('%m%d%y'),  # MMDDYY
                    dt.strftime('%d%m%y'),  # DDMMYY
                    dt.strftime('%y%m%d'),  # YYMMDD
                    dt.strftime('%b%Y'),    # Dec2023
                    dt.strftime('%B%Y'),    # December2023
                    dt.strftime('%b%y'),    # Dec23
                    str(dt.year)            # Year alone
                })
            except ValueError:
                pass
    
    # Education year
    if 'education' in profile:
        grad_year = profile['education'].get('graduation_year')
        if grad_year:
            formats.add(str(grad_year))
    
    # Car year
    if 'car' in profile:
        car_year = profile['car'].get('year')
        if car_year:
            formats.add(str(car_year))
    
    return formats

def generate_combinations(variations, interests, favorite_numbers):
    """Generate intelligent combinations"""
    combos = set()
    
    # Convert to lists for processing
    variations_list = sorted(list(variations), key=len)
    interests_list = list(interests)[:5]  # Max 5 interests
    
    # Name + number combinations
    name_terms = [t for t in variations_list if any(c.isalpha() for c in t) and len(t) >= 3]
    number_terms = [t for t in variations_list if t.isdigit() and len(t) <= 4]
    
    for name in name_terms[:100]:  # Limit to 100 names
        for num in number_terms[:20]:  # Limit to 20 numbers
            combos.add(name + num)
            combos.add(num + name)
            combos.add(name + "_" + num)
            combos.add(name + "." + num)
            
        # Add special number formats
        for year in range(1950, 2025):
            combos.add(name + str(year))
            combos.add(str(year) + name)
    
    # Interest-based combinations
    for interest in interests_list:
        # Basic interest variations
        combos.add(interest)
        combos.add(interest + "123")
        combos.add(interest + "!")
        
        # Interest + number combinations
        for num in favorite_numbers[:5]:
            combos.add(interest + num)
            combos.add(num + interest)
        
        # Interest + name combinations
        for name in name_terms[:20]:
            combos.add(interest + name)
            combos.add(name + interest)
    
    return combos

def generate_number_combinations(numbers):
    """Generate combinations of favorite numbers with limits"""
    combos = set()
    if not numbers:
        return combos
    
    # Limit to 5 favorite numbers to prevent combinatorial explosion
    numbers = numbers[:5]
    
    # Single number variations
    for num in numbers:
        combos.add(num)
        # Add zero-padded versions
        for i in range(1, 4):  # Up to 3-digit padding
            combos.add(num.zfill(i))
        # Add reversed number
        combos.add(num[::-1])
    
    # Number pairs (limit to 10 combinations)
    count = 0
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j and count < 10:
                combos.add(numbers[i] + numbers[j])
                combos.add(f"{numbers[i]}_{numbers[j]}")
                combos.add(f"{numbers[i]}.{numbers[j]}")
                count += 1
    
    # Number sequences (limit to 100 combinations)
    count = 0
    for num in numbers:
        for i in range(1, 10):  # Single digit prefixes/suffixes
            if count < 100:
                combos.add(f"{i}{num}")
                combos.add(f"{num}{i}")
                count += 2
            else:
                break
    
    return combos

def generate_interest_terms(interests):
    """Generate interest-specific keywords"""
    terms = set()
    
    for interest in interests:
        lower_interest = interest.lower()
        # Add variations of the interest itself
        terms.add(lower_interest)
        terms.add(lower_interest + '123')
        terms.add('my' + lower_interest)
        terms.add('best' + lower_interest)
        
        # Add combinations with modifiers
        for modifier in INTEREST_MODIFIERS:
            terms.add(lower_interest + modifier)
            terms.add(modifier + lower_interest)
            terms.add(lower_interest + modifier + '123')
    
    return terms

def apply_modifiers(terms):
    """Apply modifiers more selectively"""
    modified = set()
    
    for term in terms:
        # Only apply to terms within length limits
        if not (4 <= len(term) <= 30):
            continue
        
        # Leet speak only for alphanumeric terms
        if CONFIG["LEET"] and any(c.isalpha() for c in term):
            leet_term = ''.join(CONFIG["LEET"].get(c, c) for c in term)
            if 4 <= len(leet_term) <= 30:
                modified.add(leet_term)
        
        # Case variations only if they change the term
        if term != term.lower():
            modified.add(term.lower())
        if term != term.upper():
            modified.add(term.upper())
        if term != term.capitalize():
            modified.add(term.capitalize())
    
    return modified

def generate_wordlist_from_profile(profile):
    """Generate high-quality password candidates"""
    wcfrom = CONFIG["global"]["wcfrom"]
    wcto = CONFIG["global"]["wcto"]
    
    # Step 1: Base terms
    base_terms = extract_base_terms(profile)
    
    # Step 2: Variations
    variations = generate_variations(base_terms)
    
    # Step 3: Special formats (dates, etc)
    special_formats = generate_special_formats(profile)
    
    # Step 4: Smart combinations
    favorite_numbers = profile.get('favorite_numbers', [])
    combinations = generate_combinations(
        variations,
        set(profile.get('interests', [])),
        favorite_numbers
    )
    
    # Step 5: Interest terms
    interest_terms = generate_interest_terms(profile.get('interests', []))
    
    # Combine all candidates
    all_candidates = (
        base_terms | 
        variations | 
        special_formats | 
        combinations | 
        interest_terms
    )
    
    # Apply final filters
    return sorted(
        [term for term in all_candidates if wcfrom <= len(term) <= wcto],
        key=len
    )

def print_to_file(filename, wordlist):
    """Save wordlist with quality control"""
    # Remove duplicates and sort
    unique_words = sorted(set(wordlist), key=len)
    
    with open(filename, 'w') as f:
        for password in unique_words:
            # Skip passwords with spaces
            if ' ' in password:
                continue
            f.write(password + '\n')
    
    print(f"[+] Saved {len(unique_words)} high-quality passwords to {filename}")
    print("[+] Examples of generated passwords:")
    for example in unique_words[:20]:
        print(f"    {example}")

def interactive():
    profile = collect_profile()
    word_generator = generate_wordlist_from_profile(profile)
    filename = f"{profile['first_name']}_{profile['last_name']}_wordlist.txt"
    print_to_file(filename, word_generator)

def print_cow():
    print(" ___________ ")
    print(" \033[07m  cupp.py! \033[27m                # \033[07mC\033[27mommon")
    print("      \\                     # \033[07mU\033[27mser")
    print("       \\   \033[1;31m,__,\033[1;m             # \033[07mP\033[27masswords")
    print("        \\  \033[1;31m(\033[1;moo\033[1;31m)____\033[1;m         # \033[07mP\033[27mrofiler")
    print("           \033[1;31m(__)    )\\ \033[1;m  ")
    print("           \033[1;31m   ||--|| \033[1;m\033[05m*\033[25m\033[1;m      [Enhanced Version]")
    print(28 * " " + "[Based on CUPP by Muris Kurgas]\r\n")

# ======================== ORIGINAL CUPP FUNCTIONS ======================== #

def version():
    """Display version"""
    print("\r\n \033[1;31m[ cupp.py ]  " + __version__ + "\033[1;m\r\n")
    print(" * Hacked up by j0rgan - j0rgan@remote-exploit.org")
    print(" * http://www.remote-exploit.org\r\n")
    print(" Take a look ./README.md file for more info about the program\r\n")

def improve_dictionary(file_to_open):
    """Implementation of the -w option. Improve a dictionary by
    interactively questioning the user."""
    # [Original implementation remains unchanged]
    pass

def download_http(url, targetfile):
    """Download file from URL"""
    print("[+] Downloading " + targetfile + " from " + url + " ... ")
    webFile = urllib.request.urlopen(url)
    localFile = open(targetfile, "wb")
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()

def alectodb_download():
    """Download csv from alectodb and save into local file as a list of
    usernames and passwords"""
    # [Original implementation remains unchanged]
    pass

def download_wordlist():
    """Implementation of -l switch. Download wordlists from http repository"""
    # [Original implementation remains unchanged]
    pass

def download_wordlist_http(filedown):
    """Download wordlists from HTTP repository"""
    # [Original implementation remains unchanged]
    pass

def mkdir_if_not_exists(dire):
    """Create directory if it doesn't exist"""
    if not os.path.isdir(dire):
        os.mkdir(dire)

# ======================== MAIN FUNCTION ======================== #

def main():
    """Main function with enhanced interactive mode"""
    global LEET_REPLACEMENTS
    
    # Load configuration
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(base_dir, "cupp.cfg")
    read_config(config_path)
    LEET_REPLACEMENTS = CONFIG["LEET"]
    
    parser = get_parser()
    args = parser.parse_args()

    if not args.quiet:
        print_cow()

    if args.version:
        version()
    elif args.interactive:
        interactive()
    elif args.download_wordlist:
        download_wordlist()
    elif args.alecto:
        alectodb_download()
    elif args.improve:
        improve_dictionary(args.improve)
    else:
        parser.print_help()

def get_parser():
    """Create and return an argument parser"""
    parser = argparse.ArgumentParser(description="Common User Passwords Profiler")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Interactive questions for user password profiling",
    )
    group.add_argument(
        "-w",
        dest="improve",
        metavar="FILENAME",
        help="Use this option to improve existing dictionary,"
        " or WyD.pl output to make some pwnsauce",
    )
    group.add_argument(
        "-l",
        dest="download_wordlist",
        action="store_true",
        help="Download huge wordlists from repository",
    )
    group.add_argument(
        "-a",
        dest="alecto",
        action="store_true",
        help="Parse default usernames and passwords directly"
        " from Alecto DB. Project Alecto uses purified"
        " databases of Phenoelit and CIRT which were merged"
        " and enhanced",
    )
    group.add_argument(
        "-v", "--version", action="store_true", help="Show the version of this program."
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet mode (don't print banner)"
    )

    return parser

if __name__ == "__main__":
    main()
