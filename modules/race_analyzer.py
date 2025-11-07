"""
Race analysis engine for selecting A/B/C horses.

Implements the ABC Method:
- A (Anchor): Best credentialed runner ($2.80-$4.50 odds)
- B (Pace/Position): On-speed horse ($5-$10 odds)
- C (Value): Ready to spike ($8-$18 odds)
"""
from utils.odds_helpers import within_band
from utils.validators import (
    validate_field_size, count_top4_in_last3, barrier_ok,
    odds_shortening, extract_form_flags, parse_track_condition
)


def score_anchor_candidate(horse, race=None):
    """
    Score a horse as potential Anchor (A) candidate.
    
    Criteria:
    - Odds 2.80–4.50
    - Barrier ≤ 10
    - At least 2 top-4 finishes in last 3 runs
    - Track/distance match (bonus)
    - Market firmer (bonus)
    
    Returns:
        dict: {'score': float, 'rationale': str, 'qualified': bool}
    """
    score = 0
    rationale = []
    qualified = False
    
    odds = horse.get('odds_decimal')
    if not odds:
        return {'score': 0, 'rationale': 'No odds available', 'qualified': False}
    
    # Primary: Odds range (slightly flexible for favorites just under $2.80)
    if within_band(odds, 2.50, 4.50):
        score += 10
        rationale.append(f"Good anchor odds (${odds:.2f})")
        qualified = True
    else:
        rationale.append(f"Odds ${odds:.2f} outside anchor range")
        return {'score': score, 'rationale': '; '.join(rationale), 'qualified': False}
    
    # Barrier
    barrier = horse.get('barrier')
    if barrier:
        barrier_check = barrier_ok(barrier, preferred_max=10)
        if barrier_check['ok'] and barrier <= 10:
            score += 3
            rationale.append(barrier_check['message'])
        elif barrier > 10:
            score -= 2
            rationale.append(f"Wide barrier ({barrier})")
    
    # Form
    last3_form = horse.get('last3_form', '')
    top4_count = count_top4_in_last3(last3_form)
    if top4_count >= 2:
        score += 5
        rationale.append(f"Consistent form ({top4_count}/3 top-4)")
    else:
        score -= 2
        rationale.append(f"Inconsistent recent form")
    
    # Market firmer
    if odds_shortening(horse.get('market_open_odds'), horse.get('market_current_odds')):
        score += 3
        rationale.append("Market firmer")
    
    # Track/distance preference (if available)
    if race and horse.get('track_pref'):
        if race.get('track', '').lower() in horse['track_pref'].lower():
            score += 2
            rationale.append("Track specialist")
    
    return {
        'score': score,
        'rationale': '; '.join(rationale),
        'qualified': qualified
    }


def score_pace_candidate(horse, race=None):
    """
    Score a horse as potential Pace/Position (B) candidate.
    
    Criteria:
    - Odds 5.00–10.00
    - Speed map: leaders or on-pace
    - Proven at distance
    - Barrier advantage (≤ 8 preferred)
    
    Returns:
        dict: {'score': float, 'rationale': str, 'qualified': bool}
    """
    score = 0
    rationale = []
    qualified = False
    
    odds = horse.get('odds_decimal')
    if not odds:
        return {'score': 0, 'rationale': 'No odds available', 'qualified': False}
    
    # Primary: Odds range
    if within_band(odds, 5.00, 10.00):
        score += 10
        rationale.append(f"Good pace odds (${odds:.2f})")
        qualified = True
    else:
        rationale.append(f"Odds ${odds:.2f} outside pace range")
        return {'score': score, 'rationale': '; '.join(rationale), 'qualified': False}
    
    # Speed map position
    speed_map = horse.get('speed_map_hint', '').lower()
    if speed_map in ['leaders', 'on-pace']:
        score += 5
        rationale.append(f"Good speed position ({speed_map})")
    elif speed_map in ['midfield']:
        score += 1
        rationale.append("Midfield runner")
    else:
        score -= 2
        rationale.append("Back marker")
    
    # Barrier
    barrier = horse.get('barrier')
    if barrier:
        if barrier <= 8:
            score += 4
            rationale.append(f"Excellent barrier ({barrier})")
        elif barrier <= 10:
            score += 2
            rationale.append(f"Good barrier ({barrier})")
        else:
            score -= 1
            rationale.append(f"Wide barrier ({barrier})")
    
    # Distance preference
    if race and horse.get('distance_pref') and race.get('distance_m'):
        # Simple check - can be enhanced
        score += 2
        rationale.append("Proven at trip")
    
    # Market firmer
    if odds_shortening(horse.get('market_open_odds'), horse.get('market_current_odds')):
        score += 2
        rationale.append("Market firmer")
    
    return {
        'score': score,
        'rationale': '; '.join(rationale),
        'qualified': qualified
    }


def score_value_candidate(horse, race=None):
    """
    Score a horse as potential Value (C) candidate.
    
    Criteria:
    - Odds 8.00–18.00
    - Form spike indicators:
      * Up in trip
      * Down in class
      * Forgive last run
    
    Returns:
        dict: {'score': float, 'rationale': str, 'qualified': bool}
    """
    score = 0
    rationale = []
    qualified = False
    
    odds = horse.get('odds_decimal')
    if not odds:
        return {'score': 0, 'rationale': 'No odds available', 'qualified': False}
    
    # Primary: Odds range
    if within_band(odds, 8.00, 18.00):
        score += 10
        rationale.append(f"Value odds (${odds:.2f})")
        qualified = True
    else:
        rationale.append(f"Odds ${odds:.2f} outside value range")
        return {'score': score, 'rationale': '; '.join(rationale), 'qualified': False}
    
    # Form spike flags
    form_flags = extract_form_flags(horse.get('last3_form', ''))
    
    if form_flags['up_in_trip']:
        score += 4
        rationale.append("Up in trip")
    
    if form_flags['down_in_class']:
        score += 4
        rationale.append("Down in class")
    
    if form_flags['forgive']:
        score += 3
        rationale.append("Forgive last run")
    
    # Barrier - less critical for value horses
    barrier = horse.get('barrier')
    if barrier and barrier <= 10:
        score += 2
        rationale.append(f"Decent barrier ({barrier})")
    
    # Recent form (at least one good run)
    last3_form = horse.get('last3_form', '')
    top4_count = count_top4_in_last3(last3_form)
    if top4_count >= 1:
        score += 3
        rationale.append(f"Has recent form ({top4_count}/3 top-4)")
    
    return {
        'score': score,
        'rationale': '; '.join(rationale),
        'qualified': qualified
    }


def analyze_race(race, horses):
    """
    Analyze a race and select A/B/C candidates.
    
    Args:
        race: Race dict with context
        horses: List of horse dicts
        
    Returns:
        dict: Analysis results with candidates, checklist, scores
    """
    # Score all horses for each category
    anchor_scores = []
    pace_scores = []
    value_scores = []
    
    for horse in horses:
        if horse.get('is_scratched'):
            continue
        
        a_result = score_anchor_candidate(horse, race)
        b_result = score_pace_candidate(horse, race)
        c_result = score_value_candidate(horse, race)
        
        if a_result['qualified']:
            anchor_scores.append({
                'horse': horse,
                'score': a_result['score'],
                'rationale': a_result['rationale']
            })
        
        if b_result['qualified']:
            pace_scores.append({
                'horse': horse,
                'score': b_result['score'],
                'rationale': b_result['rationale']
            })
        
        if c_result['qualified']:
            value_scores.append({
                'horse': horse,
                'score': c_result['score'],
                'rationale': c_result['rationale']
            })
    
    # Sort by score (descending)
    anchor_scores.sort(key=lambda x: x['score'], reverse=True)
    pace_scores.sort(key=lambda x: x['score'], reverse=True)
    value_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Select top candidates ensuring they're all different horses
    a_horse = anchor_scores[0] if anchor_scores else None
    
    # For B, skip if it's the same as A
    b_horse = None
    for candidate in pace_scores:
        if not a_horse or candidate['horse']['name'] != a_horse['horse']['name']:
            b_horse = candidate
            break
    
    # For C, skip if it's the same as A or B
    c_horse = None
    for candidate in value_scores:
        horse_name = candidate['horse']['name']
        if (not a_horse or horse_name != a_horse['horse']['name']) and \
           (not b_horse or horse_name != b_horse['horse']['name']):
            c_horse = candidate
            break
    
    # Checklist
    num_runners = race.get('num_runners', len(horses))
    field_size_check = validate_field_size(num_runners)
    
    barriers_ok = True
    barrier_notes = []
    if a_horse and a_horse['horse'].get('barrier', 99) > 8:
        barriers_ok = False
        barrier_notes.append(f"A barrier {a_horse['horse']['barrier']} > 8")
    if b_horse and b_horse['horse'].get('barrier', 99) > 8:
        barriers_ok = False
        barrier_notes.append(f"B barrier {b_horse['horse']['barrier']} > 8")
    
    # Market firmers check
    market_firmers = []
    if a_horse and odds_shortening(a_horse['horse'].get('market_open_odds'), a_horse['horse'].get('market_current_odds')):
        market_firmers.append('A')
    if b_horse and odds_shortening(b_horse['horse'].get('market_open_odds'), b_horse['horse'].get('market_current_odds')):
        market_firmers.append('B')
    
    checklist = {
        'field_size_ok': field_size_check['valid'],
        'field_size_message': field_size_check['message'],
        'barriers_ok': barriers_ok,
        'barrier_notes': barrier_notes if not barriers_ok else ['A and B have good barriers'],
        'market_firmers': market_firmers,
        'track_condition': parse_track_condition(race.get('track_condition', ''))
    }
    
    return {
        'candidates': {
            'A': a_horse,
            'B': b_horse,
            'C': c_horse
        },
        'alternates': {
            'A': anchor_scores[1:4] if len(anchor_scores) > 1 else [],
            'B': pace_scores[1:4] if len(pace_scores) > 1 else [],
            'C': value_scores[1:4] if len(value_scores) > 1 else []
        },
        'checklist': checklist,
        'all_scores': {
            'anchor': anchor_scores,
            'pace': pace_scores,
            'value': value_scores
        }
    }
