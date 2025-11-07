"""
Form parser for processing pasted/uploaded race data.
"""
import re
import csv
from io import StringIO
from utils.odds_helpers import to_decimal


def detect_format(text):
    """
    Detect the format of pasted text.
    
    Returns:
        str: 'csv', 'text_generic', 'punters', 'racingcom'
    """
    if ',' in text and '\n' in text:
        return 'csv'
    return 'text_generic'


def parse_csv(text):
    """
    Parse CSV format race data.
    
    Expected columns: name, barrier, odds, last3_form, jockey, trainer, speed_map_hint
    
    Returns:
        list: List of horse dicts
    """
    horses = []
    
    try:
        reader = csv.DictReader(StringIO(text))
        for row in reader:
            horse = {
                'name': row.get('name', '').strip(),
                'barrier': int(row.get('barrier', 0)) if row.get('barrier') else None,
                'odds_decimal': to_decimal(row.get('odds')),
                'last3_form': row.get('last3_form', '').strip(),
                'jockey': row.get('jockey', '').strip(),
                'trainer': row.get('trainer', '').strip(),
                'speed_map_hint': row.get('speed_map_hint', '').strip().lower(),
                'track_pref': row.get('track_pref', '').strip(),
                'distance_pref': row.get('distance_pref', '').strip()
            }
            horses.append(horse)
    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")
    
    return horses


def parse_text(text):
    """
    Parse generic text format.
    
    Expected format: "5. Fast Hoof (B4) $6.50 J:Smith T:Brown 12x3"
    Also handles Racing.com multi-line format.
    
    Returns:
        list: List of horse dicts
    """
    horses = []
    
    # Check if it's Racing.com format (has 'T:' and 'J:' on separate lines)
    if '\nT:' in text and '\nJ:' in text:
        # Try the smart parser first for messy data
        try:
            from modules.smart_parser import smart_parse
            horses = smart_parse(text)
            if horses:  # If smart parser found horses, use them
                return horses
        except Exception:
            pass  # Fall through to regular parser
        
        # Fallback to original Racing.com parser
        horses = parse_racing_com_format(text)
        if horses:
            return horses
    
    # Otherwise parse line by line
    lines = text.strip().split('\n')
    
    for line in lines:
        if not line.strip():
            continue
        
        horse = parse_line(line)
        if horse:
            horses.append(horse)
    
    return horses


def parse_racing_com_format(text):
    """
    Parse Racing.com copy-paste format.
    
    Format:
    1. Horse Name (Barrier)
    T: Trainer
    J: Jockey
    Form info
    W $odds P $place
    
    Returns:
        list: List of horse dicts
    """
    horses = []
    
    # Split by horse entries - more flexible pattern
    entries = re.split(r'(?=^\d+\.\s)', text, flags=re.MULTILINE)
    
    for entry in entries:
        if not entry.strip():
            continue
        
        horse = {}
        
        # Extract horse name and barrier
        # Handle format: "1. Horse Name (NZ) (Barrier)" or "1. Horse Name (Barrier)"
        name_match = re.search(r'^(\d+)\.\s+(.+?)\s*\((\d+)\)\s*$', entry.split('\n')[0], re.MULTILINE)
        if name_match:
            horse_name = name_match.group(2).strip()
            # Remove country codes like (NZ), (IRE), (AUS)
            horse_name = re.sub(r'\s*\([A-Z]{2,3}\)\s*$', '', horse_name)
            # Skip if name is too short or looks like junk
            if len(horse_name) < 2 or horse_name.isdigit():
                continue
            horse['name'] = horse_name
            horse['barrier'] = int(name_match.group(3))
        else:
            continue
        
        # Extract trainer
        trainer_match = re.search(r'T:\s*([\w\s,&.]+?)(?:\s+J:|\n)', entry)
        if trainer_match:
            horse['trainer'] = trainer_match.group(1).strip()
        
        # Extract jockey
        jockey_match = re.search(r'J:\s*([\w.]+)', entry)
        if jockey_match:
            horse['jockey'] = jockey_match.group(1).strip()
        
        # Extract WIN odds (W $... or W$...)
        odds_match = re.search(r'W\s*\$\s*([\d.]+)', entry)
        if odds_match:
            horse['odds_decimal'] = to_decimal(odds_match.group(1))
        else:
            # Sometimes the dollar sign might be formatted differently
            odds_match = re.search(r'W[\s\n]+([\d.]+)', entry)
            if odds_match:
                horse['odds_decimal'] = to_decimal(odds_match.group(1))
        
        # Extract form - look for patterns like "21" or "First Start"
        if 'First Start' in entry:
            horse['last3_form'] = 'First Start'
        else:
            form_match = re.search(r'(?:^|\n)(\d+)(?:\s+\d+:|\s+[\d:]+)', entry, re.MULTILINE)
            if form_match:
                horse['last3_form'] = form_match.group(1)
        
        # Check for speed indicators
        if 'FAVOURITE' in entry:
            horse['speed_map_hint'] = 'leaders'
        elif 'MOVER' in entry:
            horse['speed_map_hint'] = 'on-pace'
        else:
            horse['speed_map_hint'] = ''
        
        # Default values
        horse.setdefault('track_pref', '')
        horse.setdefault('distance_pref', '')
        horse.setdefault('market_open_odds', None)
        horse.setdefault('market_current_odds', None)
        horse.setdefault('is_scratched', False)
        
        horses.append(horse)
    
    return horses


def parse_line(line):
    """
    Parse a single line of text to extract horse info.
    
    Returns:
        dict: Horse data or None
    """
    # Pattern: Number. Name (Barrier) $Odds J:Jockey T:Trainer Form
    # Example: "5. Fast Hoof (4) $6.50 J:Smith T:Brown 12x3"
    # Also handles Racing.com format with multi-line data
    
    horse = {}
    
    # Extract name (before parenthesis or newline)
    name_match = re.search(r'^\d+\.\s*([^(\n]+)', line)
    if name_match:
        horse['name'] = name_match.group(1).strip()
    else:
        return None
    
    # Extract barrier
    barrier_match = re.search(r'\((?:B)?(\d+)\)', line)
    if barrier_match:
        horse['barrier'] = int(barrier_match.group(1))
    
    # Extract odds
    odds_match = re.search(r'\$?([\d.]+)', line)
    if odds_match:
        horse['odds_decimal'] = to_decimal(odds_match.group(1))
    
    # Extract jockey
    jockey_match = re.search(r'J:([^\s]+)', line)
    if jockey_match:
        horse['jockey'] = jockey_match.group(1).strip()
    
    # Extract trainer
    trainer_match = re.search(r'T:([^\s]+)', line)
    if trainer_match:
        horse['trainer'] = trainer_match.group(1).strip()
    
    # Extract form (digits with x)
    form_match = re.search(r'([0-9x]{2,5})', line, re.IGNORECASE)
    if form_match:
        horse['last3_form'] = form_match.group(1)
    
    # Default values
    horse.setdefault('speed_map_hint', '')
    horse.setdefault('track_pref', '')
    horse.setdefault('distance_pref', '')
    horse.setdefault('market_open_odds', None)
    horse.setdefault('market_current_odds', None)
    horse.setdefault('is_scratched', False)
    
    return horse


def parse_upload(file_stream, filename):
    """
    Parse an uploaded file.
    
    Returns:
        list: List of horse dicts
    """
    content = file_stream.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    
    if filename.endswith('.csv'):
        return parse_csv(content)
    else:
        return parse_text(content)
