# Changelog of CUPP

## 3.2.1

### 1. **Enhanced User Profiling**
- **Detailed Profile Sections**:
  - Personal information (first/middle/last name, nickname, birthdate)
  - Relationship information (partner details)
  - Pet information
  - Contact info (phones, emails, social media)
  - Address details (street, city, zip, state)
  - Education history (school, mascot, graduation year)
  - Career information (company, department, job title)
  - Interests & hobbies
  - Vehicle information (make, model, year, plate)
  - Important dates (anniversaries)

### 2. **Intelligent Password Generation**
- **Advanced Name Combinations**:
  - First + Last name combinations (JoseJuan)
  - First + Last partial combinations (JoseRub, JJuan)
  - Middle name incorporations (JosePJuan)
  - Nickname integrations
- **Smart Term Extraction**:
  - Email/social media username parsing
  - Address component splitting
  - Phone number segments (last 4 digits)
  - Vehicle license plate cleaning
- **Favorite Number Handling**:
  - Individual number variations (1, 01, 001)
  - All possible permutations (123, 132, 213, etc.)
  - Number + name combinations (Jose1, Juan123)
- **Date Intelligence**:
  - Multiple date formats (YYYY-MM-DD, MMDDYYYY, DDMMYY, etc.)
  - Year extraction from all dates
  - Anniversary/year combinations

### 3. **Combinatorial Improvements**
- **Controlled Generation**:
  - Limit checks to prevent combinatorial explosion
  - Length-based filtering (wcfrom/wcto)
  - Special format generation (dates, years)
- **Advanced Combinations**:
  - Interest-based terms (hacker123, !hacker)
  - Leet speak transformations (h@ck3r)
  - Case variations (Jose, Jose, Jose)
  - Separator combinations (Jose_Juan, Jose.123)

### 4. **Technical Improvements**
- **Input Validation**:
  - Required fields enforcement
  - Date format validation
  - Phone number cleaning
  - Email/social handle parsing
- **Code Structure**:
  - Modular functions (extract_base_terms, generate_variations)
  - Helper functions (add_term, add_name_combinations)
  - Dedicated configuration loader
- **Output Control**:
  - Duplicate removal
  - Length filtering (3-30 characters)
  - Space removal in passwords
  - Example password preview

### 5. **User Experience**
- **Interactive Interface**:
  - Sectioned input prompts
  - Clear progress indicators
  - Example-based output
- **Feedback Mechanisms**:
  - Word count reporting
  - Sample password display
  - Error messages for invalid input
- **File Handling**:
  - Automatic filename generation (Firstname_Lastname.txt)
  - Output summary with statistics

### 6. **Algorithmic Improvements**
- **Term Generation**:
  - Set-based operations for uniqueness
  - Length-based sorting
  - Controlled permutation generation
- **Memory Efficiency**:
  - Generator functions
  - Early filtering by length
  - Duplicate prevention
- **Configurable Rules**:
  - Leet substitutions
  - Common suffixes
  - Separators
  - Interest modifiers

### 7. **Special Features**
- **Favorite Number Processing**:
  - Zero-padded versions (1 → 01, 001)
  - All permutations (12345 → 120 combinations)
  - Name+number integrations (Jose123)
- **Advanced Name Handling**:
  - Multi-part name support (Jose Potato)
  - Name reversal combinations
  - Initial-based combinations (JPJuan)
- **Contextual Combinations**:
  - Pet + name combinations (JoseFluffy)
  - Interest + number combos (hiking123)
  - Vehicle + year integrations (Toyota2020)

### 8. **Validation and Error Handling**
- **Date Validation**:
  - Strict YYYY-MM-DD format
  - Year extraction fallbacks
- **Phone Validation**:
  - Digit extraction
  - Last-4 number handling
- **Empty Field Handling**:
  - Skip logic for optional fields
  - Conditional combination generation

### 9. **Configuration Management**
- **Externalized Rules**:
  - Leet character mappings
  - Common suffixes
  - Separators
  - Interest modifiers
- **Threshold Controls**:
  - Minimum password length
  - Maximum password length
  - Combination limits

These improvements transform CUPP from a simple password profiler into a sophisticated security tool that generates highly targeted wordlists while maintaining user-friendly interaction and robust data handling.

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## 3.2.0-alpha

 - ran 2to3 on cupp.py to make it Python3 compatible

## 3.1.0-alpha
 - added Python3 port
 - Bugfixes

## 3.0.0
 - added word length shaping function
 - added wordlists downloader function
 - added alectodb parser
 - fixed thresholds for word concatenations
 - fixed sorting in final parsing
 - fixed some user input validations
 - ascii cow now looks nicer :)

## 2.0.0
 - added l33t mode
 - added char mode
 - ability to make pwnsauce with other wordlists or wyd.pl outputs
 - cupp.cfg makes cupp.py easier to configure 


## 1.0.0
- Initial release


