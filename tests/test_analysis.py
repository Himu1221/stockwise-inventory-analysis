import sys, unittest, math, json, csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from build import generate, purchase_plan

class InventoryTests(unittest.TestCase):
    def row(self,**kw):
        return dict(daily_demand=5,lead_days=5,on_hand=0,on_order=0,unit_cost=2,pack_size=12,**kw)
    def test_reproducible(self): self.assertEqual(generate(),generate())
    def test_continuous_inventory(self):
        _,_,daily,_=generate(); last={}
        for r in daily:
            if r['sku'] in last:self.assertEqual(last[r['sku']],r['opening_stock'])
            self.assertEqual(r['opening_stock']+r['receipts']-r['sales_units'],r['closing_stock'])
            self.assertGreaterEqual(r['closing_stock'],0)
            last[r['sku']]=r['closing_stock']
    def test_pack_rounding(self):
        p=purchase_plan([self.row()])[0]
        self.assertEqual(p['reorder_point'],45)
        self.assertEqual(p['target'],80)
        self.assertEqual(p['recommended_qty'],84)
    def test_zero_budget(self): self.assertEqual(purchase_plan([self.row()],budget=0)[0]['funded_qty'],0)
    def test_partial_pack_budget(self):
        p=purchase_plan([self.row()],budget=25)[0]
        self.assertEqual(p['funded_qty'],12);self.assertEqual(p['remaining_budget'],1)
    def test_inbound_prevents_duplicate_order(self):
        p=self.row();p['on_order']=100
        self.assertEqual(purchase_plan([p])[0]['recommended_qty'],0)
    def test_exact_trigger_boundary(self):
        p=self.row();p['on_hand']=45
        self.assertEqual(purchase_plan([p])[0]['recommended_qty'],36)
    def test_above_trigger_no_order(self):
        p=self.row();p['on_hand']=46
        self.assertEqual(purchase_plan([p])[0]['recommended_qty'],0)
    def test_zero_demand(self):
        p=self.row();p['daily_demand']=0
        self.assertEqual(purchase_plan([p])[0]['recommended_qty'],0)
    def test_budget_invariants(self):
        for budget in [0,1,23.99,24,300,8000]:
            plan=purchase_plan([self.row() for _ in range(48)],budget=budget)
            self.assertLessEqual(sum(p['order_cost'] for p in plan),budget+1e-6)
            self.assertTrue(all(p['funded_qty']%p['pack_size']==0 and 0<=p['funded_qty']<=p['recommended_qty'] for p in plan))
    def test_future_receipts_not_reported(self):
        _,_,daily,orders=generate()
        self.assertEqual(sum(d['receipts'] for d in daily),sum(o['quantity'] for o in orders if o['received_date']))
        self.assertTrue(all(not o['received_date'] or o['received_date']<='2026-10-31' for o in orders))
    def test_sql_demand_matches_source_exposure(self):
        _,_,daily,_=generate()
        payload=json.loads((Path(__file__).resolve().parents[1]/'reports/analysis.json').read_text())
        self.assertEqual(len(payload['rows']),48)
        self.assertEqual(len({p['sku'] for p in payload['rows']}),48)
        for p in payload['rows']:
            exposed=[r for r in daily if r['sku']==p['sku'] and r['closing_stock']>0]
            self.assertAlmostEqual(p['daily_demand'],round(sum(r['sales_units'] for r in exposed)/len(exposed),4))

if __name__=='__main__':unittest.main()
