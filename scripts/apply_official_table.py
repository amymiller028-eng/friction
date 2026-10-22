"""Put the official EI 2.0 'Five Core Feelings' table in the page's reference section (text only, no stats)."""
import sys

f = sys.argv[1]
c = open(f, encoding='utf-8').read().replace('\r\n', '\n')
TABLE = {
    'High':   [['Elated', 'Excited', 'Overjoyed', 'Thrilled', 'Exuberant', 'Ecstatic', 'Fired up', 'Passionate'],
               ['Depressed', 'Agonized', 'Alone', 'Hurt', 'Dejected', 'Hopeless', 'Sorrowful', 'Miserable'],
               ['Furious', 'Enraged', 'Outraged', 'Boiling', 'Irate', 'Seething', 'Loathsome', 'Betrayed'],
               ['Terrified', 'Horrified', 'Scared stiff', 'Petrified', 'Fearful', 'Panicky', 'Frantic', 'Shocked'],
               ['Sorrowful', 'Remorseful', 'Defamed', 'Worthless', 'Disgraced', 'Dishonored', 'Mortified', 'Admonished']],
    'Medium': [['Cheerful', 'Gratified', 'Good', 'Relieved', 'Satisfied', 'Glowing'],
               ['Heartbroken', 'Somber', 'Lost', 'Distressed', 'Let down', 'Melancholy'],
               ['Upset', 'Mad', 'Defended', 'Frustrated', 'Agitated', 'Disgusted'],
               ['Apprehensive', 'Frightened', 'Threatened', 'Insecure', 'Uneasy', 'Intimidated'],
               ['Apologetic', 'Unworthy', 'Sneaky', 'Guilty', 'Embarrassed', 'Secretive']],
    'Low':    [['Glad', 'Contented', 'Pleasant', 'Tender', 'Pleased', 'Mellow'],
               ['Unhappy', 'Moody', 'Blue', 'Upset', 'Disappointed', 'Dissatisfied'],
               ['Perturbed', 'Annoyed', 'Uptight', 'Resistant', 'Irritated', 'Touchy'],
               ['Cautious', 'Nervous', 'Worried', 'Timid', 'Unsure', 'Anxious'],
               ['Bashful', 'Ridiculous', 'Regretful', 'Uncomfortable', 'Pitied', 'Silly']],
}
rows = ''.join('<tr><th scope="row">' + lvl + '</th>' + ''.join('<td>' + '<br>'.join(words) + '</td>' for words in cols) + '</tr>'
               for lvl, cols in TABLE.items())
official = ('    <h3 class="ref-h">Emotional Intelligence 2.0: Five Core Feelings</h3>\n'
            '    <div class="tblwrap"><table class="official"><thead><tr><th>Intensity</th><th>Happy</th><th>Sad</th><th>Angry</th>'
            '<th>Afraid</th><th>Ashamed</th></tr></thead><tbody>' + rows + '</tbody></table></div>\n'
            '    <h3 class="ref-h">How this survey&rsquo;s answers fit the table</h3>\n')

def swap(old, new):
    global c
    if old not in c:
        raise SystemExit('missing: ' + old[:90])
    c = c.replace(old, new, 1)

swap('    <table class="reftbl">', official + '    <table class="reftbl">')
swap('The full feeling-words table, with the complete list of words for each emotion and intensity, appears in the book.',
     'The Five Core Feelings table above is reproduced from the book.')
swap('Vulnerability isn&rsquo;t in the feeling-words table; we grouped it with afraid, alongside feeling insecure and exposed.',
     'Vulnerability isn&rsquo;t in the table; we grouped it with afraid, next to &ldquo;insecure.&rdquo; Emotions such as rage, love and pride aren&rsquo;t listed either; each was placed with the closest feeling in the table.')
swap('.method-h{margin-top:0}', '''.method-h{margin-top:0}
.ref-h{font-size:1.05rem;font-weight:700;margin:1.6rem 0 .6rem}
.tblwrap{overflow-x:auto}
.official{min-width:620px;font-size:.86rem}
.official thead th{background:var(--navy);color:#fff;text-transform:uppercase;letter-spacing:.05em;font-size:.75rem}
.official tbody th{background:var(--soft);font-weight:700;vertical-align:middle;text-transform:uppercase;font-size:.75rem;letter-spacing:.05em}
.official td{vertical-align:top;line-height:1.55;border-left:1px solid var(--hair)}''')
open(f, 'w', encoding='utf-8').write(c)
print('ok')
