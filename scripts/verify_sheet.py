"""Read the coded rows back out of the saved 'anger-at-work' sheet and compute what each formula should show."""
import sys
import pandas as pd

raw = pd.read_excel(sys.argv[1], sheet_name='anger-at-work', header=None)
hdr = raw.index[raw[0].eq('ResponseId')][0]          # the data table header moves when the dictionary grows
x = raw.iloc[hdr + 1:].copy()
x.columns = raw.iloc[hdr]
x = x[x['ResponseId'].notna()]
for c in ['Angry', 'Afraid', 'Sad', 'Ashamed', 'Happy']:
    x[c] = pd.to_numeric(x[c])
print(len(x), 'coded rows')
nm = x['Named an emotion'].eq('Yes')

def grp(c, col, v):
    return x[c][x[col].eq(v)].sum() / (nm & x[col].eq(v)).sum()

for c in ['Angry', 'Afraid', 'Sad', 'Ashamed', 'Happy']:
    print(f"{c:<8} n={x[c].sum():<4} named={x[c].sum() / nm.sum():.1%} all={x[c].sum() / len(x):.1%} "
          f"non-leaders={grp(c, 'Leader role', 'Non-leaders'):.1%} leaders={grp(c, 'Leader role', 'Leaders'):.1%} "
          f"women={grp(c, 'Gender', 'Female'):.1%} men={grp(c, 'Gender', 'Male'):.1%}")
sp = x['Specific emotions'].fillna('').str.split(', ')
vf = sp.map(lambda xs: 'Vulnerability' in xs or 'Fear' in xs)
w = (nm & x.Gender.eq('Female') & vf).sum() / (nm & x.Gender.eq('Female')).sum()
m = (nm & x.Gender.eq('Male') & vf).sum() / (nm & x.Gender.eq('Male')).sum()
print(f'vulnerability/fear: women {w:.1%}, men {m:.1%}, ratio {m / w:.2f}x; named an emotion: {nm.sum()}')
