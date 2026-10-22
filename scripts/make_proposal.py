"""Build a PROPOSAL copy of the coding that follows the official EI 2.0 'Five Core Feelings' table exactly.
Writes offlimits_data_proposal.py; the live coding (offlimits_data.py) is not touched."""
import sys

src, dst = sys.argv[1], sys.argv[2]
c = open(src, encoding='utf-8').read().replace('\r\n', '\n')

def swap(old, new):
    global c
    if old not in c:
        raise SystemExit('missing: ' + old[:90])
    c = c.replace(old, new, 1)

# intensity levels that differ from the official table
swap("('Annoyance',     'Angry',   'Medium',", "('Annoyance',     'Angry',   'Low',   ")      # Annoyed = Angry LOW
swap("('Anxiety',       'Afraid',  'Medium',", "('Anxiety',       'Afraid',  'Low',   ")      # Anxious = Afraid LOW
swap("('Embarrassment', 'Ashamed', 'Low',   ", "('Embarrassment', 'Ashamed', 'Medium',")      # Embarrassed = Ashamed MEDIUM
swap("('Regret',        'Ashamed', 'Medium',", "('Regret',        'Ashamed', 'Low',   ")      # Regretful = Ashamed LOW
swap("('Scared',        'Afraid',  'Medium', r'\\b(scared|frighten)'),",
     "('Scared',        'Afraid',  'High',   r'\\bscared'),\n    ('Frightened',    'Afraid',  'Medium', r'\\bfrighten'),")  # Scared stiff HIGH, Frightened MEDIUM
# words in the table that were missing from the dictionary
swap("    # Afraid\n", """    ('Betrayed',      'Angry',   'High',   r'\\bbetray'),
    ('Boiling',       'Angry',   'High',   r'\\bboiling'),
    ('Defended',      'Angry',   'Medium', r'\\bdefensive|\\bdefended'),
    ('Perturbed',     'Angry',   'Low',    r'\\bperturb'),
    ('Uptight',       'Angry',   'Low',    r'\\buptight'),
    ('Touchy',        'Angry',   'Low',    r'\\btouchy'),
    # Afraid
    ('Shocked',       'Afraid',  'High',   r'\\bshock'),
    ('Frantic',       'Afraid',  'High',   r'\\bfrantic'),
    ('Apprehension',  'Afraid',  'Medium', r'\\bapprehens'),
    ('Intimidated',   'Afraid',  'Medium', r'\\bintimidat'),
    ('Caution',       'Afraid',  'Low',    r'\\bcautio'),
    ('Timidity',      'Afraid',  'Low',    r'\\btimid'),
""")
swap("    # Sad\n", """    # Sad
    ('Misery',        'Sad',     'High',   r'\\bmiser'),
    ('Dejection',     'Sad',     'High',   r'\\bdejected'),
    ('Agony',         'Sad',     'High',   r'\\bagoni'),
    ('Somberness',    'Sad',     'Medium', r'\\bsomber'),
    ('Moodiness',     'Sad',     'Low',    r'\\bmood(y|iness)'),
    ('Dissatisfaction','Sad',    'Low',    r'\\bdissatisf'),
""")
swap("    # Ashamed\n", """    # Ashamed
    ('Dishonored',    'Ashamed', 'High',   r'\\b(dishonor|defamed|admonish)'),
    ('Apologetic',    'Ashamed', 'Medium', r'\\bapolog'),
    ('Unworthiness',  'Ashamed', 'Medium', r'\\bunworth'),
    ('Secretive',     'Ashamed', 'Medium', r'\\b(secretive|sneaky)'),
    ('Silliness',     'Ashamed', 'Low',    r'\\b(silly|ridiculous|pitied|bashful)'),
""")
swap("    # Happy\n", """    # Happy
    ('Passion',       'Happy',   'High',   r'\\bpassion'),
    ('Satisfaction',  'Happy',   'Medium', r'\\b(satisf|gratif|relieved|glowing)'),
    ('Tenderness',    'Happy',   'Low',    r'\\b(tender|mellow)\\b'),
""")
# obvious misspellings seen in the review list
swap("r'\\banxi'),", "r'\\b(anxi|aniex|anxei)'),")
swap("r'\\b(anger|angry|angered|ander)\\b'),", "r'\\b(anger|angry|angered|ander|ager)\\b'),")
swap("(vulnerab|valunerab|vunverab|vulnerb)", "(vulnerab|valunerab|vunverab|vulnerb|volunerab)")
open(dst, 'w', encoding='utf-8').write(c)
print('ok')
