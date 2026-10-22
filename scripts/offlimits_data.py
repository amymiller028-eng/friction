"""Code Q6 ("which emotion feels most off-limits at work") into the five EI 2.0 core emotions
and intensity levels, and export the knowledge-graph data as JSON."""
import json
import re
import sys
import warnings
import pandas as pd
from scipy.stats import chi2_contingency

warnings.filterwarnings('ignore', message='This pattern is interpreted')
SRC, OUT = sys.argv[1], sys.argv[2]

# One node per emotion people actually named (never merged with "&"), placed under its core emotion and
# intensity from the feeling-words table (Quick Book version on file). Behaviors such as crying are not emotions.
WORDS = [
    # Angry
    ('Rage',          'Angry',   'High',   r'\b(rage|raging|enraged)\b'),
    ('Fury',          'Angry',   'High',   r'\b(fury|furious|irate|seething)'),
    ('Outrage',       'Angry',   'High',   r'\boutrage'),
    ('Hostility',     'Angry',   'High',   r'\bhostil'),
    ('Hate',          'Angry',   'High',   r'\b(hate|hatred|loath)'),
    ('Aggravation',   'Angry',   'High',   r'\baggravat'),
    ('Anger',         'Angry',   'Medium', r'\b(anger|angry|angered|ander|ager)\b'),
    ('Mad',           'Angry',   'Medium', r'\bmad\b'),
    ('Upset',         'Angry',   'Medium', r'\bupset'),
    ('Annoyance',     'Angry',   'Low',    r'\bannoy'),
    ('Frustration',   'Angry',   'Medium', r'\bfrustrat'),
    ('Agitation',     'Angry',   'Medium', r'\bagitat'),
    ('Disgust',       'Angry',   'Medium', r'\bdisgust'),
    ('Disdain',       'Angry',   'Medium', r'\bdisdain'),
    ('Contempt',      'Angry',   'Medium', r'\bcontempt'),
    ('Resentment',    'Angry',   'Medium', r'\bresent'),
    ('Offended',      'Angry',   'Medium', r'\boffen'),
    ('Bitterness',    'Angry',   'Medium', r'\bbitter'),
    ('Irritation',    'Angry',   'Low',    r'\birritat'),
    ('Grumpiness',    'Angry',   'Low',    r'\bgrump'),
    ('Impatience',    'Angry',   'Low',    r'\bimpatien'),
    ('Betrayed',      'Angry',   'High',   r'\bbetray'),
    ('Boiling',       'Angry',   'High',   r'\bboiling'),
    ('Defended',      'Angry',   'Medium', r'\bdefensive|\bdefended'),
    ('Perturbed',     'Angry',   'Low',    r'\bperturb'),
    ('Uptight',       'Angry',   'Low',    r'\buptight'),
    ('Touchy',        'Angry',   'Low',    r'\btouchy'),
    # Afraid
    ('Shocked',       'Afraid',  'High',   r'\bshock'),
    ('Frantic',       'Afraid',  'High',   r'\bfrantic'),
    ('Apprehension',  'Afraid',  'Medium', r'\bapprehens'),
    ('Intimidated',   'Afraid',  'Medium', r'\bintimidat'),
    ('Caution',       'Afraid',  'Low',    r'\bcautio'),
    ('Timidity',      'Afraid',  'Low',    r'\btimid'),
    ('Fear',          'Afraid',  'High',   r'\b(fear|fearful|afraid)'),
    ('Terror',        'Afraid',  'High',   r'\b(terrif|terror)'),
    ('Panic',         'Afraid',  'High',   r'\bpanic'),
    ('Horror',        'Afraid',  'High',   r'\bhorrif'),
    ('Scared',        'Afraid',  'High',   r'\bscared'),
    ('Frightened',    'Afraid',  'Medium', r'\bfrighten'),
    ('Anxiety',       'Afraid',  'Low',    r'\b(anxi|aniex|anxei)'),
    ('Insecurity',    'Afraid',  'Medium', r'\binsecur'),
    ('Threatened',    'Afraid',  'Medium', r'\bthreaten'),
    ('Uneasiness',    'Afraid',  'Medium', r'\buneas'),
    ('Overwhelm',     'Afraid',  'Medium', r'\boverwhelm'),
    ('Vulnerability', 'Afraid',  'Medium', r'(?<![a-z])(vulnerab|valunerab|vunverab|vulnerb|volunerab)'),
    ('Weakness',      'Afraid',  'Medium', r'\bweak'),
    ('Helplessness',  'Afraid',  'Medium', r'\bhelpless'),
    ('Nervousness',   'Afraid',  'Low',    r'\b(nervous|nrevous)'),
    ('Worry',         'Afraid',  'Low',    r'\bworr'),
    ('Stress',        'Afraid',  'Low',    r'\bstress'),
    ('Uncertainty',   'Afraid',  'Low',    r'\b(unsure|uncertain)'),
    ('Doubt',         'Afraid',  'Low',    r'\bdoubt'),
    ('Confusion',     'Afraid',  'Low',    r'\bconfus'),
    # Sad
    ('Misery',        'Sad',     'High',   r'\bmiser'),
    ('Dejection',     'Sad',     'High',   r'\bdejected'),
    ('Agony',         'Sad',     'High',   r'\bagoni'),
    ('Somberness',    'Sad',     'Medium', r'\bsomber'),
    ('Moodiness',     'Sad',     'Low',    r'\bmood(y|iness)'),
    ('Dissatisfaction','Sad',    'Low',    r'\bdissatisf'),
    ('Depression',    'Sad',     'High',   r'\bdepress'),
    ('Grief',         'Sad',     'High',   r'\b(grief|griev|mourn)'),
    ('Devastation',   'Sad',     'High',   r'\bdevastat'),
    ('Hopelessness',  'Sad',     'High',   r'\b(hopeless|despair)'),
    ('Hurt',          'Sad',     'High',   r'\bhurt'),
    ('Loneliness',    'Sad',     'High',   r'\blonel'),
    ('Sadness',       'Sad',     'Medium', r'\b(sad|sadness|sorrow|cry|crying|cried|tears|weep)'),  # crying is a behavior; it counts as sadness
    ('Heartbreak',    'Sad',     'Medium', r'\bheartbr'),
    ('Distress',      'Sad',     'Medium', r'\bdistress'),
    ('Melancholy',    'Sad',     'Medium', r'\bmelanchol'),
    ('Unhappiness',   'Sad',     'Low',    r'\bunhapp'),
    ('Disappointment','Sad',     'Low',    r'\b(disappoint|let down)'),
    ('Discouragement','Sad',     'Low',    r'\bdiscourag'),
    # Ashamed
    ('Dishonored',    'Ashamed', 'High',   r'\b(dishonor|defamed|admonish)'),
    ('Apologetic',    'Ashamed', 'Medium', r'\bapolog'),
    ('Unworthiness',  'Ashamed', 'Medium', r'\bunworth'),
    ('Secretive',     'Ashamed', 'Medium', r'\b(secretive|sneaky)'),
    ('Silliness',     'Ashamed', 'Low',    r'\b(silly|ridiculous|pitied|bashful)'),
    ('Shame',         'Ashamed', 'High',   r'\b(shame|ashamed)'),
    ('Humiliation',   'Ashamed', 'High',   r'\bhumiliat'),
    ('Worthlessness', 'Ashamed', 'High',   r'\bworthless'),
    ('Remorse',       'Ashamed', 'High',   r'\bremorse'),
    ('Guilt',         'Ashamed', 'Medium', r'\bguilt'),
    ('Regret',        'Ashamed', 'Low',    r'\bregret'),
    ('Embarrassment', 'Ashamed', 'Medium', r'\bembarrass'),
    ('Awkwardness',   'Ashamed', 'Low',    r'\b(awkward|uncomfortable|self.conscious)'),
    ('Shyness',       'Ashamed', 'Low',    r'\bshy\b'),
    # Happy
    ('Passion',       'Happy',   'High',   r'\bpassion'),
    ('Satisfaction',  'Happy',   'Medium', r'\b(satisf|gratif|relieved|glowing)'),
    ('Tenderness',    'Happy',   'Low',    r'\b(tender|mellow)\b'),
    ('Excitement',    'Happy',   'High',   r'\b(excite|thrill)'),
    ('Elation',       'Happy',   'High',   r'\b(elat|overjoy|ecsta|euphor)'),
    ('Joy',           'Happy',   'Medium', r'\b(joy|joyful)\b'),
    ('Happiness',     'Happy',   'Medium', r'\bhapp'),
    ('Cheerfulness',  'Happy',   'Medium', r'\bcheer'),
    ('Gratitude',     'Happy',   'Medium', r'\b(grateful|gratitude)'),
    ('Hope',          'Happy',   'Medium', r'\b(hope|hopeful|optimis)\b'),
    ('Love',          'Happy',   'Medium', r'\b(lov(e|ing)|attraction|crush|flirt\w*|romance|romantic)\b'),  # attraction/flirting count as love (editor's call)
    ('Affection',     'Happy',   'Medium', r'\baffection'),
    ('Humor',         'Happy',   'Medium', r'\b(humor|laugh|fun)\b'),
    ('Pride',         'Happy',   'Medium', r'\b(pride|proud)\b'),
    ('Contentment',   'Happy',   'Low',    r'\b(content|contented|pleased|glad)\b'),
]
CORE_ORDER = ['Angry', 'Afraid', 'Sad', 'Ashamed', 'Happy']
NO_ANSWER = r"^\s*(none|nothing|no|na|n/?a|not sure|i don'?t know|idk|don'?t know|nope|never|unsure|no idea|none of them|all of them)\W*$"
PROFANE = re.compile(r'(shit|fuck|pussy|damn|bitch|\bass\b|dick|crap|mentally challenged|retard|crazy|psycho|incompetent)', re.I)
# answers kept in the counts but not shown as quotes, at the editor's request
HIDE = re.compile(r'^(relaxed because|joy, i like everything about it|it seems that i can not express joy|joy because its so relaxing|gratitude\.\.because|grief, because it puzzles|anxiety because of work\W?s? pressure)', re.I)
HIDE_CORE = re.compile(r'^(relaxed because|joy, i like everything about it)', re.I)  # core-emotion panels only

df = pd.read_excel(SRC).iloc[1:].copy()
text = df['Q6'].fillna('').astype(str).str.replace('ï¿½', "'").str.strip()
low = text.str.lower()
lead = df['Q23'].map({'Yes': 'Leaders', 'No': 'Non-leaders'})
gender = df['Q51'].map({'Female': 'Women', 'Male': 'Men'})
no_answer = low.eq('') | low.str.match(NO_ANSWER) | low.str.match(r"^\s*(i\W?m|i am)\s+(uncertain|unsure|not sure)\b") \
            | low.str.match(r"^\s*(nothing|none)\b")

# Code only the emotion the person NAMED, not words in their explanation
# ("Mostly joy because others are angry and bitter" is joy, not anger).
EXPLAIN = re.compile(r"[.!?;:—]|\s[-–]\s|\b(because|cause|cuz|bc|since|due to|as it|as they|as people|as you|so that|so i|so you|when|if)\b")
NONE_LEAD = re.compile(r"^\s*(none|nothing|no\b|not\b|n/?a|i don'?t|idk|never|all\b|any\b|every)")

any_rx = '|'.join(rx for _, _, _, rx in WORDS)
# a clause that describes an effect ("anger, it makes people uncomfortable", "sadness causes embarrassment"):
# cut there, but only once an emotion has already been named, so lists like "anger, resentment, sadness" stay whole
EFFECT = re.compile(r",\s*(it|it's|its|i|i'm|i've|they|you|we|people|nobody|no one|everyone|everybody|this|that|which|who|he|she|but"
                    r"|feared|seen|considered|viewed|perceived|misunderstood|mistaken|equated)\b"
                    r"|\s*[-\u2013\u2014]"
                    r"|\s(makes?|causes?|feels?|seems?|is|are|can|could|would|will|gets?|seen|considered|viewed|perceived|misunderstood|mistaken|feared)\b")

def named_part(s):
    m = EXPLAIN.search(s)
    s = s[:m.start()] if m and m.start() > 0 else s
    for e in EFFECT.finditer(s):
        if re.search(any_rx, s[:e.start()]):
            return s[:e.start()]
    return s

lead_txt = low.map(named_part)
lead_has = lead_txt.str.contains(any_rx, regex=True)
# if the named part has no emotion word (e.g. "In my workplace it's the feeling of ..."), fall back to the whole
# answer, unless the person led with "none" / "not" / "I don't"
code_txt = lead_txt.where(lead_has | lead_txt.str.match(NONE_LEAD), low)
# answers read by hand and set aside: an insult rather than an emotion (shown in the sheet as 'Reviewed by hand')
MANUAL_EXCLUDE = low.str.startswith('being a millennial')
no_answer = no_answer | MANUAL_EXCLUDE
hits = {w: code_txt.str.contains(rx, regex=True) & ~no_answer for w, _, _, rx in WORDS}
hits['Weakness'] = hits['Weakness'] & lead_txt.str.contains(r'\bweak', regex=True)
# "upset" and "weak" are ambiguous; only count them when nothing more specific matched in that core
core_hit = {c: pd.concat([hits[w] for w, cc, _, _ in WORDS if cc == c], axis=1).any(axis=1) for c in CORE_ORDER}
named = pd.concat(list(core_hit.values()), axis=1).any(axis=1)
N_ALL, N_NAMED = len(df), int(named.sum())

def share(mask, base):
    return round(100 * (mask & base).sum() / max(base.sum(), 1), 3)  # keep precision; round only for display

def split(mask):
    out = {}
    for label, grp in [('Leaders', lead == 'Leaders'), ('Non-leaders', lead == 'Non-leaders'),
                       ('Women', gender == 'Women'), ('Men', gender == 'Men')]:
        out[label] = share(mask, named & grp)
    def p(a, b):
        tab = [[(mask & named & a).sum(), (~mask & named & a).sum()], [(mask & named & b).sum(), (~mask & named & b).sum()]]
        return float(chi2_contingency(tab)[1]) if min(sum(tab[0]), sum(tab[1])) else 1.0
    out['p_role'] = p(lead == 'Non-leaders', lead == 'Leaders')
    out['p_gender'] = p(gender == 'Women', gender == 'Men')
    return out

USED = set()  # a quote appears under one specific emotion only

def quotes(mask, k=3, unique=False, hide=HIDE):
    shown = text[mask][~text[mask].str.match(hide)]
    pool = [t for t in shown if 30 <= len(t) <= 150 and not PROFANE.search(t) and re.search(r'\b(because|since|as|it|so)\b', t, re.I)]
    pool += [t for t in shown if 30 <= len(t) <= 150 and not PROFANE.search(t) and t not in pool]
    seen, out = set(), []
    for t in pool:
        key = t.lower()[:40]
        if key not in seen and not (unique and key in USED):
            seen.add(key); out.append(t[0].upper() + t[1:])
            if unique:
                USED.add(key)
        if len(out) == k:
            break
    return out

# hand out specific-emotion quotes smallest group first, so a shared answer stays with the rarer emotion
WORD_QUOTES = {w: quotes(hits[w], unique=True) for w, _, _, _ in sorted(WORDS, key=lambda x: hits[x[0]].sum())}
WORD_QUOTES['Joy'] = []         # editor's call: no joy quotes
WORD_QUOTES['Excitement'] = []  # editor's call: no excitement quotes
def pick(*starts):
    """Exact answers (by their opening words) chosen by the editor."""
    out = []
    for s in starts:
        m = text[text.str.lower().str.replace('\u2019', "'").str.startswith(s.lower())]
        if len(m):
            out.append(m.iloc[0][0].upper() + m.iloc[0][1:])
    return out

WORD_QUOTES['Happiness'] = pick('Happiness. The people around me hate to see me smiling')
HAPPY_PANEL = pick('Happiness. The people around me hate to see me smiling',
                   "Joy. Because there is not much place to be happy about")
for w, core, _, _ in WORDS:      # editor's call: no usable quotes for ashamed
    if core == 'Ashamed':
        WORD_QUOTES[w] = []

data = {'n_all': N_ALL, 'n_named': N_NAMED, 'n_no_answer': int(no_answer.sum()),
        'n_other': int((~named & ~no_answer).sum()), 'cores': []}
for c in CORE_ORDER:
    m = core_hit[c]
    words = []
    for w, cc, inten, _ in WORDS:
        if cc != c or hits[w].sum() == 0:
            continue
        words.append({'name': w, 'intensity': inten, 'n': int(hits[w].sum()), 'pct': share(hits[w], named),
                      'quotes': WORD_QUOTES[w]})
    inten = {lvl: share(pd.concat([hits[w] for w, cc, il, _ in WORDS if cc == c and il == lvl] or [pd.Series(False, index=df.index)], axis=1).any(axis=1), named)
             for lvl in ['High', 'Medium', 'Low']}
    data['cores'].append({'name': c, 'n': int(m.sum()), 'pct': share(m, named), 'pct_all': share(m, pd.Series(True, index=df.index)),
                          'split': split(m), 'intensity': inten, 'words': words,
                          # core panels reuse only the approved quotes from their own bubbles, biggest bubble first
                          'quotes': HAPPY_PANEL if c == 'Happy' else [q for w in sorted(words, key=lambda w: -w['n']) for q in w['quotes'] if not HIDE_CORE.match(q)][:3]})

# who didn't name one of the five, for the note under the graph
lo = low.str.replace('\u2019', "'")
says_none = ~named & (lo.str.match(r"^\s*(none|nothing|no\b|nope)") | lo.str.contains(
    r"\b(no emotion|none (are|is|feel)|not any|any emotion is|all emotions are (ok|fine|accepted)|don'?t (feel|have) any|"
    r"no (emotions? )?(is |are )?off.?limits?)"))
OUTSIDE = [('lust', r'\b(lust|sexual)\b'), ('curiosity', r'\bcurios'), ('wonder', r'\bwonder\b'), ('sarcasm', r'\bsarcas'),
           ('zest', r'\b(zest|zeal)'), ('indecisiveness', r'\bindecisiv'), ('feeling unappreciated', r'\bunappreciat')]
outside = {name: int((~named & ~says_none & lo.str.contains(rx, regex=True)).sum()) for name, rx in OUTSIDE}
multi = pd.concat([core_hit[c_] for c_ in CORE_ORDER], axis=1).sum(axis=1) > 1
data.update({'n_says_none': int(says_none.sum()), 'n_outside': int(sum(outside.values())),
             'outside': sorted([(k, v) for k, v in outside.items() if v], key=lambda kv: -kv[1]),
             'n_multi': int((multi & named).sum())})
open(OUT, 'w', encoding='utf-8').write(json.dumps(data, indent=1, ensure_ascii=False))
print(f'all {N_ALL}, named an emotion {N_NAMED}, no answer {int(no_answer.sum())}, other {data["n_other"]}')
for c in data['cores']:
    s = c['split']
    print(f"{c['name']:<8} {c['pct']:>5}% of namers ({c['n']}) | lead {s['Leaders']} non {s['Non-leaders']} p={s['p_role']:.4f} | "
          f"women {s['Women']} men {s['Men']} p={s['p_gender']:.4f} | " + ', '.join(f"{w['name']} {w['n']}" for w in c['words']))
print('\nunmatched sample:', [t for t in text[~named & ~no_answer].head(25)])

# exact figures quoted in the essay
vf = (hits['Vulnerability'] | hits['Fear'])
def ex(mask, grp): return 100 * (mask & named & grp).sum() / (named & grp).sum()
A = core_hit['Angry']
print('EXACT anger: all %.3f | non-leaders %.3f leaders %.3f | women %.3f men %.3f' % (
    100 * (A & named).sum() / named.sum(), ex(A, lead == 'Non-leaders'), ex(A, lead == 'Leaders'), ex(A, gender == 'Women'), ex(A, gender == 'Men')))
print('EXACT vulnerability-or-fear: women %.2f men %.2f ratio %.2f | afraid core ratio %.2f' % (
    ex(vf, gender == 'Women'), ex(vf, gender == 'Men'), ex(vf, gender == 'Men') / ex(vf, gender == 'Women'),
    ex(core_hit['Afraid'], gender == 'Men') / ex(core_hit['Afraid'], gender == 'Women')))

# row-by-row coding, for the "anger-at-work" sheet
rows = pd.DataFrame({
    'ResponseId': df['ResponseId'], 'Leader role': lead, 'Gender': df['Q51'], 'Answer (Q6)': text,
    'Part coded': code_txt.where(~no_answer, ''),
    'Named an emotion': named.map({True: 'Yes', False: 'No'}),
})
for c in CORE_ORDER:
    rows[c] = core_hit[c].astype(int)
rows['Specific emotions'] = [', '.join(w for w, _, _, _ in WORDS if hits[w].loc[i]) for i in df.index]
rows['Intensity'] = [', '.join(sorted({il for w, _, il, _ in WORDS if hits[w].loc[i]}, key=['High', 'Medium', 'Low'].index)) for i in df.index]
rows['Why not counted'] = ['' if named.loc[i] else ('Reviewed by hand: an insult, not an emotion' if MANUAL_EXCLUDE.loc[i] else 'No answer / none' if no_answer.loc[i] else 'No core emotion named') for i in df.index]
rows.to_pickle(OUT.replace('.json', '_rows.pkl'))
pd.to_pickle({'WORDS': WORDS, 'CORE_ORDER': CORE_ORDER}, OUT.replace('.json', '_dict.pkl'))
