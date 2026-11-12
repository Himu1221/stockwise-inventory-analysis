# Data contract

All dates are ISO calendar dates. All amounts are CAD. Blank receipt dates mean not yet received at the snapshot, not a known future receipt. Quantity unit is each product's retail unit; purchases must be pack multiples.

| File | Grain / key | Important fields |
|---|---|---|
| products.csv | One row per SKU; `sku` | product, category, supplier_id, unit_cost, unit_price, pack_size |
| suppliers.csv | One row per supplier; `supplier_id` | supplier, lead_days (promised planning assumption) |
| daily_inventory.csv | SKU × date; `sku,date` | opening_stock, receipts, sales_units, closing_stock, fully_available |
| purchase_orders.csv | One single-SKU order; `order_id` | sku, supplier_id, ordered_date, promised_date, received_date, quantity |
| planning_inputs.csv | One row per SKU at snapshot; `sku` | aggregated facts, daily_demand, on_hand, on_order, priority |
| baseline_purchase_plan.csv | One row per SKU | policy quantities, funded_qty, order_cost, remaining_budget |

Relationships: suppliers 1→many products; products 1→many daily observations; products 1→many purchase orders. In this dataset an order belongs to one SKU. Never join the daily and order facts before aggregating to SKU, or measures will multiply.

## Definitions

| Metric | Definition / caution |
|---|---|
| fully_available | 1 if closing_stock > 0, otherwise 0. Conservative exposure proxy only |
| daily_demand | SUM(sales_units on fully_available days) / SUM(fully_available), rounded to 4 decimals; SQL NULL if no exposure |
| stockout_days | Days with closing_stock = 0; does not prove exact lost demand |
| stockout exposure | SUM(stockout_days) / SUM(observation_days) for selected SKUs |
| on_hand | Closing stock on 2026-10-31 |
| on_order | All purchase quantities with blank received_date at snapshot |
| inventory position | on_hand + on_order; no reservations or backorders |
| cover | on_hand / baseline daily_demand; undefined if demand zero |
| stock health | Stockout if on_hand=0; otherwise low if cover≤lead_days+4; excess if cover>60; otherwise balanced |
| excess stock value | Full on-hand value of products classified excess, not only units above 60 days and not recoverable cash |
| reordered quantity | If position≤ROP: ceil(max(0,target-position)/pack)×pack, otherwise zero |
| funded quantity | Minimum of request and floor(remaining budget / pack cost)×pack |
| delivered on-time rate | Received_date≤promised_date delivered orders / all delivered orders |
| overdue open | Blank receipt date and promised_date≤snapshot |
| observed lead | Mean calendar days from order to observed receipt; closed orders only |

The browser's historical pulse is full catalog. Snapshot filters never silently change that trend. Supplier cards apply only the supplier filter. Excel uses the full catalog and the same fixed priority as the baseline browser scenario.

## Quality gates and handling

The build fails if source checks fail: uniqueness of SKU/day, nonnegative movements, daily balance, received-PO reconciliation, valid SKU foreign keys, 90 observations per SKU, positive demand exposure and positive cost/pack size. These gates validate the generated case; a real ingestion pipeline would additionally quarantine invalid dates, duplicates, negative adjustments, partial receipts and supplier changes rather than assume this contract.
