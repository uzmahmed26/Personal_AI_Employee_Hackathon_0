---
name: odoo-accounting
description: Use this skill for any Odoo ERP / accounting tasks: creating invoices, looking up customers, checking financial reports, recording payments, managing products. Trigger phrases: "create invoice", "Odoo invoice", "check financials", "accounting", "list customers", "customer record", "financial summary", "overdue invoices", "Odoo".
version: 1.0.0
---

# Odoo Accounting Skill

Integrates with Odoo Community Edition (self-hosted) via the Odoo MCP server for accounting, invoicing, and CRM operations. All write operations require human approval — read operations are immediate.

## Objective

Manage business accounting through Odoo: create invoices, track receivables, manage customers, and generate financial summaries for the CEO Briefing.

## Procedure

### Read Operations (No Approval Needed)

**Get financial summary:**
```
Use MCP tool: odoo → get_financial_summary
  period: this_month
```

**List customers:**
```
Use MCP tool: odoo → list_customers
  search: "[optional name filter]"
  limit: 20
```

**List invoices:**
```
Use MCP tool: odoo → list_invoices
  state: posted
  customer_name: "[optional filter]"
```

**Get overdue invoices:**
```
Use MCP tool: odoo → get_overdue_invoices
```

**Search products:**
```
Use MCP tool: odoo → search_products
  query: "[product name]"
```

### Write Operations (Approval Required by Default)

#### Create Invoice (Draft)

Step 1 — Verify customer exists:
```
Use MCP tool: odoo → list_customers
  search: "[customer name]"
```

Step 2 — Create draft invoice (generates approval request):
```
Use MCP tool: odoo → create_invoice_draft
  customer_name: "[name]"
  amount: [number]
  description: "[line description]"
  due_date: "YYYY-MM-DD"
  force_execute: false
```

Step 3 — Create task for approval:
```bash
python run_task_skill.py create -t approval_required \
  -d "Odoo invoice draft for [customer] $[amount] — review required" \
  -p high --approval \
  -m customer="[name]" amount=[amount]
```

Step 4 — After human approves, execute with `force_execute: true`:
```
Use MCP tool: odoo → create_invoice_draft
  customer_name: "[name]"
  amount: [amount]
  description: "[description]"
  force_execute: true
```

#### Create Customer

```
Use MCP tool: odoo → create_customer
  name: "[customer name]"
  email: "[email]"
  phone: "[phone]"
  is_company: false
  force_execute: false   ← creates approval request
```

### Invoice Workflow Integration

When a WhatsApp or email task requests an invoice:

1. Find or create customer in Odoo
2. Create invoice draft (approval request auto-generated)
3. After approval: post invoice in Odoo
4. Send invoice details via email (Email Handler Skill)
5. Update Dashboard

### Weekly Audit (for CEO Briefing)

Every Sunday, the CEO Briefing Skill calls:
```
Use MCP tool: odoo → get_financial_summary
  period: this_week

Use MCP tool: odoo → get_overdue_invoices
```

This data feeds into the Monday Morning CEO Briefing.

## Odoo Setup

Odoo Community must be running locally (or on a cloud VM for Platinum tier).

```bash
# Environment variables required in .env:
ODOO_URL=http://localhost:8069
ODOO_DB=mycompany
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password
```

**Install Odoo Community:**
- Download: https://www.odoo.com/page/community
- Docker: `docker run -p 8069:8069 odoo:19`
- Required modules: Accounting, Invoicing, CRM, Inventory

## Security Rules

- All write operations (create invoice, create customer, record payment) generate approval requests by default
- `force_execute: true` should only be passed AFTER human approval is confirmed
- Financial data never leaves the local Odoo instance
- Odoo credentials are stored in `.env` only — never hardcoded
