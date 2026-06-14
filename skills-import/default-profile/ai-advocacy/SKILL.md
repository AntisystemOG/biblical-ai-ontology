---
title: AI Investment Advocacy
name: ai-advocacy
description: |
  Draft ROI communications, business justifications, and leadership briefs for AI
  tooling investments. Anchors on concrete project outcomes, cost comparisons,
  and plain-language management communication. Built around the Intralox PLCTools
  showcase as proof point.
---

# AI Investment Advocacy

## Trigger
User wants to promote AI value to employer, needs ROI case study, draft emails, or business justification for AI tooling investment.

## Context
- Employer is Intralox (manufacturing / industrial automation)
- Showcase project: Degater PLC Tool BST33/35 (Allen-Bradley Micro870 diagnostics)
- Cost basis: ~$20/month AI subscription vs. $5K–$15K commercial equivalent
- Target audience: Non-technical plant / operations management

## Steps
1. Reference `~/.hermes/profiles/ai-advocate/workspace/AI_ADVOCATE_BRIEF.md`
2. Pull key metrics from PLCTools project: capabilities, dev time, cost comparison
3. Draft email / document tailored to Intralox leadership tone
4. Prepare FAQ addressing objections: security, maintenance, vendor overlap, etc.
5. Always anchor on ROI numbers and concrete outcomes

## Workflow
When asked for a draft:
1. Load `references/plctools-showcase.md` for the hard numbers
2. Load `templates/roi-email.md` as the starter email
3. Load `templates/roi-faq.md` for objection responses
4. Customize placeholders and tone to match the specific audience

## File Locations
- Profile config: `~/.hermes/profiles/ai-advocate/config.yaml`
- Profile SOU: `~/.hermes/profiles/ai-advocate/SOUL.md`
- Briefing doc: `~/.hermes/profiles/ai-advocate/workspace/AI_ADVOCATE_BRIEF.md`
- Source reference: `~/.hermes/profiles/ai-advocate/workspace/plc-tools-src/`
- Project memory: `~/.hermes/profiles/ai-advocate/workspace/PROJECT_MEMORY.md`

## Support Files
- `references/plctools-showcase.md` — Key metrics, capability list, and cost comparison for the PLCTools showcase
- `templates/roi-email.md` — Ready-to-customize email template for leadership
- `templates/roi-faq.md` — Anticipated objections and scripted responses

## Tips
- Lead with business outcome, not technology
- Use bullet points and scanability
- Anticipate objections before they arise
- Ask is specific and small ($250–$500/year)
- Have Phase 2 ready to show it is not a one-off

## Pitfalls
- **Do not get too technical.** If the draft reads like a spec sheet, it is wrong. Management signs budgets, not code.
- **Do not oversell the AI.** Position it as an amplifier of existing expertise, not a magic replacement.
- **Avoid cloud / data fears.** Explicitly state the generated tool runs locally; the subscription is only for development assistance.
- **Do not skip the demo.** Email opens the door, but a live demo (I/O lights flipping, timeline replay) closes the deal. Always be ready to show the tool connected to a PLC.
- **Generic vendor comparisons backfire.** Frame it as "tailored to our exact machine layout" rather than just "cheaper than vendor X."
