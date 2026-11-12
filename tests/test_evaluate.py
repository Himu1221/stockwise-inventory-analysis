import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from build import generate
from evaluate import backtest, project_stock


class EvaluationTests(unittest.TestCase):
    def test_receipt_delay_exposes_gap_and_overdue_stock_is_excluded(self):
        snapshot = date(2026, 10, 31)
        product = dict(sku='test', on_hand=10, daily_demand=10)
        orders = [
            dict(sku='test', order_id='late', received_date='', promised_date='2026-10-31', quantity=200),
            dict(sku='test', order_id='due', received_date='', promised_date='2026-11-02', quantity=150),
        ]
        promised = project_stock(product, orders, snapshot)
        delayed = project_stock(product, orders, snapshot, delay_days=3)
        self.assertIsNone(promised['first_gap'])
        self.assertEqual(delayed['first_gap']['day'], 2)
        self.assertEqual(delayed['next_receipt'], '2026-11-05')
        self.assertEqual(sum(day['receipts'] for day in delayed['timeline']), 150)
        self.assertEqual(delayed['action'], 'Confirm overdue PO')

    def test_backtest_has_paired_demand_and_reconciles_stock(self):
        demand = {}
        products, suppliers, daily, _ = generate(demand)
        result, ledger = backtest(products, suppliers, daily, demand)
        self.assertLess(result['train_end'], result['test_start'])
        self.assertEqual(result['sku_days'], 1440)
        half = result['sku_days']
        self.assertEqual(len(ledger), half * 2)
        for fixed, stockwise in zip(ledger[:half], ledger[half:]):
            self.assertEqual((fixed['sku'], fixed['date'], fixed['simulated_demand']),
                             (stockwise['sku'], stockwise['date'], stockwise['simulated_demand']))
            if fixed['date'] == result['test_start']:
                self.assertEqual(fixed['opening'], stockwise['opening'])
            for row in (fixed, stockwise):
                self.assertEqual(row['opening'] + row['received'] - row['sold'], row['closing'])
                self.assertEqual(row['sold'] + row['unmet'], row['simulated_demand'])
                self.assertGreaterEqual(row['closing'], 0)
