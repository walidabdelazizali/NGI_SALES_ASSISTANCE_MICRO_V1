# Quick Start Guide — Micro Insurance Knowledge Base V1

This is a **5-minute quick start** to get you operational with the knowledge base.

---

## What You Have

A structured knowledge base with:
- **30 FAQ questions** (11 categories)
- **10 insurance plans** (structure ready)
- **30 operational rules** (decision logic)
- **Full documentation** (README + Dashboard)

---

## Getting Started in 3 Steps

### Step 1: Import the Data (2 minutes)

**Option A: Google Sheets** (Recommended for Quick Start)
1. Open Google Sheets
2. Create a new spreadsheet: "Micro Insurance KB V1"
3. Import each CSV file as a separate tab:
   - `FAQ_Questions.csv` → Tab: "FAQ Questions"
   - `Plans_Master.csv` → Tab: "Plans Master"  
   - `Rules_Master.csv` → Tab: "Rules Master"
4. File → Import → Upload → Select CSV → Import to new tab

**Option B: Excel**
1. Open Excel
2. Create new workbook: "Micro Insurance KB V1"
3. Data → From Text/CSV → Import each file to separate worksheet

**Option C: Database**
1. Create three tables: faq_questions, plans_master, rules_master
2. Import CSV files using your database tool
3. Use question_id, plan_id, rule_id as primary keys

---

### Step 2: Explore the Content (2 minutes)

**Key Fields to Know:**

**In FAQ_Questions:**
- `question` — The actual question
- `internal_answer` — Full answer for staff (includes routing, SLAs, escalation)
- `client_answer` — Safe answer for customers (no internal details)
- `category` — Primary classification
- `priority` — High/Medium/Low
- `needs_plan_link`, `needs_rule_link`, `needs_network_check` — Dependency flags

**In Plans_Master:**
- `plan_id` — Unique identifier (PLAN-001, etc.)
- `plan_name` — Display name
- `maternity_rule`, `approval_rule`, `waiting_period` — Key coverage terms

**In Rules_Master:**
- `rule_id` — Unique identifier (RULE-001, etc.)
- `rule_category` — Type of rule (Approval, Claims, Maternity, etc.)
- `internal_usage_note` — How to apply the rule operationally
- `client_safe_summary` — Customer-facing explanation

---

### Step 3: Start Using It (1 minute)

**For Claims Staff:**
```
Search FAQ by category → Use internal_answer → Check dependency flags → 
Reference Rules_Master for decision logic
```

**For Customer Service:**
```
Search FAQ by keyword → Use client_answer ONLY → 
Never expose internal routing or process details
```

**For Operations:**
```
Review Dashboard.md for metrics → Identify gaps → 
Add new content following README instructions
```

---

## Common Use Cases

### "A customer asks: Is maternity covered?"

1. Search FAQ_Questions for "maternity covered"
2. Find FAQ-005
3. Use `client_answer`: 
   > "Maternity coverage depends on your specific plan. Some plans include maternity benefits while others may have waiting periods or exclusions. Please check your policy documents or contact us with your plan details for specific information about your coverage."
4. Check dependency flags: needs_plan_link=Yes, needs_rule_link=Yes
5. Look up customer's plan in Plans_Master → check maternity_rule field
6. Reference Rules_Master RULE-012 for waiting period details

---

### "What's the claim processing SLA?"

1. Search Rules_Master for "Claim Processing SLA"
2. Find RULE-005
3. Use internal_usage_note:
   > "Standard claims: 7-10 business days; Emergency claims: 3-5 business days; Complex cases requiring Medical Director: up to 15 business days"

---

### "Customer disputes a claim rejection"

1. Search FAQ_Questions for "claim rejected"
2. Find FAQ-003 for reason categories
3. Find FAQ-018 for escalation process
4. Reference Rules_Master RULE-023 for escalation path
5. Follow internal process: Claims Officer → Supervisor → Medical Director → Formal Appeal

---

## Important Rules

### ✅ DO:
- Use `internal_answer` for staff operations
- Use `client_answer` for customer communication
- Check dependency flags before responding
- Cross-reference Plans and Rules when needed
- Add new content following README classification guide

### ❌ DON'T:
- Share internal_answer content with customers
- Expose internal routing or staff names
- Invent policy details not in the system
- Ignore dependency flags
- Collapse internal and client answers

---

## Adding New Content

**Quick Decision Tree:**

**Is it a Question + Answer?** → Add to FAQ_Questions
- Example: "How do I change my address?"

**Is it about a Plan's Coverage?** → Add to Plans_Master
- Example: "Basic Plan covers up to $500 for optical"

**Is it Decision Logic or Policy?** → Add to Rules_Master
- Example: "Pharmacy refills must be 30-day supply maximum"

**Is it Network/Provider Data?** → Hold for future network phase
- Example: "Hospital XYZ is in-network"

Full instructions in README → "How to Add New Content Later"

---

## File Locations

```
micro-insurance-kb-v1/
├── data/
│   ├── FAQ_Questions.csv          ← Main knowledge base
│   ├── Plans_Master.csv            ← Plan structures
│   └── Rules_Master.csv            ← Operational rules
├── docs/
│   └── Dashboard.md                ← Metrics and overview
├── README.md                       ← Full documentation
└── QUICK_START.md                  ← This file
```

---

## Getting Help

**For detailed information:**
- Read [README.md](../README.md) — Comprehensive documentation
- Review [Dashboard.md](docs/Dashboard.md) — Metrics and analysis

**For specific questions:**
- How to classify content? → README: "How to Add New Content Later"
- What do dependency flags mean? → README: "Dependency Flags Explained"
- Priority guidelines? → README: "Priority Guidelines"
- Content safety rules? → README: "Content Safety Guidelines"

---

## Next Actions After Quick Start

1. **Train your team** — Walk through the structure with staff
2. **Set up search** — Enable filtering/search in your spreadsheet or database
3. **Customize workflow** — Adapt to your operational processes
4. **Plan enrichment** — Identify priority gaps from Dashboard
5. **Establish updates** — Define who adds content and when

---

## Success Checklist

After 5 minutes, you should be able to:
- ✅ Access all three data files in your tool of choice
- ✅ Search FAQs by category or keyword
- ✅ Distinguish internal vs client-facing answers
- ✅ Look up plan and rule details
- ✅ Understand what dependency flags mean
- ✅ Know how to add new content

---

**You're ready to go!** 🚀

For deeper understanding, read the full README. For operational insights, review the Dashboard.

**Status:** QUICK START COMPLETE