-- Snapshot at 2026-10-31. Aggregate each fact BEFORE joining to prevent fan-out.
WITH demand AS (
 SELECT sku, SUM(sales_units) sold_units,
 SUM(fully_available) in_stock_days,
 SUM(CASE WHEN fully_available=1 THEN sales_units ELSE 0 END) uncensored_sales,
 SUM(CASE WHEN closing_stock=0 THEN 1 ELSE 0 END) stockout_days,
 COUNT(*) observation_days
 FROM daily_inventory GROUP BY sku
), open_po AS (
 SELECT sku, SUM(quantity) on_order FROM purchase_orders
 WHERE received_date='' GROUP BY sku
), snapshot AS (
 SELECT sku, closing_stock on_hand FROM daily_inventory WHERE date='2026-10-31'
)
SELECT p.*, s.supplier, s.lead_days, d.sold_units,d.in_stock_days,d.stockout_days,d.observation_days,
 ROUND(1.0*d.uncensored_sales/NULLIF(d.in_stock_days,0),4) daily_demand,
 snap.on_hand, COALESCE(o.on_order,0) on_order
FROM products p JOIN suppliers s USING(supplier_id)
JOIN demand d USING(sku) JOIN snapshot snap USING(sku)
LEFT JOIN open_po o USING(sku);
