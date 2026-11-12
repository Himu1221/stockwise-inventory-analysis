"""Reproducible synthetic inventory case study. Python standard library only."""
import csv, json, math, random, sqlite3
from datetime import date, timedelta
from pathlib import Path
from evaluate import backtest, project_stock

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = date(2026, 10, 31)
START = SNAPSHOT - timedelta(days=89)

def write_csv(name, rows):
    with (ROOT/'data'/name).open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def generate(latent_demand=None):
    rng=random.Random(1221)
    suppliers=[dict(supplier_id=f'S{i+1}', supplier=n, lead_days=l) for i,(n,l) in enumerate([
        ('Prairie Distribution',5),('Northline Foods',8),('Summit Supply',12),('Local Harvest',3)])]
    names={
        'Beverages':['Cold brew','Sparkling water','Orange juice','Green tea','Cola','Oat latte','Energy drink','Mineral water'],
        'Snacks':['Trail mix','Sea salt chips','Protein bar','Dark chocolate','Popcorn','Rice crackers','Roasted almonds','Granola bites'],
        'Pantry':['Basmati rice','Pasta','Tomato sauce','Peanut butter','Rolled oats','Canned beans','Olive oil','Honey'],
        'Household':['Dish soap','Paper towels','Laundry pods','Bin liners','Hand soap','Surface spray','Sponges','Tissues'],
        'Fresh':['Greek yogurt','Cheddar','Milk','Eggs','Hummus','Salad kit','Butter','Tofu'],
        'Personal care':['Shampoo','Toothpaste','Body wash','Deodorant','Lip balm','Sunscreen','Hand cream','Dental floss']}
    products=[]; daily=[]; orders=[]
    for i,(cat,name) in enumerate((c,n) for c,ns in names.items() for n in ns):
        sid=i%4; lead=suppliers[sid]['lead_days']; base=2+i%9
        cost=round(rng.uniform(1.5,12),2); pack=[6,12,24][i%3]
        p=dict(sku=f'SW-{i+1:03}',product=name,category=cat,supplier_id=f'S{sid+1}',unit_cost=cost,unit_price=round(cost*1.65,2),pack_size=pack)
        products.append(p)
        # Scheduled historical orders create an imperfect, intentionally varied replenishment pattern.
        arrivals={}; open_qty=0
        for j,offset in enumerate(range(0,90,14+(i%4)*2)):
            ordered=START+timedelta(days=offset)
            delay=rng.choice([-1,0,0,1,2,4,7])+(3 if sid==2 else 0)
            received=ordered+timedelta(days=lead+delay)
            qty=math.ceil(base*(12+(i%5)*2)/pack)*pack
            if i%11==0: qty*=2
            # Only the observed receipt date is published; future delivery is unknown at snapshot.
            observed=received if received<=SNAPSHOT else None
            orders.append(dict(order_id=f'PO-{i+1:03}-{j+1:02}',sku=p['sku'],supplier_id=p['supplier_id'],ordered_date=str(ordered),promised_date=str(ordered+timedelta(days=lead)),received_date=str(observed) if observed else '',quantity=qty))
            if observed: arrivals[str(observed)]=arrivals.get(str(observed),0)+qty
            else: open_qty+=qty
        stock=base*(7 if i%11 else 70)
        for d in range(90):
            day=START+timedelta(days=d); opening=stock; receipt=arrivals.get(str(day),0)
            available=opening+receipt
            # Latent demand drives simulated transactions and held-out policy evaluation.
            wanted=max(0,round(rng.gauss(base*(1.2 if day.weekday()>=5 else 1),base*.38)))
            if latent_demand is not None:
                latent_demand[p['sku'], str(day)] = wanted
            sales=min(available,wanted); stock=available-sales
            daily.append(dict(date=str(day),sku=p['sku'],opening_stock=opening,receipts=receipt,sales_units=sales,closing_stock=stock,fully_available=int(stock>0)))
    return products,suppliers,daily,orders

def purchase_plan(rows, demand_factor=1, lead_factor=1, safety_days=4, review_days=7, budget=8000):
    remaining=budget; result=[]
    # Fixed baseline risk order: this makes Python, browser and Excel allocations reproducible.
    for p in rows:
        demand=p['daily_demand']*demand_factor
        lead=p['lead_days']*lead_factor
        position=p['on_hand']+p['on_order']
        rop=demand*(lead+safety_days)
        target=demand*(lead+safety_days+review_days)
        needed=math.ceil(max(0,target-position)/p['pack_size'])*p['pack_size'] if position<=rop else 0
        funded=min(needed,math.floor((remaining+1e-8)/(p['unit_cost']*p['pack_size']))*p['pack_size'])
        cost=round(funded*p['unit_cost'],2); remaining=round(remaining-cost,2)
        result.append(dict(**p,reorder_point=rop,target=target,recommended_qty=needed,funded_qty=funded,order_cost=cost,remaining_budget=remaining))
    return result

def build():
    for d in ['data','reports','sql','docs','powerbi','tests']: (ROOT/d).mkdir(exist_ok=True)
    latent_demand = {}
    products,suppliers,daily,orders=generate(latent_demand)
    for name,rows in [('products.csv',products),('suppliers.csv',suppliers),('daily_inventory.csv',daily),('purchase_orders.csv',orders)]: write_csv(name,rows)
    db=sqlite3.connect(':memory:')
    for table,rows in [('products',products),('suppliers',suppliers),('daily_inventory',daily),('purchase_orders',orders)]:
        types={k:('REAL' if isinstance(v,float) else 'INTEGER' if isinstance(v,int) else 'TEXT') for k,v in rows[0].items()}
        db.execute(f'CREATE TABLE {table} ('+','.join(f'{k} {v}' for k,v in types.items())+')')
        db.executemany(f'INSERT INTO {table} VALUES ('+','.join('?' for _ in types)+')',[list(r.values()) for r in rows])
    db.row_factory=sqlite3.Row
    sql=(ROOT/'sql/inventory.sql').read_text()
    rows=[dict(r) for r in db.execute(sql)]
    # Baseline priority uses on-hand cover, then SKU. Zero-demand stock sorts last.
    rows.sort(key=lambda p:(p['on_hand']/p['daily_demand'] if p['daily_demand'] else 99999,p['sku']))
    for i,p in enumerate(rows): p['priority']=i+1
    write_csv('planning_inputs.csv',rows)
    supplier_metrics=[]
    for s in suppliers:
        pos=[o for o in orders if o['supplier_id']==s['supplier_id']]
        closed=[o for o in pos if o['received_date']]
        overdue=[o for o in pos if not o['received_date'] and o['promised_date']<=str(SNAPSHOT)]
        ontime=sum(o['received_date']<=o['promised_date'] for o in closed)
        supplier_metrics.append(dict(**s,delivered=len(closed),on_time=ontime,overdue_open=len(overdue),open_orders=sum(not o['received_date'] for o in pos),observed_lead=round(sum((date.fromisoformat(o['received_date'])-date.fromisoformat(o['ordered_date'])).days for o in closed)/len(closed),2)))
    trend=[]
    for d in range(90):
        day=str(START+timedelta(days=d)); records=[x for x in daily if x['date']==day]
        trend.append(dict(date=day,available=sum(x['fully_available'] for x in records),sales=sum(x['sales_units'] for x in records)))
    # Grain, balance, receipt reconciliation and field validity gates run on every build.
    checks={
        'Unique SKU/day grain':len({(x['sku'],x['date']) for x in daily})==len(daily),
        'Nonnegative stock and sales':all(min(x['opening_stock'],x['receipts'],x['sales_units'],x['closing_stock'])>=0 for x in daily),
        'Daily inventory balance':all(x['opening_stock']+x['receipts']-x['sales_units']==x['closing_stock'] for x in daily),
        'Observed receipts reconcile':sum(x['receipts'] for x in daily)==sum(o['quantity'] for o in orders if o['received_date']),
        'Foreign keys valid':all(x['sku'] in {p['sku'] for p in products} for x in daily+orders),
        '90 observations per SKU':all(sum(x['sku']==p['sku'] for x in daily)==90 for p in products),
        'Demand exposure available':all(p['in_stock_days']>0 for p in rows),
        'Positive unit costs and packs':all(p['unit_cost']>0 and p['pack_size']>0 for p in rows)}
    assert all(checks.values()),checks
    payload=dict(snapshot=str(SNAPSHOT),start=str(START),currency='CAD',seed=1221,rows=rows,suppliers=supplier_metrics,trend=trend,checks=checks)
    # Simulate a buyer obtaining revised arrival commitments for some open orders.
    # These commitments are independent of the generator's hidden receipt dates.
    open_orders = [o for o in orders if not o['received_date']]
    confirmations = [
        dict(order_id=o['order_id'], sku=o['sku'], confirmation_date=str(SNAPSHOT),
             revised_date=str(SNAPSHOT + timedelta(days=2 + index % 9)))
        for index, o in enumerate(open_orders) if index % 3 == 0
    ]
    write_csv('inbound_confirmations.csv', confirmations)
    revised = {row['order_id']: row['revised_date'] for row in confirmations}
    projected_orders = [dict(o, revised_date=revised.get(o['order_id'])) for o in open_orders]
    payload['projections'] = {
        p['sku']: [project_stock(p, projected_orders, SNAPSHOT, delay) for delay in (0, 3)]
        for p in rows
    }
    payload['backtest'], ledger = backtest(products, suppliers, daily, latent_demand)
    write_csv('policy_backtest_daily.csv', ledger)
    write_csv('policy_backtest_summary.csv', payload['backtest']['results'])
    (ROOT/'reports/analysis.json').write_text(json.dumps(payload,indent=2))
    plan=purchase_plan(rows); write_csv('baseline_purchase_plan.csv',plan)
    html=(ROOT/'src/dashboard.html').read_text(encoding='utf-8').replace('__DATA__',json.dumps(payload))
    (ROOT/'reports/dashboard.html').write_text(html,encoding='utf-8')
    db.commit()
    db.backup(sqlite3.connect(ROOT/'reports/stockwise.sqlite'))
    print(json.dumps(dict(skus=len(rows),observations=len(daily),orders=len(orders),checks=len(checks),baseline_spend=round(sum(p['order_cost'] for p in plan),2),recommended=sum(p['recommended_qty']>0 for p in plan))))

if __name__=='__main__': build()
