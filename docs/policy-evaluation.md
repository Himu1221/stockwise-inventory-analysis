# Inventory projection and policy evaluation

## 14-day projection

The projection starts with closing stock on 31 October. It subtracts the baseline demand estimate each day and adds future promised receipts before that day's demand. The delay scenario shifts those promises three calendar days. Open orders due on or before the snapshot have no revised arrival date in the source and are excluded from projected receipts. The first day with unmet demand is the projected gap. Unmet demand does not carry forward as backorders.

The dashboard prioritizes confirming overdue orders, then reviewing inbound timing or quantity for products with a gap and a future promise. It suggests reviewing a reorder when a gap has no future promise. A separate synthetic supplier confirmation file, `data/inbound_confirmations.csv`, supplies revised dates for a subset of open orders. These are modeled commitments available at the snapshot. The budget calculator and Excel workbook continue to use their original inventory-position model. The projection helps the buyer check whether that plan relies on receipts that could arrive too late.

## Held-out comparison

The demand estimate uses only sales on positive-closing-stock days from 3 August through 1 October. Both policies start the 2–31 October test with the same historical opening stock and no inherited purchase orders. The synthetic generator supplies identical held-out demand to both policies. The simulation uses that demand to score unmet units. The reorder decision uses the training estimate and simulated inventory position.

| Setting | Fixed cover | StockWise |
|---|---|---|
| Reorder trigger | 7 days of estimated demand | Supplier lead time plus 4 days |
| Order-up-to level | 21 days of estimated demand | Supplier lead time plus 11 days |
| Review cadence | Daily | Daily |
| Pack rounding | Round up | Round up |

Both policies draw from the same supplier delay assumptions. For a given SKU and placement day, they receive the same seeded delay. Orders at different times can encounter different delays. The backtest evaluates reorder rules without the shared budget cap used by the dashboard scenario tool.

| Metric | Fixed cover | StockWise | Change |
|---|---:|---:|---:|
| SKU-days with unmet demand | 215 | 166 | −49 |
| Unmet units | 1,231 | 994 | −237 |
| Average daily closing inventory at cost | CAD 39,860.75 | CAD 37,676.23 | −CAD 2,184.52 |
| Value of purchase orders placed | CAD 50,314.38 | CAD 54,156.54 | +CAD 3,842.16 |
| Units still on order at test end | 1,812 | 2,310 | +498 |

The lead-based rule improved availability and reduced average inventory in this simulation, while placing more purchase orders by value. Spend includes orders still in transit. A longer test across multiple demand and delivery patterns would show how sensitive those results are to the chosen period and its starting stock.

Use `data/policy_backtest_daily.csv` to trace stock balances, simulated demand, and order placements. Its `simulated_demand` field is evaluation data. `data/policy_backtest_summary.csv` contains the displayed metrics.
