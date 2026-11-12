# Business brief and decision record

## Decision and stakeholders

The fictional retailer's buyer must decide what to order at the 31 October snapshot. The store manager needs stockout triage; the buyer needs purchase quantities and inbound visibility; finance needs a transparent budget ceiling; the supplier manager needs an overdue-order escalation list.

Success for this prototype is reproducible, interpretable decisions and reconciled data. A live pilot would measure future stockout exposure, average inventory at cost, write-offs and supplier delivery reliability before claiming any operational benefit.

## Scope

One store, 48 products, six categories, four suppliers, 90 daily observations per SKU. No customer data, personal information, production integrations, order submission, payments or live inventory updates. Purchase recommendations require human review. All data is synthetic.

## Findings and recommended next moves

| Evidence at baseline | Implication | Proposed action | Proposed role |
|---|---|---|---|
| Seven products have zero on-hand stock; another sixteen have low cover | Availability risk is broader than immediate stockouts | Review the attention queue and confirm incoming delivery dates first | Buyer |
| All 12 triggered purchase lines fit the CAD 8,000 budget at CAD 5,717.58 | Baseline budget is sufficient for this policy's requests | Review pack quantities, shelf life and inbound duplication before approving | Buyer + finance |
| Five products exceed 60 days of on-hand cover, representing approximately CAD 40,907 at cost | Working capital and perishability warrant review | Investigate promotion history, expiry and return/transfer options; do not treat all value as recoverable savings | Store manager |
| Historical zero-closing stock exposure is 14.1% of SKU-days | Observed sales can understate demand | Compare the in-stock-day proxy to a held-out period and alternative estimates before tuning policy | Analyst |

Figures are generated synthetic examples. Owners and actions are proposed roles, not completed engagements.

## Requirements and acceptance criteria

| ID | Requirement | Acceptance evidence |
|---|---|---|
| R01 | Show availability, cost exposure and attention items | Overview metrics reconcile to analysis JSON; radar labels match product details |
| R02 | Filter inventory by category and supplier | Beverages selects 8 SKUs; incompatible filters show an empty state |
| R03 | Trace a product recommendation to inputs | Product dialog shows on hand, on order, demand proxy, exposure and supplier lead |
| R04 | Respect purchasing packs and budget | Automated partial-pack and zero-budget tests; browser controls reject invalid ranges |
| R05 | Include assumptions in exported decisions | Purchase CSV contains demand/lead factors, safety/review days and scope budget |
| R06 | Separate inbound uncertainty from delivery performance | Closed-order on-time denominator excludes open orders; overdue open count displayed |
| R07 | Support spreadsheet review | Formula-based Excel plan with five editable controls; baseline agrees with Python |
| R08 | Make data lineage auditable | CSV → SQLite SQL → planning inputs → JSON/HTML; ledger and receipt reconciliation gates |
| R09 | Work on smaller screens | Responsive navigation/cards; wide detail tables scroll inside their container |

## Policy choices and limitations

The 4-day safety buffer and 60-day excess threshold are illustrative assumptions, not statistically estimated service levels. The model assumes constant unit costs and pack sizes. In-stock-day demand may overstate or understate future demand because availability and sales patterns are related. Positive closing stock is an exposure proxy, not proof of uninterrupted shelf availability.

All open units contribute to position even if overdue. The model therefore cannot prove stock availability before the next arrival. Review overdue orders and expiry before approving. Fresh products deliberately illustrate why a cover-based rule must be checked against shelf life; no expiry records are provided.

Priority is fixed to baseline on-hand cover, then SKU. It does not dynamically reorder when scenario inputs change, and it does not maximize margin or service level. A later phase could compare priority policies using backtesting and add expiry, order arrival calendars, minimum order values, freight and SKU-level variability.

## Proposed workflow

Snapshot and reconcile → review stockout/excess signals → confirm inbound promises → change scenario assumptions → inspect requested and funded packs → export review list → buyer approves in their ordering system → evaluate future outcomes.

StockWise stops at the review-list stage. It never submits an order.
