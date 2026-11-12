"""Arrival-aware screening and out-of-sample policy comparison."""
from collections import defaultdict
from datetime import date, timedelta
from math import ceil
from random import Random


def project_stock(product, orders, snapshot, delay_days=0):
    receipts = defaultdict(int)
    overdue = []
    scheduled = []
    for order in orders:
        if order['sku'] != product['sku'] or order['received_date']:
            continue
        promised = date.fromisoformat(order.get('revised_date') or order['promised_date'])
        entry = dict(order_id=order['order_id'], quantity=order['quantity'],
                     promised_date=str(promised))
        if promised <= snapshot:
            overdue.append(entry)
        else:
            arrival = promised + timedelta(days=delay_days)
            receipts[arrival] += order['quantity']
            scheduled.append(dict(entry, scenario_date=str(arrival)))
    stock = product['on_hand']
    demand = product['daily_demand']
    timeline = []
    for offset in range(1, 15):
        day = snapshot + timedelta(days=offset)
        available = stock + receipts[day]
        stock = max(0, available - demand)
        timeline.append(dict(day=offset, date=str(day), receipts=receipts[day],
                             closing=round(stock, 2), unmet=round(max(0, demand - available), 2)))
    gap = next((r for r in timeline if r['unmet'] > 0), None)
    next_receipt = min((r['scenario_date'] for r in scheduled), default=None)
    if overdue:
        action = 'Confirm overdue PO'
    elif gap and next_receipt:
        action = 'Review inbound timing or quantity'
    elif gap:
        action = 'Review reorder'
    else:
        action = 'Monitor'
    return dict(delay_days=delay_days, timeline=timeline, first_gap=gap,
                next_receipt=next_receipt, overdue=overdue, scheduled=scheduled, action=action)


def backtest(products, suppliers, daily, latent_demand):
    dates = sorted({row['date'] for row in daily})
    train_dates, test_dates = dates[:60], dates[60:]
    train_end = train_dates[-1]
    lead_by_supplier = {s['supplier_id']: s['lead_days'] for s in suppliers}
    observed = {(row['sku'], row['date']): row for row in daily}
    scenarios = [('Fixed cover rule', False), ('StockWise lead-based rule', True)]
    results, ledger = [], []
    for name, adaptive in scenarios:
        for p in products:
            sku, pack = p['sku'], p['pack_size']
            lead = lead_by_supplier[p['supplier_id']]
            exposure = [observed[sku, day]['sales_units'] for day in train_dates
                        if observed[sku, day]['closing_stock'] > 0]
            if not exposure:
                raise ValueError(f'No training demand exposure for {sku}')
            rate = sum(exposure) / len(exposure)
            trigger_days, target_days = (lead + 4, lead + 11) if adaptive else (7, 21)
            stock = observed[sku, train_end]['closing_stock']
            inbound = defaultdict(int)
            for offset, day in enumerate(test_dates):
                opening = stock
                received = inbound.pop(offset, 0)
                demand = latent_demand[sku, day]
                sold = min(opening + received, demand)
                stock = opening + received - sold
                position = stock + sum(inbound.values())
                ordered = 0
                if position <= rate * trigger_days:
                    ordered = ceil(max(0, rate * target_days - position) / pack) * pack
                    # Common lead-time shock for the same SKU and placement day.
                    delay = Random(f'1221:{sku}:{day}').choice([-1, 0, 0, 1, 2, 4, 7])
                    delay += 3 if p['supplier_id'] == 'S3' else 0
                    inbound[offset + max(1, lead + delay)] += ordered
                ledger.append(dict(policy=name, sku=sku, date=day, opening=opening,
                                   received=received, simulated_demand=demand, sold=sold,
                                   unmet=demand-sold, closing=stock, ordered=ordered,
                                   open_units=sum(inbound.values()), closing_value=round(stock*p['unit_cost'], 2),
                                   ordered_cost=round(ordered*p['unit_cost'], 2)))
        records = [r for r in ledger if r['policy'] == name]
        results.append(dict(policy=name, stockout_days=sum(r['unmet'] > 0 for r in records),
                            unmet_units=sum(r['unmet'] for r in records),
                            avg_inventory=round(sum(r['closing_value'] for r in records)/len(test_dates), 2),
                            spend=round(sum(r['ordered_cost'] for r in records), 2),
                            ending_open_units=sum(r['open_units'] for r in records if r['date'] == test_dates[-1])))
    return dict(train_start=train_dates[0], train_end=train_end, test_start=test_dates[0],
                test_end=test_dates[-1], sku_days=len(products)*len(test_dates), results=results), ledger
