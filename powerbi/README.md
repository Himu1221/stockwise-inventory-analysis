# Power BI implementation handoff

**Status:** Data, DAX snippets, theme and layout specification only. There is no native PBIX/PBIP report in this package. Power BI Desktop was not installed in the build environment. Do not claim this as a completed or tested Power BI implementation.

The completed interactive dashboard is `../reports/dashboard.html`. The Excel purchasing model is independently editable and verified in the authoring engine.

## Model setup

1. Import CSVs from `../data`. Set ISO dates to Date, costs/demand to Decimal, unit quantities/flags/priority to Whole number. Blank received dates must become null, never an arbitrary date.
2. Name tables `Planning` (planning_inputs), `Daily`, `Orders`, `Products`, `Suppliers`. Use single-direction relationships Suppliers→Products→Daily/Orders, and Products→Planning on SKU; check one-to-many cardinality. Do not let duplicated supplier fields create extra automatic relationships.
3. Use Products category and Suppliers supplier as shared slicers. Do not use fact-table labels as global slicers. For the pulse, remove category/supplier visual interactions if keeping the full-catalog definition. Disable category interactions on supplier visuals, or explicitly revise the denominator and labels together.
4. Import `StockWise-theme.json`. It supplies the basic palette and structural colors using the documented theme keys. Validate import in Desktop before adding further styling.
5. Create measures in `measures.dax` one block at a time. Format currencies as CAD and rates as percentages. The scenario measure requires disconnected parameter tables with the exact names specified in the comments.

## Three-page report layout

| Page | Visuals | Interactions |
|---|---|---|
| Inventory Overview | 4 KPI cards; 90-day availability line; stock-health donut; SKU detail matrix | Category/supplier slicers; SKU drill-through; tooltip with demand exposure |
| Reorder Planning | Numeric-range parameter slicers; requested-unit matrix; baseline funded plan | Demand/lead factors, safety/review days; baseline budget allocation clearly labeled |
| Supplier Performance | Delivered on-time rate; observed lead; overdue open matrix | Supplier slicer; category excluded with visible explanation |

The supplied dynamic DAX covers **requested units**, not greedy budget allocation. For exact budget behavior, use the completed web/Excel model. Import `baseline_purchase_plan.csv` only for a clearly labeled fixed baseline budget view. Never present that static import as reacting to scenario slicers. Implement and test a separate allocation solution before claiming full Power BI scenario parity.

## Validation before calling the native report finished

- On-hand value and stockout exposure agree with analysis JSON.
- Full-catalog baseline spend in the imported baseline table is CAD 5,717.58; 12 funded lines.
- Blanks in receipt date remain open; overdue orders are not counted in the delivered denominator.
- A single SKU has 90 daily rows; adding PO data does not multiply sales or inventory.
- Measure totals are checked under single SKU, category and supplier filters.
- Parameter slicers do not change static baseline funded quantities; clearly label their different scopes.
- Keyboard navigation, contrast and the mobile layout are reviewed in Desktop/service.

Official references: [Report themes](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes), [custom theme structure](https://learn.microsoft.com/en-us/power-bi/create-reports/report-themes-create-custom), [numeric range parameters](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-what-if).
