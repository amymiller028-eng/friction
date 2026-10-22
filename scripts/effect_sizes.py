"""Practical significance of the anger gaps: percentage-point gap, Cohen's h, odds ratio with 95% CI."""
import math
import sys
import pandas as pd

r = pd.read_pickle(sys.argv[1])
nm = r['Named an emotion'].eq('Yes')
sp = r['Specific emotions'].fillna('')
vf = sp.str.split(', ').map(lambda xs: 'Vulnerability' in xs or 'Fear' in xs)
rows = [('Anger: non-leaders vs. leaders', r['Angry'].eq(1), r['Leader role'].eq('Non-leaders'), r['Leader role'].eq('Leaders')),
        ('Anger: women vs. men', r['Angry'].eq(1), r['Gender'].eq('Female'), r['Gender'].eq('Male')),
        ('Vulnerability or fear: men vs. women', vf, r['Gender'].eq('Male'), r['Gender'].eq('Female'))]
for name, hit, ga, gb in rows:
    a, na = (hit & nm & ga).sum(), (nm & ga).sum()
    b, nb = (hit & nm & gb).sum(), (nm & gb).sum()
    p1, p2 = a / na, b / nb
    h = 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))
    orr = (a / (na - a)) / (b / (nb - b))
    se = math.sqrt(1 / a + 1 / (na - a) + 1 / b + 1 / (nb - b))
    lo, hi = math.exp(math.log(orr) - 1.96 * se), math.exp(math.log(orr) + 1.96 * se)
    print(f'{name:<38} {p1:6.1%} vs {p2:6.1%}  gap {100 * (p1 - p2):5.1f} pts  ratio {p1 / p2:.2f}x  h={h:.2f}  OR={orr:.2f} [{lo:.2f}, {hi:.2f}]  n={na}/{nb}')
