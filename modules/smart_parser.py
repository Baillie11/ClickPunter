"""
Smart parser with intelligent pattern recognition for racing data.
Handles messy Racing.com copy-paste with AI-like extraction.
"""
import re
from utils.odds_helpers import to_decimal


class SmartRacingParser:
    """Intelligent parser that extracts racing data from messy text."""
    
    def __init__(self):
        # Common patterns we look for
        self.horse_name_pattern = r'^(\d+)\.\s+(.+?)$'
        self.barrier_pattern = r'\((\d{1,2})\)'
        self.odds_pattern = r'(?:W|WIN)[\s\n]*\$?[\s\n]*(\d+\.?\d*)'
        self.jockey_pattern = r'J:?\s*([A-Z][A-Za-z.\']+(?:\s+[A-Z][A-Za-z.\']+)*)'
        self.trainer_pattern = r'T:?\s*([A-Z][A-Za-z.,&\'\s]+?)(?=\s+J:|$|\n)'
        
    def parse(self, text):
        """
        Intelligently parse racing data from any format.
        
        Args:
            text: Raw text from Racing.com or similar
            
        Returns:
            list: List of horse dicts
        """
        horses = []
        
        # Split into potential horse blocks
        # Look for lines starting with "number."
        blocks = self._split_into_blocks(text)
        
        for block in blocks:
            horse = self._extract_horse_data(block)
            if horse and horse.get('name') and horse.get('odds_decimal'):
                horses.append(horse)
        
        return horses
    
    def _split_into_blocks(self, text):
        """Split text into blocks, one per horse."""
        # Strategy: Find all lines that start with "number."
        # Then take everything until the next "number."
        
        lines = text.split('\n')
        blocks = []
        current_block = []
        
        for line in lines:
            # Check if this line starts a new horse
            if re.match(r'^\d+\.\s+\w', line.strip()):
                # Save previous block if it exists
                if current_block:
                    blocks.append('\n'.join(current_block))
                # Start new block
                current_block = [line]
            else:
                # Add to current block
                if current_block:
                    current_block.append(line)
        
        # Don't forget the last block
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def _extract_horse_data(self, block):
        """Extract horse data from a text block."""
        horse = {}
        
        # Extract horse name and number
        first_line = block.split('\n')[0]
        name_match = re.search(self.horse_name_pattern, first_line.strip(), re.MULTILINE)
        
        if name_match:
            horse_num = name_match.group(1)
            raw_name = name_match.group(2).strip()
            
            # Clean the name - remove anything in parentheses EXCEPT the barrier
            # Strategy: Extract barrier first, then remove all parentheses content
            barrier = self._extract_barrier(raw_name)
            if barrier:
                horse['barrier'] = barrier
            
            # Now clean the name
            cleaned_name = raw_name
            # Remove country codes like (NZ), (IRE), (AUS)
            cleaned_name = re.sub(r'\s*\([A-Z]{2,3}\)\s*', ' ', cleaned_name)
            # Remove barrier number
            cleaned_name = re.sub(r'\s*\(\d{1,2}\)\s*', ' ', cleaned_name)
            # Clean up extra spaces
            cleaned_name = ' '.join(cleaned_name.split())
            
            horse['name'] = cleaned_name
        else:
            return None
        
        # Extract odds (WIN odds)
        odds = self._extract_odds(block)
        if odds:
            horse['odds_decimal'] = odds
        
        # Extract jockey
        jockey = self._extract_jockey(block)
        if jockey:
            horse['jockey'] = jockey
        
        # Extract trainer
        trainer = self._extract_trainer(block)
        if trainer:
            horse['trainer'] = trainer
        
        # Extract form
        form = self._extract_form(block)
        if form:
            horse['last3_form'] = form
        
        # Extract speed indicators
        horse['speed_map_hint'] = self._extract_speed_hint(block)
        
        # Defaults
        horse.setdefault('track_pref', '')
        horse.setdefault('distance_pref', '')
        horse.setdefault('market_open_odds', None)
        horse.setdefault('market_current_odds', None)
        horse.setdefault('is_scratched', False)
        
        return horse
    
    def _extract_barrier(self, text):
        """Extract barrier number."""
        # Look for the LAST number in parentheses (that's usually the barrier)
        matches = re.findall(r'\((\d{1,2})\)', text)
        if matches:
            # Return the last match (barrier is usually last)
            return int(matches[-1])
        return None
    
    def _extract_odds(self, block):
        """Extract WIN odds intelligently."""
        # Look for "W" or "WIN" followed by a price
        # Handle various formats: "W $9.50", "W$9.50", "W\n$9.50", "W\n9.50"
        
        # Strategy 1: Look for W/WIN near a dollar amount
        odds_match = re.search(r'(?:W|WIN)[\s\n]*\$?[\s\n]*(\d+\.?\d*)', block, re.IGNORECASE)
        if odds_match:
            return to_decimal(odds_match.group(1))
        
        # Strategy 2: Look for FAVOURITE or MOVER lines (odds usually nearby)
        if 'FAVOURITE' in block or 'MOVER' in block:
            # Find any dollar amount near these keywords
            context = block[block.find('FAVOURITE') if 'FAVOURITE' in block else block.find('MOVER'):]
            price_match = re.search(r'\$(\d+\.?\d*)', context[:100])
            if price_match:
                return to_decimal(price_match.group(1))
        
        # Strategy 3: Just find ANY dollar amount that looks like odds ($2.00 - $999.00)
        price_matches = re.findall(r'\$(\d+\.?\d*)', block)
        for price in price_matches:
            price_val = float(price)
            if 1.00 <= price_val <= 999.00:  # Valid odds range
                return price_val
        
        return None
    
    def _extract_jockey(self, block):
        """Extract jockey name."""
        # Look for "J:" or "J " followed by a name
        jockey_match = re.search(r'J:?\s*([A-Z][A-Za-z.\']+(?:\s+[A-Z][A-Za-z.\']+)?)', block)
        if jockey_match:
            return jockey_match.group(1).strip()
        return ''
    
    def _extract_trainer(self, block):
        """Extract trainer name."""
        # Look for "T:" followed by a name (can have multiple words, &, commas)
        trainer_match = re.search(r'T:?\s*([A-Z][A-Za-z.,&\'\s]+?)(?=\s+J:|$|\n\d|\n[A-Z]:)', block)
        if trainer_match:
            trainer = trainer_match.group(1).strip()
            # Clean up - remove trailing punctuation
            trainer = re.sub(r'[\s,]+$', '', trainer)
            return trainer
        return ''
    
    def _extract_form(self, block):
        """Extract recent form."""
        # Look for "First Start" explicitly
        if 'First Start' in block:
            return 'First Start'
        
        # Look for form patterns like "2-843", "122-6", "31553"
        # Usually appears after jockey/trainer info
        form_patterns = [
            r'(?:^|\n)([0-9xX\-]{3,10})(?:\s+\d+:|$|\n)',  # Form with dashes or just digits
            r'([0-9xX]{3,6})',  # Simple form string
        ]
        
        for pattern in form_patterns:
            form_match = re.search(pattern, block)
            if form_match:
                form = form_match.group(1)
                # Filter out things that are clearly not form (like dates, weights)
                if not re.match(r'^\d{1,2}[\./]\d', form):  # Not a date
                    return form
        
        return ''
    
    def _extract_speed_hint(self, block):
        """Extract speed map hints from keywords."""
        block_upper = block.upper()
        
        if 'FAVOURITE' in block_upper:
            return 'leaders'
        elif 'MOVER' in block_upper:
            return 'on-pace'
        elif 'LEADER' in block_upper:
            return 'leaders'
        elif 'CLOSER' in block_upper or 'BACKMARKER' in block_upper:
            return 'back'
        
        return ''


# Global instance
smart_parser = SmartRacingParser()


def smart_parse(text):
    """
    Parse racing data using the smart parser.
    
    Args:
        text: Raw racing text
        
    Returns:
        list: List of horse dicts
    """
    return smart_parser.parse(text)
