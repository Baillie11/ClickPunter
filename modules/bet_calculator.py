"""
Betting calculator for computing combinations and applying strategies.
"""
from itertools import permutations, combinations
from utils.odds_helpers import flexi_percentage, format_currency


def combos_trifecta_boxed(horses):
    """
    Generate all trifecta combinations for boxed bet.
    
    Args:
        horses: List of 3 horses
        
    Returns:
        list: List of (1st, 2nd, 3rd) tuples (6 combos)
    """
    if len(horses) != 3:
        raise ValueError("Trifecta box requires exactly 3 horses")
    
    return list(permutations(horses, 3))


def combos_quinella_boxed(horses):
    """
    Generate all quinella combinations for boxed bet.
    
    Args:
        horses: List of 3 horses
        
    Returns:
        list: List of (horse1, horse2) tuples (3 combos)
    """
    if len(horses) != 3:
        raise ValueError("Quinella box requires exactly 3 horses")
    
    return list(combinations(horses, 2))


def combos_exacta_boxed(horses):
    """
    Generate all exacta combinations for boxed bet.
    
    Args:
        horses: List of horses
        
    Returns:
        list: List of (1st, 2nd) tuples
    """
    if len(horses) < 2:
        raise ValueError("Exacta box requires at least 2 horses")
    
    return list(permutations(horses, 2))


def combos_first4_boxed(horses):
    """
    Generate all first 4 combinations for boxed bet.
    
    Args:
        horses: List of 4+ horses
        
    Returns:
        list: List of (1st, 2nd, 3rd, 4th) tuples
    """
    if len(horses) < 4:
        raise ValueError("First 4 box requires at least 4 horses")
    
    return list(permutations(horses, 4))


def apply_strategy(strategy_type, selections, budget=None, options=None):
    """
    Apply a betting strategy and calculate stakes.
    
    Args:
        strategy_type: "budget_5", "budget_6", "custom"
        selections: dict with 'A', 'B', 'C' horse names/IDs
        budget: Total budget (required for custom)
        options: Additional options dict
        
    Returns:
        dict: Bet breakdown with stakes and combos
    """
    if options is None:
        options = {}
    
    horses = [selections.get('A'), selections.get('B'), selections.get('C')]
    
    # Validate selections
    if not all(horses):
        return {
            'error': 'Must select A, B, and C horses',
            'bets': [],
            'total_stake': 0
        }
    
    # Check for duplicates
    if len(set(horses)) != 3:
        return {
            'error': 'A, B, and C must be different horses',
            'bets': [],
            'total_stake': 0
        }
    
    bets = []
    total_stake = 0
    
    if strategy_type == 'budget_6':
        # $6 Strategy: $0.50 trifecta box + $1.00 quinella box
        tri_combos = combos_trifecta_boxed(horses)
        quin_combos = combos_quinella_boxed(horses)
        
        tri_unit = 0.50
        quin_unit = 1.00
        
        tri_stake = len(tri_combos) * tri_unit  # 6 * 0.50 = $3
        quin_stake = len(quin_combos) * quin_unit  # 3 * 1.00 = $3
        
        bets.append({
            'type': 'Trifecta Boxed',
            'unit': tri_unit,
            'num_combos': len(tri_combos),
            'stake': tri_stake,
            'flexi_pct': 1.0,
            'combos': tri_combos
        })
        
        bets.append({
            'type': 'Quinella Boxed',
            'unit': quin_unit,
            'num_combos': len(quin_combos),
            'stake': quin_stake,
            'flexi_pct': 1.0,
            'combos': quin_combos
        })
        
        total_stake = tri_stake + quin_stake
    
    elif strategy_type == 'budget_5':
        # $5 Strategy: $2 flexi trifecta + $3 quinella
        tri_combos = combos_trifecta_boxed(horses)
        quin_combos = combos_quinella_boxed(horses)
        
        tri_full_cost = len(tri_combos) * 1.0  # Full unit = $1
        tri_stake = 2.00
        tri_flexi = flexi_percentage(tri_stake, tri_full_cost)
        
        quin_unit = 1.00
        quin_stake = len(quin_combos) * quin_unit  # $3
        
        bets.append({
            'type': 'Trifecta Boxed (Flexi)',
            'unit': 1.0,
            'num_combos': len(tri_combos),
            'stake': tri_stake,
            'flexi_pct': tri_flexi,
            'combos': tri_combos
        })
        
        bets.append({
            'type': 'Quinella Boxed',
            'unit': quin_unit,
            'num_combos': len(quin_combos),
            'stake': quin_stake,
            'flexi_pct': 1.0,
            'combos': quin_combos
        })
        
        total_stake = tri_stake + quin_stake
    
    elif strategy_type == 'budget_10':
        # $10 Strategy: $1 trifecta box + $4 quinella box
        tri_combos = combos_trifecta_boxed(horses)
        quin_combos = combos_quinella_boxed(horses)
        
        tri_unit = 1.00
        quin_unit = 1.33  # $4 / 3 combos
        
        tri_stake = len(tri_combos) * tri_unit  # 6 * 1.00 = $6
        quin_stake = 4.00  # Round to $4
        
        bets.append({
            'type': 'Trifecta Boxed',
            'unit': tri_unit,
            'num_combos': len(tri_combos),
            'stake': tri_stake,
            'flexi_pct': 1.0,
            'combos': tri_combos
        })
        
        bets.append({
            'type': 'Quinella Boxed',
            'unit': quin_unit,
            'num_combos': len(quin_combos),
            'stake': quin_stake,
            'flexi_pct': 1.0,
            'combos': quin_combos
        })
        
        total_stake = tri_stake + quin_stake
    
    elif strategy_type == 'budget_15':
        # $15 Strategy: $1.50 trifecta box + $6 quinella box
        tri_combos = combos_trifecta_boxed(horses)
        quin_combos = combos_quinella_boxed(horses)
        
        tri_unit = 1.50
        quin_unit = 2.00
        
        tri_stake = len(tri_combos) * tri_unit  # 6 * 1.50 = $9
        quin_stake = len(quin_combos) * quin_unit  # 3 * 2.00 = $6
        
        bets.append({
            'type': 'Trifecta Boxed',
            'unit': tri_unit,
            'num_combos': len(tri_combos),
            'stake': tri_stake,
            'flexi_pct': 1.0,
            'combos': tri_combos
        })
        
        bets.append({
            'type': 'Quinella Boxed',
            'unit': quin_unit,
            'num_combos': len(quin_combos),
            'stake': quin_stake,
            'flexi_pct': 1.0,
            'combos': quin_combos
        })
        
        total_stake = tri_stake + quin_stake
    
    elif strategy_type == 'trifecta_only':
        # Trifecta Only: $1 trifecta box
        tri_combos = combos_trifecta_boxed(horses)
        
        tri_unit = 1.00
        tri_stake = len(tri_combos) * tri_unit  # 6 * 1.00 = $6
        
        bets.append({
            'type': 'Trifecta Boxed',
            'unit': tri_unit,
            'num_combos': len(tri_combos),
            'stake': tri_stake,
            'flexi_pct': 1.0,
            'combos': tri_combos
        })
        
        total_stake = tri_stake
    
    elif strategy_type == 'quinella_only':
        # Quinella Only: $2 quinella box
        quin_combos = combos_quinella_boxed(horses)
        
        quin_unit = 2.00
        quin_stake = len(quin_combos) * quin_unit  # 3 * 2.00 = $6
        
        bets.append({
            'type': 'Quinella Boxed',
            'unit': quin_unit,
            'num_combos': len(quin_combos),
            'stake': quin_stake,
            'flexi_pct': 1.0,
            'combos': quin_combos
        })
        
        total_stake = quin_stake
    
    elif strategy_type == 'custom':
        # Custom strategy
        if not budget or budget <= 0:
            return {
                'error': 'Custom strategy requires a valid budget',
                'bets': [],
                'total_stake': 0
            }
        
        # User can specify how to split budget
        tri_percent = options.get('tri_percent', 0.4)  # 40% to trifecta
        quin_percent = options.get('quin_percent', 0.6)  # 60% to quinella
        
        tri_combos = combos_trifecta_boxed(horses)
        quin_combos = combos_quinella_boxed(horses)
        
        tri_stake = budget * tri_percent
        quin_stake = budget * quin_percent
        
        tri_full_cost = len(tri_combos) * 1.0
        tri_flexi = flexi_percentage(tri_stake, tri_full_cost)
        
        quin_full_cost = len(quin_combos) * 1.0
        quin_flexi = flexi_percentage(quin_stake, quin_full_cost)
        
        bets.append({
            'type': 'Trifecta Boxed (Flexi)',
            'unit': 1.0,
            'num_combos': len(tri_combos),
            'stake': tri_stake,
            'flexi_pct': tri_flexi,
            'combos': tri_combos
        })
        
        bets.append({
            'type': 'Quinella Boxed (Flexi)',
            'unit': 1.0,
            'num_combos': len(quin_combos),
            'stake': quin_stake,
            'flexi_pct': quin_flexi,
            'combos': quin_combos
        })
        
        total_stake = tri_stake + quin_stake
    
    else:
        return {
            'error': f'Unknown strategy type: {strategy_type}',
            'bets': [],
            'total_stake': 0
        }
    
    return {
        'bets': bets,
        'total_stake': round(total_stake, 2),
        'selections': horses,
        'strategy': strategy_type
    }


def estimate_dividends_from_odds(odds_a, odds_b, odds_c, takeout=0.20):
    """
    Estimate trifecta and quinella dividends from fixed odds.
    
    Formula (rough approximation):
    - Trifecta: (odds_1st * odds_2nd * odds_3rd) * (1 - takeout) * base_unit
    - Quinella: sqrt(odds_1st * odds_2nd) * (1 - takeout) * multiplier
    
    Args:
        odds_a, odds_b, odds_c: Decimal odds for each horse
        takeout: House edge (typically 15-25% for exotics, default 20%)
        
    Returns:
        dict: Estimated dividends for trifecta and quinella
    """
    if not all([odds_a, odds_b, odds_c]):
        return {'trifecta': 0, 'quinella': 0, 'error': 'Missing odds'}
    
    # Trifecta: multiply all three odds and reduce for takeout
    # The order matters in trifecta, so we use the exact sequence
    trifecta_base = odds_a * odds_b * odds_c
    trifecta_dividend = trifecta_base * (1 - takeout)
    
    # Quinella: any two horses in top 2 (order doesn't matter)
    # Average the pairwise products
    quinella_base = ((odds_a * odds_b) + (odds_a * odds_c) + (odds_b * odds_c)) / 3
    quinella_dividend = quinella_base * (1 - takeout) * 0.5  # Quinella pays less than exacta
    
    return {
        'trifecta': round(trifecta_dividend, 2),
        'quinella': round(quinella_dividend, 2)
    }


def estimate_returns(bets, dividends):
    """
    Estimate returns based on dividends.
    
    Args:
        bets: List of bets from apply_strategy
        dividends: dict with 'trifecta' and/or 'quinella' dividends
        
    Returns:
        dict: Estimated returns
    """
    returns = {
        'trifecta_return': 0,
        'quinella_return': 0,
        'total_return': 0
    }
    
    for bet in bets:
        bet_type = bet['type'].lower()
        flexi = bet.get('flexi_pct', 1.0)
        stake = bet.get('stake', 0)
        
        if 'trifecta' in bet_type and dividends.get('trifecta'):
            # For trifecta: dividend * flexi_pct (returns per $1 bet)
            returns['trifecta_return'] = dividends['trifecta'] * flexi
        
        if 'quinella' in bet_type and dividends.get('quinella'):
            # For quinella: dividend * flexi_pct
            returns['quinella_return'] = dividends['quinella'] * flexi
    
    returns['total_return'] = returns['trifecta_return'] + returns['quinella_return']
    
    return returns


def get_tab_instructions(strategy_type, horses):
    """
    Generate TAB-ready betting instructions.
    
    Args:
        strategy_type: The strategy being used
        horses: List of 3 horse names [A, B, C]
        
    Returns:
        str: Instructions for placing bets at TAB
    """
    instructions = []
    
    if strategy_type == 'budget_6':
        instructions.append("Trifecta Box: {}, {}, {} - $0.50 unit (Total: $3.00)".format(horses[0], horses[1], horses[2]))
        instructions.append("Quinella Box: {}, {}, {} - $1.00 unit (Total: $3.00)".format(horses[0], horses[1], horses[2]))
    
    elif strategy_type == 'budget_5':
        instructions.append("Trifecta Box: {}, {}, {} - $2.00 Flexi 33% (Total: $2.00)".format(horses[0], horses[1], horses[2]))
        instructions.append("Quinella Box: {}, {}, {} - $1.00 unit (Total: $3.00)".format(horses[0], horses[1], horses[2]))
    
    elif strategy_type == 'budget_10':
        instructions.append("Trifecta Box: {}, {}, {} - $1.00 unit (Total: $6.00)".format(horses[0], horses[1], horses[2]))
        instructions.append("Quinella Box: {}, {}, {} - $1.33 unit (Total: $4.00)".format(horses[0], horses[1], horses[2]))
    
    elif strategy_type == 'budget_15':
        instructions.append("Trifecta Box: {}, {}, {} - $1.50 unit (Total: $9.00)".format(horses[0], horses[1], horses[2]))
        instructions.append("Quinella Box: {}, {}, {} - $2.00 unit (Total: $6.00)".format(horses[0], horses[1], horses[2]))
    
    elif strategy_type == 'trifecta_only':
        instructions.append("Trifecta Box: {}, {}, {} - $1.00 unit (Total: $6.00)".format(horses[0], horses[1], horses[2]))
    
    elif strategy_type == 'quinella_only':
        instructions.append("Quinella Box: {}, {}, {} - $2.00 unit (Total: $6.00)".format(horses[0], horses[1], horses[2]))
    
    return " | ".join(instructions)


def format_bet_breakdown(bets_result):
    """
    Format bet breakdown for display.
    
    Args:
        bets_result: Result from apply_strategy
        
    Returns:
        str: Formatted breakdown
    """
    if 'error' in bets_result:
        return bets_result['error']
    
    lines = []
    lines.append(f"Strategy: {bets_result['strategy']}")
    lines.append(f"Selections: {', '.join(bets_result['selections'])}")
    lines.append("")
    
    for bet in bets_result['bets']:
        lines.append(f"{bet['type']}:")
        lines.append(f"  Combinations: {bet['num_combos']}")
        lines.append(f"  Unit: {format_currency(bet['unit'])}")
        lines.append(f"  Stake: {format_currency(bet['stake'])}")
        if bet['flexi_pct'] < 1.0:
            lines.append(f"  Flexi: {bet['flexi_pct']*100:.1f}%")
        lines.append("")
    
    lines.append(f"Total Stake: {format_currency(bets_result['total_stake'])}")
    
    return "\n".join(lines)
