#!/usr/bin/env python3
"""CEO Briefing Generator — pulls Odoo data + task system metrics"""

import urllib.request, json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
import yaml

VAULT = Path(r"C:\Users\laptop world\Desktop\Hack00")
TODAY = datetime.now()
WEEK_START = TODAY - timedelta(days=TODAY.weekday())
REPORT_DATE = TODAY.strftime("%Y-%m-%d")

# ── Odoo helpers ──────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:8069/jsonrpc"

def odoo_call(params):
    data = json.dumps({"jsonrpc":"2.0","method":"call","id":1,"params":params}).encode()
    req = urllib.request.Request(BASE_URL, data=data,
                                  headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req).read())

uid = odoo_call({"service":"common","method":"authenticate",
                  "args":["mycompany","admin","admin",{}]})["result"]

def odoo(model, method, args=None, kwargs=None):
    return odoo_call({
        "service":"object","method":"execute_kw",
        "args":["mycompany", uid, "admin", model, method,
                args or [], {"context":{"lang":"en_US","tz":"UTC"}, **(kwargs or {})}]
    })["result"]

# ── 1. ODOO FINANCIAL DATA ────────────────────────────────────────────────────
print("Fetching Odoo financial data...")

month_start  = TODAY.strftime("%Y-%m-01")
week_start_s = WEEK_START.strftime("%Y-%m-%d")
today_s      = TODAY.strftime("%Y-%m-%d")

inv_all = odoo("account.move","search_read",
    [[["move_type","=","out_invoice"],["invoice_date",">=",month_start]]],
    {"fields":["name","amount_total","amount_residual","payment_state",
               "invoice_date","invoice_date_due","partner_id","state"],"limit":200})

inv_week = [i for i in inv_all if (i.get("invoice_date") or "") >= week_start_s]

total_month   = sum(i["amount_total"] for i in inv_all)
paid_month    = sum(i["amount_total"] for i in inv_all if i["payment_state"]=="paid")
outstanding   = sum(i["amount_residual"] for i in inv_all if i["payment_state"]!="paid")
total_week    = sum(i["amount_total"] for i in inv_week)
paid_week     = sum(i["amount_total"] for i in inv_week if i["payment_state"]=="paid")

overdue = odoo("account.move","search_read",
    [[["move_type","=","out_invoice"],["payment_state","!=","paid"],
      ["invoice_date_due","<",today_s],["state","=","posted"]]],
    {"fields":["name","amount_residual","invoice_date_due","partner_id"],"limit":50})
overdue_total = sum(i["amount_residual"] for i in overdue)

customers = odoo("res.partner","search_read",
    [[["customer_rank",">",0]]],
    {"fields":["id","name"],"limit":200})

accounts = odoo("account.account","search_read",
    [[["deprecated","=",False]]],
    {"fields":["code","name","account_type"],"limit":10})

print(f"  {len(inv_all)} invoices | PKR {total_month:,.0f} month | {len(customers)} customers")

# ── 2. TASK SYSTEM DATA ───────────────────────────────────────────────────────
print("Reading task pipeline...")

def parse_frontmatter(path):
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
        if txt.startswith("---"):
            parts = txt.split("---", 2)
            if len(parts) >= 3:
                return yaml.safe_load(parts[1]) or {}, parts[2].strip()
    except Exception:
        pass
    return {}, ""

def tasks_in(folder):
    p = VAULT / folder
    if not p.exists():
        return []
    items = []
    for f in p.iterdir():
        if f.suffix in (".md", ".txt"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            meta, body = parse_frontmatter(f) if f.suffix == ".md" else ({}, "")
            items.append({"name": f.name, "mtime": mtime, "meta": meta, "body": body[:200]})
    return items

completed   = tasks_in("03_Completed_Tasks")
failed      = tasks_in("05_Failed_Tasks")
in_progress = tasks_in("02_In_Progress_Tasks")
pending_q   = tasks_in("01_Incoming_Tasks")
pend_appr   = tasks_in("Pending_Approval")
approved    = tasks_in("Approved")

completed_week = [t for t in completed if t["mtime"] >= WEEK_START]
failed_week    = [t for t in failed    if t["mtime"] >= WEEK_START]

total_processed = len(completed_week) + len(failed_week)
success_rate    = (len(completed_week) / max(1, total_processed)) * 100

type_counter = Counter(t["meta"].get("task_type","unknown") for t in completed_week)
prio_counter = Counter(t["meta"].get("priority","unknown") for t in completed_week)

ledger_files = sorted((VAULT/"Decision_Ledger").glob("*.md")) if (VAULT/"Decision_Ledger").exists() else []

print(f"  {len(completed_week)} completed | {len(failed_week)} failed | {success_rate:.0f}% success rate")

# ── 3. BUILD BRIEFING MARKDOWN ───────────────────────────────────────────────
print("Generating briefing markdown...")

def pkr(n):
    return f"PKR {n:,.0f}"

alert_lines = []
if overdue_total > 0:
    alert_lines.append(f"FINANCE: {len(overdue)} overdue invoice(s) — {pkr(overdue_total)} uncollected")
if success_rate < 85 and total_processed > 0:
    alert_lines.append(f"SYSTEM: Success rate {success_rate:.0f}% is below 85% threshold")
if len(pend_appr) > 3:
    alert_lines.append(f"APPROVAL QUEUE: {len(pend_appr)} items awaiting human approval")
if len(failed_week) > 5:
    alert_lines.append(f"TASKS: {len(failed_week)} failed tasks this week need review")

summary_line = (
    f"This week the AI Employee system processed {total_processed} tasks "
    f"with a {success_rate:.0f}% success rate. "
    f"Revenue collected this week: {pkr(paid_week)} of {pkr(total_week)} invoiced. "
    f"Month-to-date: {pkr(paid_month)} collected of {pkr(total_month)} invoiced."
)
if alert_lines:
    summary_line += f" ALERTS: {len(alert_lines)} issue(s) require attention."
else:
    summary_line += " No critical issues detected."

lines = []
lines.append("---")
lines.append(f"generated: {TODAY.isoformat()}")
lines.append(f"period: {WEEK_START.strftime('%Y-%m-%d')} to {TODAY.strftime('%Y-%m-%d')}")
lines.append("type: monday_briefing")
lines.append("odoo_db: mycompany")
lines.append("---")
lines.append("")
lines.append("# Monday Morning CEO Briefing")
lines.append(f"## {TODAY.strftime('%A, %d %B %Y')}")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Executive Summary")
lines.append("")
lines.append(summary_line)
lines.append("")

# ── Revenue section ──
lines.append("---")
lines.append("")
lines.append("## Revenue (Odoo ERP)")
lines.append("")
lines.append("| Metric | Amount |")
lines.append("|--------|--------|")
lines.append(f"| This Week — Invoiced        | {pkr(total_week)} |")
lines.append(f"| This Week — Collected       | {pkr(paid_week)} |")
lines.append(f"| Month-to-Date Invoiced      | {pkr(total_month)} |")
lines.append(f"| Month-to-Date Collected     | {pkr(paid_month)} |")
lines.append(f"| Outstanding Receivables     | {pkr(outstanding)} |")
lines.append(f"| Overdue (past due, unpaid)  | {pkr(overdue_total)} |")
lines.append("")
lines.append(f"**Active Customers:** {len(customers)}  ")
lines.append(f"**Invoices This Month:** {len(inv_all)} "
             f"({sum(1 for i in inv_all if i['payment_state']=='paid')} paid, "
             f"{sum(1 for i in inv_all if i['payment_state']!='paid')} unpaid)")
lines.append("")

lines.append("### Invoice Detail (This Month)")
lines.append("")
lines.append("| # | Invoice | Customer | Amount | Payment |")
lines.append("|---|---------|----------|--------|---------|")
for idx, inv in enumerate(inv_all, 1):
    status = "PAID" if inv["payment_state"] == "paid" else "UNPAID"
    cust   = inv["partner_id"][1] if inv.get("partner_id") else "—"
    lines.append(f"| {idx} | {inv['name']} | {cust} | {pkr(inv['amount_total'])} | {status} |")
lines.append("")

if overdue:
    lines.append("### Overdue Invoices")
    lines.append("")
    lines.append("| Invoice | Customer | Overdue Amount | Due Date |")
    lines.append("|---------|----------|----------------|----------|")
    for inv in overdue:
        cust = inv["partner_id"][1] if inv.get("partner_id") else "—"
        lines.append(f"| {inv['name']} | {cust} | {pkr(inv['amount_residual'])} | {inv['invoice_date_due']} |")
    lines.append("")
else:
    lines.append("**No overdue invoices — all receivables current.**")
    lines.append("")

# ── Task Performance ──
lines.append("---")
lines.append("")
lines.append("## Task System Performance")
lines.append("")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
lines.append(f"| Completed This Week   | {len(completed_week)} |")
lines.append(f"| Failed This Week      | {len(failed_week)} |")
lines.append(f"| In Progress Now       | {len(in_progress)} |")
lines.append(f"| Pending Queue         | {len(pending_q)} |")
lines.append(f"| Pending Approvals     | {len(pend_appr)} |")
lines.append(f"| Approved Items        | {len(approved)} |")
lines.append(f"| **Success Rate**      | **{success_rate:.1f}%** |")
lines.append(f"| Total Tasks (all time)| {len(completed)} |")
lines.append("")

if type_counter:
    lines.append("### Completed by Task Type (This Week)")
    lines.append("")
    for t, c in type_counter.most_common():
        lines.append(f"- {t.replace('_',' ').title()}: {c}")
    lines.append("")

if prio_counter:
    lines.append("### Completed by Priority (This Week)")
    lines.append("")
    for p, c in prio_counter.most_common():
        lines.append(f"- {p.title()}: {c}")
    lines.append("")

if completed_week:
    lines.append("### Recent Completions (Top 10)")
    lines.append("")
    lines.append("| Task File | Type | Priority | Completed |")
    lines.append("|-----------|------|----------|-----------|")
    for t in sorted(completed_week, key=lambda x: x["mtime"], reverse=True)[:10]:
        tp = t["meta"].get("task_type", "—")
        pr = t["meta"].get("priority", "—")
        ts = t["mtime"].strftime("%m/%d %H:%M")
        lines.append(f"| {t['name'][:50]} | {tp} | {pr} | {ts} |")
    lines.append("")

if failed_week:
    lines.append(f"### Failed Tasks ({len(failed_week)})")
    lines.append("")
    for t in failed_week[:10]:
        rc = t["meta"].get("retry_count", "?")
        lines.append(f"- {t['name']} (retries: {rc})")
    lines.append("")

# ── Bottlenecks & Alerts ──
lines.append("---")
lines.append("")
lines.append("## Bottlenecks & Alerts")
lines.append("")
if alert_lines:
    for a in alert_lines:
        lines.append(f"- **{a}**")
else:
    lines.append("- No critical bottlenecks detected. System operating normally.")
lines.append("")

# ── Recommendations ──
lines.append("---")
lines.append("")
lines.append("## Proactive Recommendations")
lines.append("")
if overdue:
    lines.append(f"1. **Invoice Collection:** Follow up on {len(overdue)} overdue invoice(s) totalling {pkr(overdue_total)}.")
else:
    lines.append("1. **Invoice Collection:** All invoices paid — no follow-up needed.")

lines.append(f"2. **Customer Pipeline:** {len(customers)} active customers in CRM. Consider upsell for existing accounts.")
lines.append(f"3. **Task Queue:** {len(pending_q)} tasks pending — run `python autonomous_system.py` to process.")
lines.append(f"4. **System Health:** {success_rate:.0f}% success rate {'— investigate failed tasks.' if success_rate < 90 else '— system running optimally.'}")

if pend_appr:
    lines.append(f"5. **Approvals Needed:** {len(pend_appr)} item(s) in Pending_Approval/ awaiting review.")
else:
    lines.append("5. **Approvals:** No items pending — approval queue is clear.")

lines.append("")

# ── Upcoming Due Dates ──
lines.append("---")
lines.append("")
lines.append("## Upcoming Invoice Due Dates (Next 7 Days)")
lines.append("")
next_week = (TODAY + timedelta(days=7)).strftime("%Y-%m-%d")
upcoming = [i for i in inv_all
            if today_s <= (i.get("invoice_date_due") or "") <= next_week
            and i["payment_state"] != "paid"]

if upcoming:
    lines.append("| Invoice | Customer | Due Date | Amount |")
    lines.append("|---------|----------|----------|--------|")
    for i in sorted(upcoming, key=lambda x: x.get("invoice_date_due", "")):
        cust = i["partner_id"][1] if i.get("partner_id") else "—"
        lines.append(f"| {i['name']} | {cust} | {i['invoice_date_due']} | {pkr(i['amount_total'])} |")
else:
    lines.append("No invoices due in the next 7 days.")
lines.append("")

# ── Decision Ledger ──
lines.append("---")
lines.append("")
lines.append("## Decision Ledger")
lines.append("")
lines.append(f"Total decision logs on file: **{len(ledger_files)}**")
lines.append("")
for lf in ledger_files[-5:]:
    lines.append(f"- {lf.name}")
lines.append("")

# ── Footer ──
lines.append("---")
lines.append("")
lines.append(f"*Generated: {TODAY.strftime('%Y-%m-%d %H:%M:%S')}*  ")
lines.append("*Data sources: Odoo ERP (mycompany) · Task Pipeline · Decision Ledger*  ")
lines.append("*Generated by Personal AI Employee CEO Briefing System*")
lines.append("")

# ── Save ─────────────────────────────────────────────────────────────────────
briefings_dir = VAULT / "Briefings"
briefings_dir.mkdir(exist_ok=True)
filename  = f"{REPORT_DATE}_Monday_Briefing.md"
out_path  = briefings_dir / filename
out_path.write_text("\n".join(lines), encoding="utf-8")

print(f"\nBriefing saved  : Briefings/{filename}")
print(f"Revenue (week)  : {pkr(total_week)} invoiced / {pkr(paid_week)} paid")
print(f"Revenue (month) : {pkr(total_month)} invoiced / {pkr(paid_month)} paid")
print(f"Overdue         : {len(overdue)} invoice(s) — {pkr(overdue_total)}")
print(f"Tasks completed : {len(completed_week)} (success rate {success_rate:.0f}%)")
print(f"Alerts          : {len(alert_lines)}")
print("\nCEO Briefing DONE!")
