"""Item-by-item findings for the friction-page survey -> full Word report + one-page summary.
Q6 (off-limits emotion) uses the EI 2.0 coding exported by offlimits_data.py (see the 'anger-at-work' sheet)."""
import json
import re
import sys
import warnings
import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Inches

warnings.filterwarnings('ignore', message='This pattern is interpreted as a regular expression')
SRC, FULL, SHORT, OFFLIMITS = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
NAVY = RGBColor(0x00, 0x2D, 0x61)
GREY = RGBColor(0x55, 0x66, 0x77)


def fix(s):
    s = str(s).replace('�', "'")
    s = re.sub(r"\s'\s", ' — ', s).replace(' - Selected Choice', '')
    return re.sub(r'^\d+\.\s*', '', s.strip())


raw = pd.read_excel(SRC, sheet_name='Sheet1')
QTEXT = {c: fix(raw.iloc[0][c]) for c in raw.columns}
df = raw.iloc[1:].copy()
for c in df.columns:
    if df[c].dtype == object:
        df[c] = df[c].map(lambda v: fix(v) if isinstance(v, str) else v)
N = len(df)
recap = pd.to_numeric(df['Q_RecaptchaScore'], errors='coerce')
start = pd.to_datetime(df['StartDate'])
OFF = json.load(open(OFFLIMITS, encoding='utf-8'))
CORES = {c['name']: c for c in OFF['cores']}

AGREE = ['Strongly disagree', 'Somewhat disagree', 'Neither agree nor disagree', 'Somewhat agree', 'Strongly agree']
AMOUNT = ['Not at all', 'A little', 'A moderate amount', 'A lot', 'A great deal']
CHANGE = ['None at all', 'A little', 'A moderate amount', 'A lot', 'A great deal']
CONF = ['Not at all confident', 'Slightly confident', 'Moderately confident', 'Very confident', 'Extremely confident']
FREQ = ['Never', 'Sometimes', 'About half the time', 'Most of the time', 'Always']
BEHAV = ['Never', 'Rarely', 'Sometimes', 'Usually', 'Almost Always', 'Always']
OFTEN = ['Never', 'Rarely', 'Sometimes', 'Often', 'Very Often']
IMPORT = ['Not at all important', 'Slightly important', 'Moderately important', 'Very important', 'Extremely important']
LIKELY = ['Definitely not', 'Probably not', 'Might or might not', 'Probably yes', 'Definitely yes']
INTENSE = ['Much less intense', 'Somewhat less intense', 'About the same', 'Somewhat more intense', 'Much more intense']
PRIORITY = ['Always results first', 'Usually results first', 'An equal balance between results and relationships',
            'Usually relationships first', 'Always relationships first']
KNOW = ["I've never heard of it", "I've heard of it but don't know much", 'I have a general understanding',
        'I have a good understanding and could explain it to others',
        'I have advanced knowledge (e.g., training, teaching, or research experience)']
EDU = ['Some high school or less', 'High school diploma or GED', 'Some college, but no degree',
       'Associates or technical degree', "Bachelor's degree",
       'Graduate or professional degree (MA, MS, MBA, PhD, JD, MD, DDS etc.)', 'Prefer not to say']
INCOME = ['Less than $25,000', '$25,000-$49,999', '$50,000-$74,999', '$75,000-$99,999', '$100,000-$149,999',
          '$150,000 or more', 'Prefer not to say']
LEVEL = ['Individual Contributor (no formal leadership role)', 'Frontline Supervisor', 'Mid-level Manager',
         'Senior Manager', 'Executive']


def pct(x):
    return f'{x:.0f}%'


def dist(col, order=None):
    s = df[col].dropna()
    s = s[s.astype(str).str.strip() != '']
    vc = s.value_counts()
    if order:
        vc = vc.reindex([o for o in order if o in vc.index] + [i for i in vc.index if i not in order]).fillna(0)
    return vc.astype(int), len(s)


def share(col, cats):
    vc, n = dist(col)
    return 100 * vc.reindex(cats).fillna(0).sum() / n


def finding(col, scale):
    """One plain sentence for a closed item."""
    vc, n = dist(col, scale)
    p = lambda cats: 100 * vc.reindex(cats).fillna(0).sum() / n
    if scale is AGREE:
        return f'{pct(p(AGREE[3:]))} agree ({pct(p(AGREE[4:]))} strongly), {pct(p(AGREE[:2]))} disagree and {pct(p(AGREE[2:3]))} are neutral.'
    if scale is AMOUNT:
        return f'{pct(p(AMOUNT[3:]))} feel this a lot or a great deal; {pct(p(AMOUNT[:1]))} not at all.'
    if scale is CHANGE:
        return f'{pct(p(CHANGE[3:]))} expect it to change a lot or a great deal; {pct(p(CHANGE[:1]))} expect no change.'
    if scale is CONF:
        return f'{pct(p(CONF[3:]))} are very or extremely confident; {pct(p(CONF[:2]))} are slightly or not at all confident.'
    if scale is FREQ:
        return f'{pct(p(FREQ[2:]))} feel this at least half the time ({pct(p(FREQ[3:]))} most of the time or always); {pct(p(FREQ[:1]))} never do.'
    if scale is BEHAV:
        return f'{pct(p(BEHAV[4:]))} say almost always or always; {pct(p(BEHAV[:2]))} say rarely or never.'
    if scale is OFTEN:
        return f'{pct(p(OFTEN[3:]))} say often or very often; {pct(p(OFTEN[:2]))} say rarely or never.'
    if scale is IMPORT:
        return f'{pct(p(IMPORT[3:]))} say very or extremely important; {pct(p(IMPORT[:1]))} say not at all important.'
    if scale is LIKELY:
        return f'{pct(p(LIKELY[3:]))} say yes (probably or definitely), {pct(p(LIKELY[:2]))} say no and {pct(p(LIKELY[2:3]))} are unsure.'
    if scale is INTENSE:
        return f'{pct(p(INTENSE[2:3]))} say about the same; {pct(p(INTENSE[3:]))} say more intense at work and {pct(p(INTENSE[:2]))} less intense.'
    if scale is PRIORITY:
        return f'{pct(p(PRIORITY[2:3]))} say an equal balance; {pct(p(PRIORITY[:2]))} lean toward results and {pct(p(PRIORITY[3:]))} toward relationships.'
    top = vc.sort_values(ascending=False)
    return f'Most common answer: "{top.index[0]}" ({pct(100 * top.iloc[0] / n)}), followed by "{top.index[1]}" ({pct(100 * top.iloc[1] / n)}).'


# ---------- open-ended coding (keyword-based, approximate) ----------
NONE_RX = r"^\s*(none|nothing|no|na|n/?a|not sure|i don'?t know|idk|don'?t know|nope|never|not really|no idea|can'?t think.*|i can'?t recall|i dont know|unsure)\W*$"
THEMES = {
    'Q15': [('Coworkers supporting or helping each other', r'\b(help|support|team|coworker|co-worker|colleague|together)'),
            ('A positive mood lifting the day or productivity', r'\b(happy|happi|positive|good mood|joy|upbeat|laugh|humor|fun)'),
            ('Recognition, thanks or appreciation', r'\b(thank|apprec|gratitude|grateful|recogni|prais|compliment)'),
            ('Celebrating wins or milestones', r'\b(celebrat|milestone|birthday|achiev|success|accomplish|promot|award|goal)'),
            ('Empathy, listening or understanding', r'\b(listen|empath|understand|compassion|comfort|vulnerab|open up|shared)'),
            ('Customers, patients or students', r'\b(customer|client|patient|student|kid|guest)')],
    'Q16': [('Anger, arguments or conflict', r'\b(anger|angry|yell|argu|fight|conflict|scream|mad|rude|hostil|cuss|snap)'),
            ('Stress, pressure or burnout', r'\b(stress|overwhelm|anxi|pressure|deadline|burn|busy|tired|exhaust|drain)'),
            ('Personal life or grief spilling into work', r'\b(personal|family|death|died|passed|lost my|grief|divorce|broke up|break up|sick|illness|funeral)'),
            ('A boss, manager or supervisor', r'\b(boss|manager|supervisor|leader|management)'),
            ('Coworker behavior, attitudes or drama', r'\b(coworker|co-worker|colleague|attitude|gossip|drama|complain|team member)'),
            ('Customers, patients or students', r'\b(customer|client|patient|student|kid|guest)')],
    'Q22': [('Listen and communicate openly', r'\b(listen|open|hear|communicat|talk|ask|feedback)'),
            ('Stay calm and in control', r'\b(calm|control|patien|breath|compos|professional|manage|temper|relax|cool)'),
            ('Show empathy, kindness and care', r'\b(empath|understand|compassion|kind|care|caring|respect|nice|considerate)'),
            ('Be authentic, honest or vulnerable', r'\b(authentic|yourself|honest|vulnerab|real|transparen|human|genuine)'),
            ('Acknowledge emotions and let people express them', r'\b(acknowledg|express|okay to|ok to|allow|normaliz|validat|space)'),
            ('Keep emotions out of work', r"\b(leave it at|at home|at the door|hide|separate|don'?t show|not show|keep (your |their )?emotions|keep it to)")],
    'Q49': [('Empathy, compassion and emotional intelligence', r'\b(empath|compassion|emotion|eq|sympath|caring|kind|feel|understanding)'),
            ('Communication and working with people', r'\b(communicat|interact|relationship|people skill|listen|social|teamwork|collaborat|connect|interpersonal)'),
            ('Critical thinking, judgment and creativity', r'\b(critical|problem|think|creativ|innovat|judg|common sense|decision|reason|logic)'),
            ('Adaptability and willingness to learn', r'\b(adapt|flexib|learn|change|open.minded|resilien)'),
            ('Knowing how to use AI and technology', r'\b(ai|a\.i\.|tech|technology|computer|tool|digital)\b'),
            ('Integrity, honesty and trust', r'\b(honest|integrity|trust|ethic|loyal|moral)'),
            ('Leadership and management', r'\b(leader|leadership|manag)')],
}
INDUSTRY = [('Healthcare', r'\b(health|medical|hospital|nurs|pharma|dental|clinic|care|doctor|patient|therapy)'),
            ('Education', r'\b(educat|school|teach|universit|college|academ|child ?care|daycare|tutor)'),
            ('Retail', r'\b(retail|store|cashier|sales|grocery|walmart|target)'),
            ('Manufacturing', r'\b(manufactur|factory|production|plant|industrial|machin|automotive)'),
            ('Construction and trades', r'\b(construct|electric|plumb|hvac|carpent|maintenance|landscap|roof|mechanic)'),
            ('Food service and hospitality', r'\b(food|restaurant|hospitality|hotel|server|cook|chef|bar|catering|housekeep)'),
            ('IT and technology', r'\b(it|tech|software|computer|information|telecom|engineer|data)\b'),
            ('Finance, insurance and real estate', r'\b(financ|bank|insuranc|account|real estate|mortgage|credit)'),
            ('Government, military and public safety', r'\b(govern|military|army|navy|police|law enforcement|public|city|county|state|federal|security|fire)'),
            ('Transportation and logistics', r'\b(transport|logistic|warehouse|wearhouse|shipping|truck|driv|deliver|airline|aviation|aerospace)'),
            ('Professional services and consulting', r'\b(consult|legal|law|marketing|advertis|human resources|hr|admin|office)')]


def code(col, themes):
    s = df[col].dropna().astype(str)
    s = s[s.str.strip() != '']
    low = s.str.lower()
    none = low.str.match(NONE_RX)
    rows = []
    for name, rx in themes:
        hit = low.str.contains(rx, regex=True) & ~none
        ex = [t for t in s[hit] if 25 <= len(t) <= 150 and not re.search(r'(shit|fuck|pussy|damn|bitch|ass\b|mentally challenged|retard)', t, re.I)]
        rows.append((name, 100 * hit.sum() / len(s), ex[:2]))
    rows.sort(key=lambda r: -r[1])
    return rows, len(s), 100 * none.sum() / len(s)


# ---------- document helpers ----------
def shade(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hex_)
    tcPr.append(sh)


def new_doc():
    d = Document()
    for sec in d.sections:
        sec.left_margin = sec.right_margin = Inches(0.9)
        sec.top_margin = sec.bottom_margin = Inches(0.8)
    st = d.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10.5)
    for lvl, size in ((1, 15), (2, 12)):
        h = d.styles[f'Heading {lvl}']; h.font.name = 'Calibri'; h.font.size = Pt(size); h.font.color.rgb = NAVY
    return d


def table(d, header, rows, widths=None):
    t = d.add_table(rows=1, cols=len(header))
    t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ''
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9)
        shade(c, 'E8EEF5')
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''
            run = cells[i].paragraphs[0].add_run(str(v)); run.font.size = Pt(9)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    d.add_paragraph()
    return t


def note(d, text):
    p = d.add_paragraph(); r = p.add_run(text); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = GREY


def lead(d, text):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = True


def item(d, col, scale=None, who=None):
    vc, n = dist(col, scale)
    d.add_heading(f'{col}. {QTEXT[col]}', level=2)
    note(d, f'n = {n:,}' + (f' · {who}' if who else ''))
    lead(d, finding(col, scale))
    table(d, ['Response', 'n', '%'], [(k, f'{v:,}', pct(100 * v / n)) for k, v in vc.items()], [4.6, 0.8, 0.8])


def grid(d, prefix, scale, title, key_cats, key_label):
    cols = [c for c in df.columns if re.fullmatch(prefix + r'_\d+', c)]
    d.add_heading(title, level=2)
    note(d, f'n = {N:,} · each row adds to 100%')
    rows, stats = [], []
    for c in cols:
        label = QTEXT[c].split(' - ')[-1]
        vc, n = dist(c, scale)
        rows.append([label] + [pct(100 * vc.get(s, 0) / n) for s in scale])
        stats.append((label, 100 * vc.reindex(key_cats).fillna(0).sum() / n, c))
    table(d, ['Item'] + scale, rows, [2.4] + [0.75] * len(scale))
    stats.sort(key=lambda r: -r[1])
    lead(d, f'Ranked by {key_label}:')
    for label, v, c in stats:
        d.add_paragraph(f'{label}: {finding(c, scale)}', style='List Bullet')
    return {lbl: v for lbl, v, _ in stats}


def open_item(d, col, themes, who=None, intro=''):
    rows, n, none = code(col, themes)
    d.add_heading(f'{col}. {QTEXT[col]}', level=2)
    note(d, f'n = {n:,} written answers' + (f' · {who}' if who else '') +
         ' · themes found by keyword search, so percentages are approximate and an answer can count toward more than one theme')
    top = rows[0]
    lead(d, (intro or f'The most common theme is {top[0].lower()} ({pct(top[1])} of answers).') +
         f' About {pct(none)} gave no real answer (for example "none" or "not sure").')
    table(d, ['Theme', '% of answers', 'Examples'],
          [(name, pct(v), '\n'.join(f'"{e.strip()}"' for e in ex)) for name, v, ex in rows], [1.9, 0.9, 3.9])
    return rows


def q6_section(d):
    """Off-limits emotion, coded into the five EI 2.0 core emotions on the emotion each person named."""
    d.add_heading(f'Q6. {QTEXT["Q6"]}', level=2)
    note(d, f'n = {OFF["n_named"]:,} people named an emotion (of {OFF["n_all"]:,}) · coded into the five core emotions of '
            'Emotional Intelligence 2.0, using only the emotion each person named, not words in their explanation · '
            'full coding in the "anger-at-work" sheet of the survey workbook')
    a = CORES['Angry']['split']
    lead(d, f'Anger is the emotion most often named as off-limits: {pct(CORES["Angry"]["pct"])} of those who named an emotion, '
            f'counting rage, frustration and disdain as forms of anger. Non-leaders ({pct(a["Non-leaders"])}) and women ({pct(a["Women"])}) '
            f'name it more than leaders ({pct(a["Leaders"])}) and men ({pct(a["Men"])}); both gaps are statistically significant.')
    table(d, ['Core emotion', '% who named it', 'Non-leaders', 'Leaders', 'Women', 'Men', 'Most-named emotions'],
          [(c['name'], pct(c['pct']), pct(c['split']['Non-leaders']), pct(c['split']['Leaders']), pct(c['split']['Women']), pct(c['split']['Men']),
            ', '.join(f"{w['name'].lower()} ({w['n']})" for w in sorted(c['words'], key=lambda w: -w['n'])[:3])) for c in OFF['cores']],
          [1.0, 0.8, 0.8, 0.7, 0.7, 0.6, 2.1])
    note(d, 'People could name more than one emotion, so the rows add to more than 100%. Vulnerability is grouped with afraid.')


# ---------- full report ----------
d = new_doc()
d.add_heading('Friction Page Survey: Item-by-Item Findings', level=0)
note(d, f'{N:,} completed responses · fielded {start.min():%b %d, %Y} to {start.max():%b %d, %Y}')

leaders = (df['Q23'] == 'Yes').sum()
d.add_heading('About the data', level=1)
for t in [f'{N:,} people completed the survey; every response is 100% complete.',
          f'Questions 24–34 went only to the {leaders:,} people with a formal leadership role, who rated themselves. '
          f'Questions 35–45 went only to the {N - leaders:,} without one, who rated their own leader.',
          'Percentages are of the people who answered each item and are rounded, so they may not add to exactly 100.',
          'Open-ended answers were grouped into themes by keyword search. Treat those percentages as approximate. '
          'Q6 (the off-limits emotion) was coded more carefully into the Emotional Intelligence 2.0 core emotions; see the "anger-at-work" sheet.',
          f'Data quality: {int((recap < 0.5).sum())} responses had a reCAPTCHA score below 0.5, which can signal automated '
          'or careless responding. They are included here; removing them moves no answer share by more than about 1 point.']:
    d.add_paragraph(t, style='List Bullet')

d.add_heading('Understanding of EQ and background', level=1)
item(d, 'Q1', KNOW)
item(d, 'Q2')

d.add_heading('Emotions outside of work and at work', level=1)
out = grid(d, 'Q3', AMOUNT, f'Q3. {QTEXT["Q3_1"].split(" - ")[0]}', AMOUNT[3:], 'a lot or a great deal')
at = grid(d, 'Q17', AMOUNT, f'Q17. {QTEXT["Q17_1"].split(" - ")[0]}', AMOUNT[3:], 'a lot or a great deal')
d.add_heading('Q3 vs. Q17: the same emotions outside of work and at work', level=2)
cmp = sorted(((k, out[k], at[k], at[k] - out[k]) for k in out), key=lambda r: r[3])
flat = [k.lower() for k, o, a, diff in cmp if abs(diff) <= 1]
lead(d, f'Positive emotions drop the most at work: {cmp[0][0].lower()} ({cmp[0][3]:+.0f} points), {cmp[1][0].lower()} '
        f'({cmp[1][3]:+.0f}) and {cmp[2][0].lower()} ({cmp[2][3]:+.0f}). {", ".join(flat[:-1]).capitalize()} and {flat[-1]} '
        'are felt about as often at work as outside it.')
table(d, ['Emotion', 'Outside work', 'At work', 'Difference (points)'],
      [(k, pct(o), pct(a), f'{diff:+.0f}') for k, o, a, diff in cmp], [2.2, 1.3, 1.3, 1.6])
note(d, '"A lot" or "a great deal".')
item(d, 'Q8', INTENSE)

d.add_heading('Managing emotions at work', level=1)
item(d, 'Q4', CONF)
item(d, 'Q5', CONF)
q6_section(d)
item(d, 'Q13', FREQ)
item(d, 'Q14', FREQ)
open_item(d, 'Q15', THEMES['Q15'])
open_item(d, 'Q16', THEMES['Q16'])

d.add_heading('Workplace attitudes about emotion', level=1)
for c in ['Q7', 'Q9', 'Q10', 'Q11', 'Q12', 'Q19', 'Q20', 'Q21']:
    item(d, c, AGREE)
open_item(d, 'Q22', THEMES['Q22'])

d.add_heading('Self-rated EQ behaviors at work', level=1)
grid(d, 'Q18', BEHAV, f'Q18. {QTEXT["Q18_1"].split(" - ")[0]}', BEHAV[4:], 'almost always or always')

d.add_heading('Leaders rating themselves', level=1)
note(d, f'Asked only of the {leaders:,} respondents with a formal leadership role.')
item(d, 'Q23')
for c, sc in [('Q24', AGREE), ('Q25', AGREE), ('Q26', OFTEN), ('Q27', AGREE), ('Q28', PRIORITY), ('Q29', None),
              ('Q30', AGREE), ('Q31', AGREE), ('Q32', AGREE), ('Q33', AGREE), ('Q34', AGREE)]:
    item(d, c, sc, 'leaders only')

d.add_heading('Non-leaders rating their leader', level=1)
note(d, f'Asked only of the {N - leaders:,} respondents without a formal leadership role.')
for c, sc in [('Q35', AGREE), ('Q36', AGREE), ('Q37', OFTEN), ('Q38', AGREE), ('Q39', PRIORITY), ('Q40', None),
              ('Q41', AGREE), ('Q42', AGREE), ('Q43', AGREE), ('Q44', AGREE), ('Q45', AGREE)]:
    item(d, c, sc, 'non-leaders only')

PAIRS = [('Aware of their emotional impact on others', 'Q24', 'Q35', AGREE[3:]),
         ('Decide with both logic and emotion', 'Q25', 'Q36', AGREE[3:]),
         ('Stay focused and effective under stress', 'Q26', 'Q37', OFTEN[3:]),
         ('Balance honesty with empathy in feedback', 'Q27', 'Q38', AGREE[3:]),
         ('Convey clear direction and positivity', 'Q31', 'Q42', AGREE[3:]),
         ('Show honesty, respect and integrity', 'Q32', 'Q43', AGREE[3:]),
         ('Show care for employees', 'Q33', 'Q44', AGREE[3:]),
         ('Make it safe to ask questions and take risks', 'Q34', 'Q45', AGREE[3:])]
gap_rows = [(lbl, share(a, cats), share(b, cats)) for lbl, a, b, cats in PAIRS]
d.add_heading('Leaders vs. non-leaders: how leaders see themselves and how employees see them', level=2)
big = max(gap_rows, key=lambda r: r[1] - r[2])
lead(d, f'Leaders rate themselves far higher than employees rate their own leaders on every behavior. '
        f'The biggest gap is "{big[0].lower()}": {pct(big[1])} of leaders vs. {pct(big[2])} of employees.')
table(d, ['Behavior', 'Leaders about themselves', 'Employees about their leader', 'Gap (points)'],
      [(lbl, pct(a), pct(b), f'{a - b:+.0f}') for lbl, a, b in gap_rows], [2.6, 1.4, 1.5, 0.9])
note(d, 'Agree (somewhat or strongly), or often/very often for the stress item. These are different people: leaders are not rating the same leaders the employees describe.')
res_l, res_e = share('Q28', PRIORITY[:2]), share('Q39', PRIORITY[:2])
d.add_paragraph(f'Under deadline pressure, {pct(res_l)} of leaders say they lean toward results first, while {pct(res_e)} '
                'of employees say their organization\'s leaders do.', style='List Bullet')

d.add_heading('EQ, AI and the future of work', level=1)
item(d, 'Q46', IMPORT)
item(d, 'Q47', CHANGE)
item(d, 'Q48', LIKELY)
open_item(d, 'Q49', THEMES['Q49'])

d.add_heading('About the respondents', level=1)
yr = pd.to_numeric(df['Q50'], errors='coerce')
age = 2025 - yr
gen = pd.cut(yr, [1900, 1945, 1964, 1980, 1996, 2015], labels=['Silent (before 1946)', 'Boomers (1946–64)', 'Gen X (1965–80)', 'Millennials (1981–96)', 'Gen Z (1997–2012)'])
gvc = gen.value_counts().reindex(gen.cat.categories)
d.add_heading(f'Q50. {QTEXT["Q50"]}', level=2)
note(d, f'n = {yr.notna().sum():,}')
lead(d, f'Median age is about {age.median():.0f} (born {yr.median():.0f}); ages run from {age.min():.0f} to {age.max():.0f}. '
        f'{gvc.idxmax().split(" (")[0]} are the largest group.')
table(d, ['Generation', 'n', '%'], [(k, f'{v:,}', pct(100 * v / gvc.sum())) for k, v in gvc.items()], [4.6, 0.8, 0.8])
item(d, 'Q51')
race = df['Q52'].dropna().str.split(',').explode().str.strip().value_counts()
d.add_heading(f'Q52. {QTEXT["Q52"]}', level=2)
note(d, f'n = {df["Q52"].notna().sum():,} · people could choose more than one, so percentages add to more than 100')
lead(d, f'{pct(100 * race.iloc[0] / N)} chose {race.index[0]}, and {pct(100 * race.get("Black or African American", 0) / N)} chose Black or African American.')
table(d, ['Response', 'n', '% of people'], [(k, f'{v:,}', pct(100 * v / N)) for k, v in race.items()], [4.6, 0.8, 0.8])
item(d, 'Q53', EDU)
item(d, 'Q54', INCOME)
kids = pd.to_numeric(df['Q55'], errors='coerce')
d.add_heading(f'Q55. {QTEXT["Q55"]}', level=2)
note(d, f'n = {kids.notna().sum():,}')
lead(d, f'{pct(100 * (kids > 0).mean())} have at least one child under 18 at home; {pct(100 * (kids == 0).mean())} have none.')
kv = kids.clip(upper=4).value_counts().sort_index()
table(d, ['Children under 18', 'n', '%'], [(('4 or more' if k == 4 else f'{k:.0f}'), f'{v:,}', pct(100 * v / kids.notna().sum())) for k, v in kv.items()], [4.6, 0.8, 0.8])
ind = df['Q56'].dropna().astype(str).str.lower()
d.add_heading(f'Q56. {QTEXT["Q56"]}', level=2)
note(d, f'n = {len(ind):,} · typed answers grouped by keyword, so approximate; an answer is counted in its first matching group')
assigned = pd.Series('Other or unclear', index=ind.index)
for name, rx in reversed(INDUSTRY):
    assigned[ind.str.contains(rx, regex=True)] = name
iv = assigned.value_counts()
lead(d, f'The largest groups are {iv.index[0].lower()} ({pct(100 * iv.iloc[0] / len(ind))}) and {iv.index[1].lower()} ({pct(100 * iv.iloc[1] / len(ind))}); the sample spans a wide range of industries.')
table(d, ['Industry', 'n', '%'], [(k, f'{v:,}', pct(100 * v / len(ind))) for k, v in iv.items()], [4.6, 0.8, 0.8])
item(d, 'Q57', LEVEL)

# ---------- key findings (shared by both documents) ----------
q49 = code('Q49', THEMES['Q49'])[0]
ang = CORES['Angry']
KEY = [
    f'Leaders see themselves very differently than employees see them. {pct(big[1])} of leaders say they are aware of their '
    f'emotional impact on others, but only {pct(big[2])} of employees say that about their leader. Leaders rate themselves higher on all eight behaviors asked.',
    f'Emotional labor is common. {pct(share("Q13", FREQ[2:]))} say managing emotions at work leaves them drained at least half the time, '
    f'and {pct(share("Q14", FREQ[2:]))} say it leaves them feeling inauthentic that often.',
    f'People are less sure about negative emotions. {pct(share("Q4", CONF[3:]))} are very or extremely confident managing strong positive '
    f'emotions at work, vs. {pct(share("Q5", CONF[3:]))} for strong negative ones.',
    f'Anger is the emotion most often named as off-limits at work: {pct(ang["pct"])} of the {OFF["n_named"]:,} who named an emotion, well ahead of '
    f'afraid ({pct(CORES["Afraid"]["pct"])}) and sad ({pct(CORES["Sad"]["pct"])}). Non-leaders ({pct(ang["split"]["Non-leaders"])}) and '
    f'women ({pct(ang["split"]["Women"])}) name it most.',
    f'Workplaces are only lukewarm about emotion. {pct(share("Q9", AGREE[3:]))} agree emotions are acceptable at work, and '
    f'{pct(share("Q10", AGREE[3:]))} say showing emotion is seen as weakness. {pct(share("Q19", AGREE[3:]))} say leaders feel more pressure to hide emotions.',
    f'Work mutes positive emotions more than negative ones. Love drops from {pct(out["Love"])} outside work to {pct(at["Love"])} at work '
    f'and gratitude from {pct(out["Gratitude"])} to {pct(at["Gratitude"])}, while dread, frustration and pride are felt about as often in both.',
    f'Employees feel the cost of results-first leadership. {pct(share("Q40", ["Reduces my motivation/performance"]))} say it reduces their '
    f'motivation, vs. {pct(share("Q40", ["Boosts my motivation/performance"]))} who say it boosts it.',
    f'EQ is expected to matter more as AI spreads. {pct(share("Q46", IMPORT[3:]))} say EQ will be very or extremely important for human success, '
    f'and when asked which human skills will matter most, {q49[0][0].lower()} comes up most ({pct(q49[0][1])} of answers).',
    f'Engagement is high: {pct(share("Q20", AGREE[3:]))} agree they are engaged at work.',
]
anchor = d.paragraphs[2]._p
anchor.addprevious(d.add_heading('Key findings', level=1)._p)
for t in KEY:
    anchor.addprevious(d.add_paragraph(t, style='List Number')._p)
d.save(FULL)

# ---------- one-page summary ----------
s = new_doc()
s.add_heading('Friction Page Survey: Summary', level=0)
note(s, f'{N:,} completed responses ({leaders:,} leaders, {N - leaders:,} non-leaders) · fielded {start.min():%b %Y} to {start.max():%b %Y} · full item-by-item results in the companion report')
s.add_heading('What we found', level=1)
for t in KEY:
    s.add_paragraph(t, style='List Number')
s.add_heading('Leaders vs. employees', level=1)
table(s, ['Behavior', 'Leaders (self)', 'Employees (about their leader)', 'Gap'],
      [(lbl, pct(a), pct(b), f'{a - b:+.0f}') for lbl, a, b in gap_rows], [2.8, 1.2, 1.6, 0.7])
s.save(SHORT)
print('saved', FULL, SHORT)
print('\n'.join(KEY))
