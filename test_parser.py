from modules.smart_parser import smart_parse

test_data = """1. Liberami (NZ) (6)
T: 
R.D.Griffiths
  J: 
L.Nolen
2-843
20: 4-6-2
60kg
W
$9.50
P
$2.75

2. Sabaj (13)
T: 
Mick Price & Michael Kent (Jnr)
  J: 
M.Zahra
122-6
FAVOURITE
W
$2.70"""

print("Testing smart parser...")
horses = smart_parse(test_data)
print(f'\nFound {len(horses)} horses:')
for h in horses:
    print(f"  {h.get('name')}: Barrier {h.get('barrier')}, Odds ${h.get('odds_decimal')}, Form: {h.get('last3_form')}")
