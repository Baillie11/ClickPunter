"""
Validation and checking functions for race analysis.
"""
import re


def parse_track_condition(condition_str):
    """
    Parse track condition string to standard format.
    
    Args:
        condition_str: Track condition string
        
    Returns:
        str: One of GOOD, SOFT, HEAVY, SYNTH, UNKNOWN
    """
    if not condition_str:
        return 'UNKNOWN'
    
    condition_upper = str(condition_str).upper().strip()
    
    if 'GOOD' in condition_upper or 'FIRM' in condition_upper:
        return 'GOOD'
    elif 'SOFT' in condition_upper or 'YIELDING' in condition_upper:
        return 'SOFT'
    elif 'HEAVY' in condition_upper or 'SLOW' in condition_upper:
        return 'HEAVY'
    elif 'SYNTH' in condition_upper or 'POLY' in condition_upper:
        return 'SYNTH'
    
    return 'UNKNOWN'


def validate_field_size(num_runners, preferred_min=8, preferred_max=12):
    """
    Check if field size is in the preferred range.
    
    Args:
        num_runners: Number of runners
        preferred_min: Minimum preferred (default 8)
        preferred_max: Maximum preferred (default 12)
        
    Returns:
        dict: {'valid': bool, 'message': str}
    """
    if num_runners is None:
        return {'valid': False, 'message': 'Unknown field size'}
    
    if num_runners < preferred_min:
        return {
            'valid': False,
            'message': f'Small field ({num_runners} runners) - higher risk'
        }
    elif num_runners > preferred_max:
        return {
            'valid': False,
            'message': f'Large field ({num_runners} runners) - harder to pick'
        }
    else:
        return {
            'valid': True,
            'message': f'Ideal field size ({num_runners} runners)'
        }


def count_top4_in_last3(form_str):
    """
    Count top 4 finishes in the last 3 runs.
    
    Form string examples: "12x3", "241", "x14"
    
    Args:
        form_str: Form string
        
    Returns:
        int: Count of top 4 finishes (1-4)
    """
    if not form_str:
        return 0
    
    # Extract digits from form string
    digits = re.findall(r'\d', str(form_str))
    
    # Take up to last 3 runs
    last_3 = digits[:3] if len(digits) >= 3 else digits
    
    # Count 1, 2, 3, 4
    count = sum(1 for d in last_3 if d in ['1', '2', '3', '4'])
    
    return count


def barrier_ok(barrier, preferred_max=10):
    """
    Check if barrier is acceptable.
    
    Args:
        barrier: Barrier number
        preferred_max: Maximum preferred barrier (default 10)
        
    Returns:
        dict: {'ok': bool, 'message': str}
    """
    if barrier is None:
        return {'ok': False, 'message': 'No barrier info'}
    
    if barrier <= 8:
        return {'ok': True, 'message': f'Good barrier ({barrier})'}
    elif barrier <= preferred_max:
        return {'ok': True, 'message': f'Acceptable barrier ({barrier})'}
    else:
        return {'ok': False, 'message': f'Wide barrier ({barrier})'}


def horse_matches_conditions(horse_dict, race_dict):
    """
    Basic heuristic check if horse suits race conditions.
    
    Args:
        horse_dict: Horse data dict
        race_dict: Race data dict
        
    Returns:
        bool: True if conditions match
    """
    # This is a simple implementation - can be enhanced
    
    # Check track condition preference
    if race_dict.get('track_condition'):
        track_cond = parse_track_condition(race_dict['track_condition'])
        track_pref = horse_dict.get('track_pref', '')
        
        # If horse has wet track preference and it's wet, good match
        if track_cond in ['SOFT', 'HEAVY']:
            if 'wet' in str(track_pref).lower() or 'soft' in str(track_pref).lower():
                return True
    
    # Default to True if no specific mismatch found
    return True


def odds_shortening(open_odds, current_odds, threshold=0.9):
    """
    Check if odds have shortened (market firmer).
    
    Args:
        open_odds: Opening odds
        current_odds: Current odds
        threshold: Ratio threshold (default 0.9 = 10% shorter)
        
    Returns:
        bool: True if odds have shortened significantly
    """
    if not open_odds or not current_odds:
        return False
    
    # Odds shortened if current < open * threshold
    return current_odds < (open_odds * threshold)


def extract_form_flags(form_str):
    """
    Extract flags from form string (up in trip, down in class, forgive).
    
    Args:
        form_str: Form string or description
        
    Returns:
        dict: Flags {up_in_trip, down_in_class, forgive}
    """
    if not form_str:
        return {'up_in_trip': False, 'down_in_class': False, 'forgive': False}
    
    form_lower = str(form_str).lower()
    
    return {
        'up_in_trip': 'up in trip' in form_lower or 'step up' in form_lower,
        'down_in_class': 'down in class' in form_lower or 'drop' in form_lower,
        'forgive': 'forgive' in form_lower or 'excuse' in form_lower
    }
