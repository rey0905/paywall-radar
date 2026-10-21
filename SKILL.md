---
name: paywall-radar
description: Screen websites, apps and online tools for hidden paywalls before recommending them, meaning the kind that make you answer a long signup quiz or upload your resume and only then reveal you must buy a plan to use anything. Use this skill whenever you are about to recommend, list or compare websites, apps, platforms or online tools (job boards, remote-work sites, resume builders, AI tools, course or learning platforms, "free" alternatives), whenever the user asks whether a site is free, legit or worth signing up for, pastes a signup/onboarding/"journey" link, or complains that a site made them pay after they filled everything in. Also use it when the user asks for "any sites/tools/apps for X", "a free way to do X", or says they got tricked into paying. Use it even when the user did not mention price, because an unscreened recommendation that ends in a paywall wastes their time.
---

# Paywall Radar

Some sites are built as a funnel: a friendly "Try it now" button, ten screens of questions about your goals, a resume upload, sometimes an email, and only on the last screen a "Choose your plan" page with a countdown timer. By then the user has invested twenty minutes and handed over personal data. This skill makes sure you never send the user into one of those without warning, and that you can tell, without signing up yourself, whether a site is one of them.

## What counts as a trap

A site gets filtered when **the thing the user came to do cannot be done without paying**. It is a *hidden* paywall when the price only appears after the user has invested effort (questionnaire, upload, account).

Judge the free side by the user's actual task. A free tier that cannot finish the task counts as paid: a job site that lets you see three listings, a resume builder that only exports a watermarked PDF, an AI tool whose "free" plan is a single preview.

Products that charge openly are not traps, but they are still paid. Put them in the filtered line marked as openly priced, unless the user has said they are happy to pay.

Many platforms are two-sided, so check the user's side. On job boards employers usually pay to post and job seekers browse and apply for free. An optional "Pro" upgrade for seekers is fine as long as the free side completes the task.

## Ground rules

These exist because checking a site should never cost the user what the trap would have cost them.

- Do not sign up, do not enter an email, name, phone number or resume, and do not click "Get access", "Start trial" or any purchase button. Handing personal data to a site in order to find out whether it is a trap defeats the purpose.
- Read-only actions are fine: loading pages, reading their text, reading the JavaScript the site serves to every visitor, and editing step numbers in a URL to look ahead.
- Clicking through a questionnaire using only non-personal choices (for example "What role are you looking for?") needs the user's explicit OK for that specific site. Stop at the first screen that asks for an email or account.
- Report what you observed, with the date. Do not call a company a scam; describe the facts ("no pricing page; the plan page appears after signup; auto-renews at £155.99/year") and let the user judge.

## Workflow

Work from cheapest to most expensive and stop as soon as the verdict is clear. When you are screening several candidates for a recommendation list, run Steps 1 and 2 for all of them, and go deeper only on the ones that are still unclear.

**Step 0: Check the ledger.** Look the domain up in `references/known-sites.md`. Reuse an entry that is less than 90 days old. Re-verify anything older, because pricing changes.

**Step 1: Read public information outside the funnel.**
- Homepage: does it say "free" anywhere, and is there a pricing link in the navigation or footer?
- Pricing page, FAQ and terms of use. In the terms, search for *subscription, auto-renew, recurring, trial, refund*. A refund or "money-back" policy on a site that never shows a price is telling.
- If the site has a mobile app, check its App Store or Google Play listing. The "In-App Purchases" section lists real prices.
- Reviews: web search `"<site>" reddit`, `"<site>" trustpilot`, and `"<site>" subscription OR charged OR refund OR paywall`. Look for "filled everything in, then it asked me to pay" and for surprise renewals.

**Step 2: Run the probe.** From this skill's directory:

```bash
python3 scripts/probe.py https://example.com
```

It downloads only what any visitor's browser downloads (the HTML, the site's own scripts, public policy pages) and reports pricing links, "free" claims, payment providers, paywall routes in the code, and billing language in the terms. It uses only the Python standard library and needs no keys. Read its output using `references/signals.md`. If it reports that the page needs JavaScript to render, or it cannot fetch the page, open the page in a browser tool if you have one and read the rendered text and the list of loaded resources instead.

**Step 3: Look ahead in the funnel by URL.** Funnels often number their steps in the address: `/journey/2/join/10`, `/onboarding/step-3`, `?step=4`. Try other numbers, especially the first and last, and the bare path. Pages are sometimes not locked to the order you are meant to see them in, so you may land straight on the plan page. This is read-only navigation, so it is fine.

**Step 4: Test the user's actual task on the free side.** For a job board, open one listing and see whether the apply link works without an account. For a resume builder, find out whether export is free. For an AI tool, find out whether one real run is possible without a card. One concrete check like this is worth more than any amount of marketing copy.

**Step 5: Decide** using the evidence weighting below and the verdict list.

## Weighing the evidence

Testing on real job sites showed that **billing terms appear on almost every site**, including job boards that are genuinely free for seekers, so subscription language in the terms means little on its own. The signals that actually separate traps from honest sites are these.

Strong signs of a hidden paywall:
- a plan or price page that only shows up at the end of the onboarding flow;
- paywall routes in the code (choose-plan, paywall, upsell, limited-offer, payment-process) on a site that shows no pricing anywhere;
- pressure tactics on the plan page: countdown timer, "50% off" intro price, price shown per day, renewal amount in small print;
- reviews describing pay-after-onboarding or surprise charges.

Moderate signs:
- no pricing link anywhere on the site;
- the site never says "free";
- it asks questions before showing you any of the product (for example, no job listings you can browse);
- a prominent money-back guarantee with no visible price.

Counter-signals:
- the site says "free" plainly and Step 4 confirms the free side completes the task;
- a pricing page that lists a free tier;
- core content you can browse without an account.

**When you cannot find evidence that the free side works, do not present the site as free.** A product that really is free says so loudly, because "free" is its best selling point. A site that asks for effort first and never says "free" has to prove otherwise.

## Verdicts

| Verdict | Meaning | Where it goes |
|---|---|---|
| FREE | Core task is free | Recommend |
| FREE TIER OK | Free side completes the task; paid extras exist | Recommend, and state what is free and what costs money |
| UNVERIFIED | Not enough evidence either way | Separate "unverified, may charge" note, with what is unknown |
| FILTERED: hidden paywall | Core task needs payment, and the price is revealed only after effort | Filtered line |
| FILTERED: paid | Core task needs payment, priced openly | Filtered line, unless the user is fine paying |

## Output format

Write in the user's language. Lead with the recommendations, and put the filtered sites in one short block at the end. They still get mentioned, so that the user recognizes them if they come across them later.

Example (user asking for remote job sites):

```
**Worth using**
| Site | What you get for free |
|---|---|
| Himalayas | Browse and apply for free; AI job tools cost extra ($29/month) |
| ... | ... |

**Unverified**: Example.io. No price on the homepage; couldn't confirm whether applying needs a membership.

**Filtered**: globalwork.ai. No pricing page; a plan screen appears after the signup quiz (countdown timer, "50% off", per-day price), and the fine print says it auto-renews at £155.99/year (checked 2026-10-22).
```

Keep the evidence to one clause per site. Offer the detailed findings if the user wants them.

## When the user is already stuck on a site

If the user pastes a link they are halfway through, or have just been surprised by, answer directly:
1. Is there any free path to what they want? If not, say so.
2. What will it really cost, including the auto-renew amount and billing period?
3. If they already entered data or a card: suggest checking for an active subscription and cancelling it, and emailing the site's contact address to request account and data deletion. Many terms grant the site a broad license to user uploads, so deletion is worth asking for.
4. Offer free alternatives, screened with this same workflow.

## Updating the ledger

After you verify a site, add or update its row in `references/known-sites.md` with the date, the verdict and one or two observed facts with where you saw them. Facts only, no opinions. If the skill directory is read-only, tell the user the row you would add.
