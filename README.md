# StockWise — Inventory & Reordering Analysis

An independent business/data analysis portfolio case study by **Himanshu Gidhvani**. A simulated convenience retailer has stockouts alongside excess stock. StockWise turns inventory observations and supplier promises into a reviewable, budget-constrained purchase plan.

**All businesses, products, transactions and results are simulated. This is not paid client work. No savings, revenue uplift or service-level improvement has been measured.**

## Open the project

[Launch the live dashboard](https://himu1221.github.io/projects/stockwise/dashboard.html)

- Open `reports/dashboard.html` in a modern browser. It is self-contained, works offline, and requires no account or build tool.
- Open `StockWise-Purchasing-Model.xlsx` in Excel. Amber cells on Purchase plan are editable. The workbook models the full catalog; use dashboard filters for narrower scopes.
- Read `docs/business-case.md` for stakeholder needs, decisions and limitations.
- Read `docs/data-dictionary.md` for grains, definitions and relationships.
- Read `powerbi/README.md` for the Power BI handoff. **There is no native PBIX/PBIP in this release.** The verified dashboard is HTML/CSS/JavaScript; the Power BI measures and theme are handoff materials, not a tested Power BI report.

## Dashboard

Three views: **Inventory overview**, **Reorder planning**, **Supplier signals**.

Inventory overview includes cost-based on-hand value, zero-closing exposure, stock health, a full-catalog availability trend, clickable product radar, searchable attention queue and product drill-through dialogs. Category/supplier filters update snapshot metrics; the historical trend stays full catalog and is labeled accordingly.

Reorder planning exposes demand and lead multipliers, safety days, review days and purchasing budget. It recomputes pack-rounded requests and funded quantities, with an assumptions-inclusive CSV export. Priority remains fixed to baseline on-hand cover for reproducibility. Filters define an independent purchasing budget scope; do not add results from overlapping scopes.

Supplier signals separates delivered on-time performance from overdue open purchase orders. It respects the supplier filter; category is explicitly excluded.

Typography uses Bahnschrift / Aptos Display headings, Segoe UI body copy, and Consolas figures with cross-platform fallbacks. Fonts are system based; no external font service or JavaScript library is required. Statuses include text, not color alone. Responsive navigation, visible keyboard focus, native dialogs and reduced-motion support are included.

## Baseline evidence

Snapshot: **31 October 2026**. History: **3 August–31 October 2026**. Currency: **CAD**.

48 products · 6 categories · 4 suppliers · 4,320 SKU-day observations · 276 purchase orders. Eight source quality gates and fourteen Python tests pass.

The baseline full-catalog scenario uses demand factor 1, lead factor 1, safety buffer 4 days, review interval 7 days and CAD 8,000 budget. It requests and funds **12 lines for CAD 5,717.58**, leaving **CAD 2,282.42**. This is modeled purchasing spend, not a realized benefit.

## Analysis approach

1. Generate deterministic transactions using seed 1221; latent demand drives simulation and backtest evaluation.
2. Reconcile daily opening stock + receipts − sales = closing stock and purchase-order receipts to the ledger.
3. Aggregate daily facts and open orders separately in SQL before joining product dimensions, avoiding join fan-out.
4. Estimate demand from sales on days with positive closing stock divided by those days. Zero-closing days are conservatively excluded. This is a biased proxy under some conditions, not an unbiased forecast.
5. Trigger a reorder when inventory position (on hand + all open units) is at or below demand × (lead + safety days). Target adds the review interval. Round the shortfall up to a pack multiple.
6. Allocate affordable packs in baseline cover order. This is a transparent greedy heuristic, not mathematical optimization. Arrival timing, backorders, shelf life, tax, freight and reservations are not modeled.

## Reproduce

Python 3.10+; standard library only for the core analysis:

```sh
python src/build.py
python -m unittest discover -s tests -v
```

Generated artifacts: four source CSVs, planning inputs, baseline purchase plan, a SQLite database, analysis JSON and the self-contained dashboard. Edit the HTML template in `src/dashboard.html`, then rebuild; do not maintain a separate generated dashboard by hand.

The Excel workbook is separately authored with `@oai/artifact-tool` 2.8.58+ using `src/build_workbook.mjs`. Run it in an environment providing that package:

```sh
node src/build_workbook.mjs .
```

The builder recalculates, compares the baseline, tests zero budget and demand sensitivity, renders both sheets, and exports XLSX. It is optional for the core Python build and not part of CI. The shipped workbook has been formula-checked and visually reviewed through the authoring engine; native Excel UI validation was not performed.

## Business analyst artifacts

- Stakeholder brief, scope and evidence-linked recommendations
- Requirements and acceptance criteria
- Data dictionary, relationships and KPI definitions
- SQL with pre-aggregation and a reproducible SQLite database
- Automated source checks, boundary tests and cross-engine baseline parity
- Editable Excel purchasing model and Power BI implementation handoff
- Honest LinkedIn / portfolio description in `docs/portfolio-copy.md`

See `MAINTENANCE.md` for future changes.

## Projection and policy backtest

Open a product to compare promised receipt dates with a three-day delay. The planning view includes a held-out comparison of the fixed and lead-based reorder rules. See [policy evaluation](docs/policy-evaluation.md) for assumptions and results.
