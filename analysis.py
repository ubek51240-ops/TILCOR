"""Significance tests and effect sizes for the tables of chapter III (no third-party libraries, so the platform
runs without SciPy).

  * Pearson's chi-square and the log-likelihood statistic G² (Dunning, 1993) for an r × c table, with p-values
    from the chi-square distribution (regularised upper incomplete gamma function, series and continued
    fraction as in Press et al., 2007, sect. 6.2);
  * Cramér's V as the effect size of an r × c table (Cramér, 1946);
  * odds ratio of a 2 × 2 table with the 95 % Wald interval of its logarithm (0.5 is added to every cell when
    a cell is empty).
"""
import math


def _gammq(a, x):
    """Regularised upper incomplete gamma Q(a, x)."""
    if x < 0 or a <= 0:
        return float('nan')
    if x == 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1:                       # series for P, then Q = 1 - P
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(1000):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return max(0.0, 1.0 - s * math.exp(-x + a * math.log(x) - gln))
    b = x + 1 - a                       # continued fraction for Q (modified Lentz)
    c = 1.0 / 1e-300
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def chi2_sf(x, df):
    return _gammq(df / 2.0, x / 2.0) if x > 0 else 1.0


def contingency(table):
    """table: list of rows of counts. Returns chi2, g2, df, p_chi2, p_g2, cramers_v, n, expected."""
    rows = [list(map(float, r)) for r in table]
    r_tot = [sum(r) for r in rows]
    c_tot = [sum(col) for col in zip(*rows)]
    n = sum(r_tot)
    keep_r = [i for i, v in enumerate(r_tot) if v > 0]
    keep_c = [j for j, v in enumerate(c_tot) if v > 0]
    if n == 0 or len(keep_r) < 2 or len(keep_c) < 2:
        return None
    chi2 = g2 = 0.0
    exp = []
    for i in keep_r:
        er = []
        for j in keep_c:
            e = r_tot[i] * c_tot[j] / n
            o = rows[i][j]
            er.append(e)
            chi2 += (o - e) ** 2 / e
            if o > 0:
                g2 += 2 * o * math.log(o / e)
        exp.append(er)
    df = (len(keep_r) - 1) * (len(keep_c) - 1)
    k = min(len(keep_r), len(keep_c)) - 1
    v = math.sqrt(chi2 / (n * k)) if k > 0 else None
    return {'chi2': chi2, 'g2': g2, 'df': df, 'p_chi2': chi2_sf(chi2, df), 'p_g2': chi2_sf(g2, df), 'v': v, 'n': int(n),
            'min_expected': min(min(r) for r in exp)}


def odds_ratio(a, b, c, d):
    """2 x 2 table [[a, b], [c, d]]: odds ratio (a/b) / (c/d) with a 95 % Wald interval."""
    if 0 in (a, b, c, d):
        a, b, c, d = a + .5, b + .5, c + .5, d + .5
    lor = math.log(a * d / (b * c))
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return math.exp(lor), math.exp(lor - 1.96 * se), math.exp(lor + 1.96 * se)


def fmt_p(p, lang='uz'):
    if p is None:
        return '—'
    if p < 0.001:
        return 'p < 0,001' if lang != 'en' else 'p < 0.001'
    s = '%.3f' % p
    return 'p = ' + (s if lang == 'en' else s.replace('.', ','))
