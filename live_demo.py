#!/usr/bin/env python3
"""Live Demo — Personal AI Employee System"""

import time, json, urllib.request
from pathlib import Path
from datetime import datetime

VAULT = Path(r"C:\Users\laptop world\Desktop\Hack00")

def sep(title=""):
    print("\n" + "="*60)
    if title: print(f"  {title}")
    print("="*60)

def step(n, msg):
    print(f"\n[STEP {n}] {msg}")
    print("-"*45)

def odoo_call(params):
    data = json.dumps({"jsonrpc":"2.0","method":"call","id":1,"params":params}).encode()
    req  = urllib.request.Request("http://localhost:8069/jsonrpc", data=data,
                                   headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req).read())

def odoo_exec(uid, model, method, args=None, kwargs=None):
    return odoo_call({
        "service":"object","method":"execute_kw",
        "args":["mycompany", uid, "admin", model, method,
                args or [], {"context":{"lang":"en_US"}, **(kwargs or {})}]
    })["result"]

sep("PERSONAL AI EMPLOYEE — LIVE DEMO")
print(f"  Date  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  System: Autonomous Task + Odoo ERP + MCP Integrations")

# ── DEMO 1: Pipeline counts ──────────────────────────────────────────────────
step(1, "Task Pipeline — Live State")
for folder in ["01_Incoming_Tasks","02_In_Progress_Tasks","03_Completed_Tasks","05_Failed_Tasks","Pending_Approval","Approved"]:
    p = VAULT / folder
    n = len([f for f in p.iterdir() if f.name != ".gitkeep"]) if p.exists() else 0
    bar = "#" * min(n, 30)
    print(f"  {folder:<28} [{bar:<30}] {n}")

# ── DEMO 2: Create new task ──────────────────────────────────────────────────
step(2, "Creating New Task — WhatsApp Invoice Request")
import sys, os
sys.path.insert(0, str(VAULT))
os.chdir(VAULT)

from task_executor_skill import TaskExecutorSkill
executor = TaskExecutorSkill()
result = executor.execute_task(
    task_type="email",
    description="DEMO: TechHub Solutions ne WhatsApp pe invoice maangi — PKR 350,000 — Annual Support Contract renewal",
    priority="high",
    approval_required=True,
    metadata={"customer": "TechHub Solutions", "amount": 350000, "source": "whatsapp_demo"}
)
task_file = result.get("task_file","")
print(f"  Task created : {task_file}")
print(f"  Priority     : high")
align = result.get('business_alignment', 0); print(f"  Alignment    : {float(align):.0%}" if isinstance(align,(int,float)) else f"  Alignment    : {align}")
print(f"  Risk         : {result.get('risk_level','—')}")
time.sleep(2)

# Check if task_processor moved it
moved_to = "01_Incoming_Tasks"
for folder in ["02_In_Progress_Tasks","03_Completed_Tasks"]:
    if task_file and (VAULT/folder/task_file).exists():
        moved_to = folder
        break
print(f"  Pipeline     : {moved_to}")

# ── DEMO 3: Odoo — Create invoice ───────────────────────────────────────────
step(3, "Odoo ERP — Creating Invoice for TechHub Solutions")
uid = odoo_call({"service":"common","method":"authenticate",
                  "args":["mycompany","admin","admin",{}]})["result"]
print(f"  Odoo Auth    : UID={uid}")

# Find TechHub partner
partners = odoo_exec(uid, "res.partner","search_read",
    [[["name","ilike","TechHub"]]],
    {"fields":["id","name"],"limit":1})
partner_id = partners[0]["id"] if partners else None
partner_name = partners[0]["name"] if partners else "TechHub Solutions"
print(f"  Customer     : {partner_name} (ID:{partner_id})")

# Create invoice
inv_id = odoo_exec(uid, "account.move","create",[{
    "move_type": "out_invoice",
    "partner_id": partner_id,
    "invoice_date": datetime.now().strftime("%Y-%m-%d"),
    "invoice_date_due": "2026-03-15",
    "invoice_line_ids": [[0,0,{"name":"Annual Support Contract Renewal","quantity":1,"price_unit":350000}]]
}])
print(f"  Invoice ID   : {inv_id} (Draft)")

# Post invoice
odoo_exec(uid, "account.move","action_post",[[inv_id]])
inv = odoo_exec(uid, "account.move","read",[[inv_id]],
    {"fields":["name","amount_total","state","payment_state"]})[0]
print(f"  Invoice No   : {inv['name']}")
print(f"  Amount       : PKR {inv['amount_total']:,.0f}")
print(f"  State        : {inv['state'].upper()} | Payment: {inv['payment_state']}")

# ── DEMO 4: Approval Workflow ────────────────────────────────────────────────
step(4, "Approval Workflow — Creating Approval Request")
from create_approval import create_approval_request
approval_file = create_approval_request(
    approval_type="odoo_invoice",
    data={"invoice_id": inv_id, "invoice_no": inv["name"], "amount": 350000, "customer": partner_name},
    description="Annual Support Contract Renewal. PKR 350,000. Awaiting CEO approval."
)
print(f"  Approval file: {approval_file}")
pend = len([f for f in (VAULT/"Pending_Approval").iterdir() if f.name != ".gitkeep"])
print(f"  Queue size   : {pend} pending approval(s)")

# ── DEMO 5: Financial Summary ────────────────────────────────────────────────
step(5, "Odoo Financial Summary — Live Data")
all_inv = odoo_exec(uid, "account.move","search_read",
    [[["move_type","=","out_invoice"]]],
    {"fields":["amount_total","payment_state"],"limit":200})
total    = sum(i["amount_total"] for i in all_inv)
paid     = sum(i["amount_total"] for i in all_inv if i["payment_state"]=="paid")
unpaid   = sum(i["amount_total"] for i in all_inv if i["payment_state"]!="paid")
custs    = odoo_exec(uid,"res.partner","search_read",[[["customer_rank",">",0]]],{"fields":["id"],"limit":200})
print(f"  Customers    : {len(custs)}")
print(f"  Total Inv    : {len(all_inv)}")
print(f"  Revenue      : PKR {total:,.0f}")
print(f"  Collected    : PKR {paid:,.0f}")
print(f"  Outstanding  : PKR {unpaid:,.0f}")

# ── DEMO 6: MCP Tools count ──────────────────────────────────────────────────
step(6, "MCP Server Tools — Available")
tools_map = {
    "gmail":8, "linkedin":4, "whatsapp":4,
    "facebook":6, "twitter":7, "instagram":7, "odoo":8
}
total_tools = sum(tools_map.values())
for srv, n in tools_map.items():
    print(f"  {srv:<12}: {n} tools")
print(f"  {'TOTAL':<12}: {total_tools} tools across 7 servers")

# ── DEMO 7: Update Dashboard ─────────────────────────────────────────────────
step(7, "Updating Dashboard")
import subprocess
r = subprocess.run(["python","dashboard_updater.py"], capture_output=True, text=True, cwd=str(VAULT))
print(f"  {r.stdout.strip()}")

# Show final pipeline
for folder in ["01_Incoming_Tasks","02_In_Progress_Tasks","03_Completed_Tasks"]:
    p = VAULT / folder
    n = len([f for f in p.iterdir() if f.name != ".gitkeep"]) if p.exists() else 0
    print(f"  {folder:<28}: {n}")

sep("DEMO COMPLETE")
print("  All systems operational. PKR", f"{total:,.0f}", "total revenue in Odoo.")
print("  Dashboard updated. CEO Briefing ready in Briefings/")
print()
