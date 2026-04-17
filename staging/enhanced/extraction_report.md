# Enhanced Plan Staging Extraction Report
Generated: 2026-04-15 00:26:16

## 1. Source Files Discovered

| Filename | Type | Detected Plan | Status | Confidence |
|----------|------|---------------|--------|------------|
| MR.HUSSEIN 1R@.xlsx | xlsx | HN_CLASSIC_2R | usable | high |
| MR.HUSSEIN CLASSIC 1@.xlsx | xlsx | HN_CLASSIC_2 | usable | high |
| MR.HUSSEIN CLASSIC 2@.xlsx | xlsx | HN_CLASSIC_3 | usable | high |
| MR.HUSSEIN CLASSIC 3@.xlsx | xlsx | HN_CLASSIC_4 | usable | high |
| MR.HUSSEIN CLASSIC 4@.xlsx | xlsx | HN_CLASSIC_1R | usable | high |
| MR.HUSSEIN prime 1@.xlsx | xlsx | HN_PRIME_2 | usable | high |
| NGI_Master_Plans-all plans compire.xlsx | xlsx | ALL_PLANS_COMPARISON | usable | high |
| NGI_Master_Plans.xlsx | xlsx | ALL_PLANS_COMPARISON | usable | high |
| NGI_Networks_Comparison.pdf | pdf | REFERENCE | usable | medium |
| NGI_Networks_Premium_Guide--1.pdf | pdf | REFERENCE | usable | medium |

## 2. Plans Directly Supported by Source

| Plan Code | Display Name | Annual Max | Network | Area |
|-----------|-------------|------------|---------|------|
| HN_CLASSIC_2R | Classic Plan-2R | AED 250,000 | HN Standard Plus | Worldwide Excluding USA and Canada |
| HN_CLASSIC_2 | Classic Plan-2 | AED 250,000 | HN Standard Plus | Worldwide Excluding USA and Canada |
| HN_CLASSIC_3 | Classic Plan-3 | AED 250,000 | HN Standard | UAE+Home country |
| HN_CLASSIC_4 | Classic Plan-4 | AED 150,000 | HN Basic Plus | UAE+Home country |
| HN_CLASSIC_1R | Classic Plan-1R | AED 300,000 | HN Advantage | Worldwide Excluding USA and Canada |
| HN_PRIME_2 | Prime Plan-2 | AED 500,000 | HN Premier | Worldwide |

## 3. Plans Still Pending Source

- **HN_PRIME_1**: No direct TOB workbook found for this plan. Do NOT fabricate benefit values.
- **HN_CLASSIC_1**: No direct TOB workbook found for this plan. Do NOT fabricate benefit values.

## 4. Unreadable Files

None.

## 5. Network Mapping Summary

| Plan Code | Network in Source | Mapped Internal |
|-----------|------------------|-----------------|
| HN_CLASSIC_2R | HN Standard Plus | HN Standard Plus |
| HN_CLASSIC_2 | HN Standard Plus (Additional 10% Co-pay applicable | HN Standard Plus |
| HN_CLASSIC_3 | HN Standard | HN Standard |
| HN_CLASSIC_4 | HN Basic Plus | HN Basic Plus |
| HN_CLASSIC_1R | HN Advantage | HN Advantage |
| HN_PRIME_2 | HN Premier | HN Premier |

## 6. Safety Notes

- No live runtime files were modified (data/plans/, data/benefits/, data/rules/)
- Missing plans are explicitly marked `pending_source` with NO fabricated values
- All benefit values come directly from TOB workbook cells
- File-to-plan mapping was verified via the TOB 'Plan Name' field (not filename)
