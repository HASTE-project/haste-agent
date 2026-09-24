import math
from scipy.stats import ttest_ind
from results_analysis_table_of_results import labels, times

next_p_power = lambda p : math.floor(math.log10(p)) + 1
sigfig = lambda x, n=3: f"{x:.{max(0, n - 1 - math.floor(math.log10(abs(x))))}f}" # (with trailing 0s)

# Test the lambdas
for p in [0.2, 0.05, 0.04, 0.009, 0.0012, 6.39e-7, 3.1e-10]:
    print(f"p = {p:g}  ->  p < 10^({next_p_power(p)}) or {rf'$p < 10^{{{next_p_power(p)}}}$'} or {sigfig(p, n = 3)} or {p:.3g}")

print()


CON_LEVEL = 0.95

for label_A, label_B in [
    ['1,r', '1,s'],
    ['2,r', '2,s'],
    ['3,r', '3,s'],
                        ]:

    sample_A = times[labels.index(label_A)]
    sample_B = times[labels.index(label_B)]

    # From docs:
    # Calculate the T-test for the means of two independent samples of scores.
    # This is a test for the null hypothesis that 2 independent samples have identical average (expected) values.
    # This test assumes that the populations have identical variances by default.
    result = ttest_ind(sample_A,
                       sample_B,

                   # True: Student's t-test - equal variance assumption
                   # False: Welch's t-test - No assumption about equal variance - easier to justify?
                   equal_var=False
                   )

    print("==="*30)

    print(f"Comparing {label_A} and {label_B}")
    print(f"t-statistic = {result.statistic} standard errors")
    print(f"p-value associated with the given alternative = {result.pvalue}")
    print(f"The number of degrees of freedom used in calculation of the t-statistic = {result.df}")
    print(f"Confidence level = {CON_LEVEL}")
    print(f"Confidence interval around the difference in population means for the given confidence level = {result.confidence_interval(confidence_level=CON_LEVEL)} seconds")
    print()
    print(f"sample count A: {len(sample_A)}")
    print(f"sample count B: {len(sample_B)}")

    t = result.statistic
    p = result.pvalue


    # stats to 3 sig figs.
    latex = (
        rf"$t({sigfig(result.df, n=3)}) = {sigfig(result.statistic, n=3)}$, "
        rf"$p = {result.pvalue:.3g} $ or $ < 10^{{-123456}}$, "
        rf"${int(CON_LEVEL * 100)}\%$ CI $ [{result.confidence_interval(confidence_level=CON_LEVEL).low:.3g}, "
        rf"{result.confidence_interval(confidence_level=CON_LEVEL).high:.3g}]$"
    )

    print()
    print(latex)