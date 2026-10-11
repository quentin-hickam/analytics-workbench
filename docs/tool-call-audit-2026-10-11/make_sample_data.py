"""Synthetic retail orders with seeded quality issues (seed 7)."""
import csv, random, datetime as dt, sys
from pathlib import Path
random.seed(7)
out = Path(sys.argv[1])
regions = ["North", "South", "East", "West"]
ret_rate = {"North": .06, "South": .11, "East": .08, "West": .15}
customers = []
for i in range(1, 401):
    customers.append({"customer_id": f"C{i:04d}", "region": random.choice(regions),
                      "segment": random.choice(["consumer", "business"]),
                      "signup_date": (dt.date(2024,1,1)+dt.timedelta(days=random.randint(0,800))).isoformat()})
with open(out/"customers.csv", "w", newline="") as f:
    w = csv.DictWriter(f, customers[0].keys()); w.writeheader(); w.writerows(customers)
rows = []
for i in range(1, 2401):
    c = random.choice(customers)
    if i % 97 == 0:  # orphan customer ids (partial extract)
        cid = f"C{random.randint(900,950):04d}"
    else:
        cid = c["customer_id"]
    d = dt.date(2026,1,1)+dt.timedelta(days=random.randint(0,180))
    region = c["region"]
    if i % 41 == 0: region = " " + region.lower() + " "      # whitespace/case variants
    elif i % 53 == 0: region = region.upper()
    amount = round(random.lognormvariate(4, .6), 2)
    if i % 67 == 0: amount = -999                             # sentinel
    returned = "Y" if random.random() < ret_rate[c["region"]] else "N"
    date_s = d.isoformat() if i % 29 else d.strftime("%m/%d/%Y")  # mixed formats
    rows.append({"order_id": f"O{i:05d}", "customer_id": cid, "order_date": date_s,
                 "region": region, "channel": random.choice(["web","store","phone"]),
                 "amount": amount, "returned": returned})
rows += [dict(r) for r in random.sample(rows, 12)]           # exact duplicate rows
random.shuffle(rows)
with open(out/"orders.csv", "w", newline="") as f:
    w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(customers), len(rows))
