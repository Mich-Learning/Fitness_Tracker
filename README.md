## Running Analysis

The project also correlates weekly running volume with weekly
average weight.

### Weekly Summary

| Week       | Avg Weight (kg) | Total KM |
|------------|-----------------|----------|
| 2026-08-30 | 89.83           | 26.44    |
| 2026-09-06 | 89.90           | 22.56    |
| 2026-09-13 | 91.20           | 44.07    |
| 2026-09-20 | 89.93           | 11.87    |

### Correlation

**+0.86** (weight vs. km), 4 weeks analyzed.

**Interpretation:** With only 4 weeks of data, this correlation is
not statistically meaningful. The positive sign likely reflects
reverse causation (running more in response to higher weight) and
the short observation window. More data is needed for a reliable
conclusion.

### What's next

- Run the analysis weekly as new data is logged
- Revisit the correlation after 3+ months
- Consider lag analysis (this week's runs vs. next week's weight)
- Add scatter plot to visualize the relationship