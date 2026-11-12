# Maintain StockWise

Source of truth: `src/build.py`, `sql/inventory.sql`, `src/dashboard.html`, and `src/build_workbook.mjs`.

1. Read README and business-case limitations before changing definitions.
2. Change the source files, then run the Python build and tests.
3. If policies change, update the Python `purchase_plan`, browser `calculate` and Excel formulas together; compare every baseline row, not only totals.
4. Regenerate Excel only in an artifact-tool-capable environment. Do not replace it with a CSV renamed .xlsx.
5. Open the generated dashboard. Verify filters, no-results, product dialogs, scenario limits, zero budget, CSV export, supplier denominators and mobile layout.
6. Update baseline figures and portfolio copy when data or policy changes. Keep the simulated-data disclosure.
7. Review before publishing. Free static hosting is sufficient; no paid domain or service is needed.

The snapshot date appears in the generator, SQL and presentation labels. Update all three together when advancing the reporting period. This release intentionally uses a fixed snapshot for reproducibility.
