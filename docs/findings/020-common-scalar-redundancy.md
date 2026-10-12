# Finding 020 - Correction to Finding 019: it is COMMON-SCALAR redundancy, not topology vs value

Status: Finding 019's explanation is **refuted** and its claim of independent reproduction is
**retracted**. The separation it measured is real, but its cause is different and the
consequence for the certificate library is worse.
Reproduce: scripts/step42_overlap_rule.py, step43_separation_test.py
Data: runs/overlap_rule.json, runs/separation_test.json

## 1. What Finding 019 claimed

  1. value-value cuts average 0.8274 and topology-topology cuts 1.1330;
  2. this "reproduces findings 013 and 015 from different cuts", so the split that matters
     is topology versus value;
  3. both candidate certificates are value-derived and therefore do not compose.

## 2. Claim 2 is retracted outright

Finding 019's topology cuts **are** Finding 015's structural cuts - payload grounded,
>=2 ground ties, payload degree >=3, n >=6 - identical, not merely similar. And three of
its four value cuts (sag, in-band, and the performance pair) are Finding 013's. So the
"reproduction from a different cut list" was the same measurement run twice, and the
agreement of the two means was guaranteed rather than evidential.

That was my error and it inflated a coincidence into a confirmation.

## 3. Claim 1's explanation is refuted by a controlled test

If the split were topology versus value, then any value cut should behave like any other
value cut. Step 42 built cuts keyed to **controlled overlaps** in the structure's
independent draws:

| pair | overlap | ratio |
|---|---|---|
| first-edge stiffness x last-edge stiffness | disjoint draws | 1.100 |
| first-edge stiffness x topology | disjoint | 0.874 |
| last-edge stiffness x topology | disjoint | 0.897 |
| first-edge stiffness x waterbed W | shares a draw with W | 0.920 |
| last-edge stiffness x waterbed W | shares a draw with W | 1.080 |
| waterbed W x topology | disjoint | 1.035 |

| group | mean ratio |
|---|---|
| disjoint draws (4 pairs) | **0.976** |
| shared draw (2 pairs) | **1.000** |

**No separation, and no effect of overlap.** Every value is within about two standard
errors of 1.0 at n = 200. The overlap hypothesis is dead, and with it the topology-versus-
value reading: these are all value cuts and they do not behave alike.

## 4. Claim 1 itself survives, for the specific cut families

Bootstrap over networks, 2000 resamples:

| family | mean ratio | 95% CI |
|---|---|---|
| VAL (sag, peak, in-band, g0/m0, W) | 0.8862 | [0.8567, 0.9182] |
| TOP (grounded, >=2 ties, degree, n) | 1.1339 | [1.0810, 1.1937] |
| **TOP - VAL** | **0.2477** | **[0.1786, 0.3185]** |

The gap excludes zero, and holds across three seeds (VAL 0.8861, 0.9047, 0.9060; TOP
1.1330, 1.0902, 1.1441). **The separation is real for these cuts.**

But note the family mean moved from 0.8274 in Finding 019 to 0.8862 here, purely because
adding the peak cut to the family changes which pairs are averaged. A statistic that moves
by 0.06 when one cut joins the family is not a robust characterisation of anything.

## 5. What actually distinguishes the families

Every VAL cut is a monotone function of the same underlying scalar - **how well does this
structure isolate**. The rank correlations say so directly, from Finding 019's own data:

| pair | Spearman rho | p |
|---|---|---|
| sag vs in-band | **-0.8195** | 9.4e-50 |
| g0/m0 vs W | **-0.4976** | 6.6e-14 |
| W vs sag | **+0.4622** | 5.6e-12 |
| g0/m0 vs sag | **-0.4509** | 2.1e-11 |
| W vs in-band | **-0.3888** | 1.3e-08 |
| g0/m0 vs in-band | **+0.3872** | 1.5e-08 |

All six |rho| are between 0.39 and 0.82. They are all measuring one thing. The TOP cuts
are binary statements about graph shape and are not functions of that scalar, and step 42's
single-edge cuts are not either - which is why both are independent and the VAL family is
not.

> **Cuts that measure one capability are redundant with each other. Cuts that do not, are
> not. Topology versus value was a proxy for this and the proxy is wrong.**

## 6. The consequence is worse than Finding 019 said

Finding 019 concluded that certificates must be keyed to topology. The corrected reading is
that **certificates must not be monotone functions of a common scalar**, and every physical
performance bound is exactly that - a monotone measure of how well the structure performs.

This is a real threat to the library programme. Finding 011 needs successive cuts to take a
constant fraction of what remains; if all certificates rank the space the same way, the
second one cuts almost nothing the first left.

**The operational test is now cheap and direct**: compute the Spearman correlation between
two certificates' bounds over the ensemble. |rho| near 0 means the pair is worth having;
|rho| near 0.5 or above means one certificate wearing two hats, whatever their proofs look
like. This replaces the topology/value rule with something measurable on the bounds
themselves rather than on a label attached to them.

## 7. What is still open

  * Whether **any** pair of physical performance bounds can have |rho| near zero. The
    correlations above suggest a common factor, but the search has only examined bounds on
    one physical domain and one ensemble family.
  * Whether a topology-keyed bound with growing coverage exists at all - Finding 010
    eliminated the one candidate and Finding 019's route to a replacement is now closed.
  * Finding 018's waterbed and Finding 014's payload law both stand as results. What is
    retracted is only the claim that they, or cuts like them, can compose.

## 8. Limits

  * The bootstrap resamples networks, not cuts. With 10 VAL pairs and 6 TOP pairs the
    family means rest on few pairs, and section 4 shows the mean is sensitive to family
    membership.
  * Spearman rho is computed on the raw quantities, not on the binary cuts, so it
    diagnoses the cause rather than restating the ratio.
  * One ensemble family, one calibration, one band edge.
