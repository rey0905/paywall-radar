# Known sites

Verified observations, newest first within each section. Re-verify any row older than 90 days before relying on it, because pricing changes.

Rules for rows: observed facts only, each with a date and where it was seen. No opinions, no labels like "scam". Verdicts use the names defined in SKILL.md.

## Filtered

| Domain | Verdict | Observed facts | Checked |
|---|---|---|---|
| zety.com | FILTERED: paid | /pricing (viewed from Singapore, prices in SGD): "Basic Package FREE" includes the builder but only "Download in TXT Format". PDF and other formats need Pro: 14-day trial for S$2.95, then "auto-renews at S$34.95 billed every 4 weeks". Annual plan S$71.40, auto-renews yearly. Blocks non-browser requests, so it was checked in a browser. | 2026-10-22 |
| globalwork.ai | FILTERED: hidden paywall | Homepage has no pricing link and never says "free". `/en/journey/2/join/1` opens a "Choose your plan" page with a countdown timer, "50% discount", per-day prices (GBP 0.07/day), and fine print: auto-charges 155.99 GBP every year until cancelled. Terms of use §6: subscriptions renew automatically. The site's scripts contain `choosePlan`, `limitedOffer` and `/start/payment-process` routes. | 2026-10-22 |

## Unverified

| Domain | What is known | What is missing | Checked |
|---|---|---|---|
| remoteok.com | Jobs are listed on the homepage. A "Premium" subscription exists ("No free trial", per /premium). Stripe is loaded. | Whether applying needs Premium | 2026-10-22 |

## OK

| Domain | Verdict | Observed facts | Checked |
|---|---|---|---|
| himalayas.app | FREE TIER OK | Homepage: "Get started for free", "No credit card required". Public /pricing page. Paid AI tools priced openly ($9 and $29/month plans seen in page data). | 2026-10-22 |
| weworkremotely.com | FREE TIER OK | Job listings browsable without an account. Terms mention an optional annual "Job Seeker Pro Subscription"; "$299" on the page is the employer job-posting fee. | 2026-10-22 |
