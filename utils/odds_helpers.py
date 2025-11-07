"""
Utility functions for handling odds and betting calculations.
"""
import re


def to_decimal(odds):
    """
    Convert odds to decimal format.
    
    Supports:
    - Decimal: 3.50, $3.50
    - Fractional: 5/2, 7/1
    - String numbers: "3.50"
    
    Args:
        odds: Odds in various formats
        
    Returns:
        float: Decimal odds, or None if invalid
    """
    if odds is None:
        return None
    
    # Already a number
    if isinstance(odds, (int, float)):
        return float(odds)
    
    # String processing
    odds_str = str(odds).strip()
    
    # Remove dollar sign
    odds_str = odds_str.replace('$', '').strip()
    
    # Try decimal
    try:
        return float(odds_str)
    except ValueError:
        pass
    
    # Try fractional (e.g., "5/2")
    if '/' in odds_str:
        try:
            parts = odds_str.split('/')
            if len(parts) == 2:
                numerator = float(parts[0].strip())
                denominator = float(parts[1].strip())
                if denominator != 0:
                    return (numerator / denominator) + 1.0
        except (ValueError, ZeroDivisionError):
            pass
    
    return None


def within_band(value, low, high):
    """
    Check if a value is within a range (inclusive).
    
    Args:
        value: Value to check
        low: Lower bound
        high: Upper bound
        
    Returns:
        bool: True if value is in [low, high]
    """
    if value is None:
        return False
    return low <= value <= high


def format_currency(value):
    """
    Format a number as currency.
    
    Args:
        value: Numeric value
        
    Returns:
        str: Formatted currency string (e.g., "$5.00")
    """
    if value is None:
        return "$0.00"
    return f"${value:.2f}"


def flexi_percentage(stake, total_cost):
    """
    Calculate flexi bet percentage.
    
    Args:
        stake: Amount staked
        total_cost: Total cost of the bet at full unit
        
    Returns:
        float: Percentage as decimal (0.0 to 1.0)
    """
    if total_cost <= 0:
        return 0.0
    return min(stake / total_cost, 1.0)


def format_odds(odds):
    """
    Format odds for display.
    
    Args:
        odds: Decimal odds
        
    Returns:
        str: Formatted odds (e.g., "$3.50")
    """
    if odds is None:
        return "N/A"
    return f"${odds:.2f}"
