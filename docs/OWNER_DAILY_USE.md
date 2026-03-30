# Owner Daily Use Guide

## Scope
- This project currently supports only Remedy 02 plan queries.
- Other plans (Remedy 04/05/06, etc.) are not supported and will return "No answer found."

## How to Run Daily
1. Activate your Python environment if needed.
2. Run the interactive owner mode:

    python scripts/owner_query.py

3. Or run a single question via CLI:

    python scripts/ask_kb.py "Your question here"

## Example Questions

### English
- What is the annual limit for Remedy 02?
- Does Remedy 02 include telemedicine?
- What is the deductible for Remedy 02?
- Is Aster Qusais in the network?
- What wellness benefits are included in Remedy 02?

### Arabic / Mixed
- ما هو annual limit لخطة ريميدي 02؟
- هل ريمدي ٢ فيها حمل؟
- ايه area of coverage بتاعة ريميدي 02؟
- هل Aster Qusais موجود في الشبكة؟

## What the Project Can Answer
- Annual limit, deductible, telemedicine, wellness, maternity, area of coverage, provider network, reimbursement, declaration requirements, pre-existing conditions for Remedy 02
- Network membership for supported providers
- FAQ/training questions (if present in the data)

## What the Project Cannot Answer Yet
- Any plan except Remedy 02
- Dental, optical, exclusions, pre-authorization, or other unsupported benefits
- Provider network for unsupported providers
- Any question outside the loaded data
