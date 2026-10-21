# Reading the probe output

`scripts/probe.py` prints one block per URL. This file explains each line, how much weight it carries, and the common pressure tactics to look for once you reach a plan page.

## Line by line

| Probe line | What it checks | Weight |
|---|---|---|
| page renders without JS | Whether the HTML has readable text. If not, the page is a JavaScript shell and you need a browser to read it. | None. It tells you which tool to use. |
| pricing link on page | A short link such as `/pricing`, `/plans`, `/premium` on the page | "no" is a moderate warning sign |
| says 'free' out loud | Phrases like "free plan", "100% free", "no credit card" in the visible text | "no" is a moderate warning sign; "YES" is a counter-signal, but confirm it with Step 4 |
| price visible on page | A currency amount in the visible text | Context only. Salary figures and employer posting fees also match. |
| payment provider in code | Stripe, Paddle, Chargebee, Solidgate, etc. referenced in the HTML or scripts | Weak alone, since most paid products use one. Strong when combined with "no pricing link". |
| paywall/funnel code signals | Route and component names such as `choosePlan`, `paywall`, `upsell`, `limitedOffer`, `payment-process`, `subscriptions/order` in the site's own scripts | **Strong** when the site shows no pricing. These names only exist if a plan screen is built into the flow. |
| billing terms in policy pages | Auto-renew, recurring, refund, trial wording in the terms, pricing or refund pages | **Weak.** Nearly every site has this, including ones that are free for your side of the marketplace. |

The probe reports evidence, not a verdict. Always ask whose side the payment is on: a job board's "$299 to post a job" is for employers.

## Calibration (tested 2026-10-22)

| Site | Pricing link | Says free | Funnel code | Billing terms | What it actually is |
|---|---|---|---|---|---|
| globalwork.ai | no | no | 6 kinds (choose-plan, payment-process, upsell, limited offer, subscription API, pricing API) | yes | Hidden paywall at the end of signup |
| himalayas.app | yes | yes | none | yes | Free for job seekers; paid AI tools priced openly |
| weworkremotely.com | yes | no | none | yes (optional "Job Seeker Pro") | Free listings; optional seeker upgrade |
| remoteok.com | yes | no | none (Stripe present) | yes ("Premium", "No free trial") | Listings visible; free-side apply flow not checked |

The pattern that separated the trap: **no pricing link + never says free + funnel code**. Billing terms appeared on all four sites.

A second pattern beats the probe on its own: **"free" that stops just short of the task.** zety.com says "Basic Package FREE", so the probe scores it as a free claim. But the free tier only downloads a plain TXT file, and a usable PDF resume needs a trial that renews at S$34.95 every 4 weeks. Only Step 4 (checking whether the free side completes the user's real task) catches this. Watch for free tiers that let you *build* but not *export*, *browse* but not *apply*, or *preview* but not *use*.

Some sites (zety.com among them) block non-browser requests, so the probe times out. That tells you nothing about the site. Switch to a browser tool and read the pricing page directly.

## Pressure tactics on plan pages

If you reach a plan page through Step 3, note any of these. They suggest the price is designed not to be looked at closely.

- **Countdown timer**. Reload the page and see whether it starts over.
- **Big "50% off" intro price**, with the full renewal price only in the fine print.
- **Price per day** (for example £0.07/day) instead of the amount actually charged.
- **Auto-renew sentence near the button**, such as "Without cancellation ... will automatically charge 155.99 GBP every 1 year".
- **"Lifetime" or "most popular" anchoring**, where one plan exists mainly to make another look cheap.
- **$1 or 7-day trials** that convert into a full subscription unless cancelled.
- **Billing "every 4 weeks"** instead of monthly, which means 13 charges a year rather than 12.

When you report the site, state the real charge (amount and period), not the per-day figure.

## Where the evidence usually hides

- **Terms of use, section "Subscriptions" or "Billing"**: the renewal rule.
- **Refund / money-back policy**: proof the product takes money, even when the homepage never mentions it.
- **JavaScript bundles**: route tables (`/start/payment-process`, `/choose-plan`) and UI strings ("Subscription active · {count} matches unlocked").
- **App store listings**: "In-App Purchases" with actual prices.
- **Trustpilot / Reddit**: "I filled in everything and then...", "charged after the trial", "couldn't cancel".
