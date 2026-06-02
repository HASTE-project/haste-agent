
labels = [
'0,n',
'1,s',
'2,s',
'3,s',
'1,r',
'2,r',
'3,r',
'ffill,0' ]


# from results_analysis_benchmark.py   (time taken, i.e. makespan)

times = [[189.62956071, 188.9358809 , 189.53306317, 188.89595008, 189.11738372, 189.326823  ],
 [171.18717599, 169.89840198, 170.16703987, 170.20266485, 170.54400492, 170.85723591],
 [166.57133818, 166.87848401, 166.07723618, 166.40571809, 165.61088371, 167.95390892],
 [167.11507916, 166.13979888, 166.97401595, 166.40615392, 167.23539996, 166.27744222],
 [176.41721797, 175.89205408, 174.04230595, 174.88991213, 174.3710978, 174.93174887],
 [166.26198912, 167.33605814, 165.58362293, 166.41929817, 166.26461887, 165.87485814],
 [168.47383499, 166.87946701, 166.3824141 , 166.31914496, 165.87923789, 166.21895719],
 [166.13273597, 166.37595582, 166.42690587, 166.27055216, 166.7566278, 165.82221699]]

# helper functions
def mean(xs):
    return sum(xs) / len(xs)

def std(xs):
    m = mean(xs)
    return (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5  # population std

# build LaTeX table
lines = []
lines.append(r"\begin{tabular}{lrrrr}")
lines.append(r"\hline")
lines.append(r"label & h2 & h3 & h4 & h5 \\")  # placeholder headers
lines.append(r"\hline")

for label, row in zip(labels, times):
    mn = min(row)
    mx = max(row)
    mu = mean(row)
    sd = std(row)
    lines.append(f"{label} & {mn:.2f} & {mx:.2f} & {mu:.2f} & {sd:.2f} \\\\")

lines.append(r"\hline")
lines.append(r"\end{tabular}")

print("\n".join(lines))