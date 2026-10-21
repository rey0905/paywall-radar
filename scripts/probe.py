#!/usr/bin/env python3
"""paywall-radar probe: look for hidden-paywall evidence without signing up.

Reads only what any visitor's browser downloads anyway: the page HTML, the
site's own JavaScript bundles, and a few public policy pages. It never submits
a form, creates an account, or sends personal data.

Usage:
    python3 scripts/probe.py https://example.com [https://another.site ...]
    python3 scripts/probe.py --json https://example.com
    python3 scripts/probe.py --zh https://example.com    (labels in Chinese)

The output is evidence, not a verdict. SKILL.md explains how to weigh it.
Pure standard library, no dependencies, no API keys.
"""

import json
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
TIMEOUT = 15
MAX_BYTES = 6 * 1024 * 1024
MAX_SCRIPTS = 40
MAX_HITS_PER_SIGNAL = 4

# Payment and subscription-billing providers. Loading one of these on a page
# that never mentions a price is a strong hint that a checkout is coming.
PAYMENT_PROVIDERS = {
    "Stripe": r"js\.stripe\.com|stripe\.com/v3|pk_live_[0-9A-Za-z]{8}",
    "Paddle": r"cdn\.paddle\.com|paddle\.js",
    "Chargebee": r"chargebee\.com",
    "Recurly": r"recurly\.com",
    "Solidgate": r"solidgate\.com",
    "Primer": r"primer\.io",
    "Braintree": r"braintreegateway\.com|braintree-api",
    "Checkout.com": r"checkout\.com/|frames\.checkout",
    "Adyen": r"adyen\.com",
    "RevenueCat": r"revenuecat\.com",
    "Lemon Squeezy": r"lemonsqueezy\.com",
    "FastSpring": r"fastspring\.com",
    "PayPal": r"paypal\.com/sdk|paypalobjects\.com",
}

# Route names and UI strings that only exist if the product has a paywall
# step. Kept specific on purpose: a bare word like "subscription" also matches
# ordinary state-management code and would cause false alarms.
FUNNEL_PATTERNS = {
    "paywall route/component": r"[\"'/](paywall|pay-wall)[\"'/_-]",
    "choose-plan step": r"choose[-_ ]?plan|select[-_ ]?plan|plan[-_]?selection",
    "checkout / payment step": r"[\"'/](checkout|payment-process|payment[-_]?step|billing[-_]?step)[\"'/?]",
    # case-sensitive camelCase/route forms, so a job category like "Upselling" doesn't count
    "upsell / limited offer": r"(?-i:Upsells?[A-Z0-9_]|upsells?[A-Z_/\"'-])|limited[-_ ]?offer|intro[-_ ]?offer|discount[-_ ]?timer",
    "subscription API": r"[\"'/]subscriptions?/(order|plans?|products?|create|status|checkout)",
    # API calls only; a plain <a href="/pricing"> link is reported separately
    "pricing API": r"(?-i:getPricing|fetchPricing|getPrices|fetchPlans|getPlans)|api/[\w/-]*pric",
    "auto-renew wording": r"auto(matically)?[- ]?(renew|charge)|recurring (charge|billing)",
    "trial wording": r"free[- ]?trial|trial (period|ends)|\btrial\b[^\n]{0,40}(charge|then)",
}

# Words a genuinely free product tends to say out loud.
FREE_PATTERNS = {
    "free claim": r"\b(100% free|free forever|completely free|always free|free plan|free tier|it'?s free|for free)\b",
    "no card claim": r"no credit card( required)?",
}

_CUR = r"(?:US\$|S\$|\$|€|£|¥|GBP|USD|EUR|SGD|CNY)\s?"
_PERIOD = r"\s?(?:/|per)\s?(?:day|week|wk|month|mo|year|yr)\b"
# On the visible page a bare "$29" counts; salary figures like "$90k" don't.
PRICE_PATTERN = _CUR + r"\d{1,4}(?:[.,]\d{2})?(?![\dkK])(?:" + _PERIOD + r")?"
# Inside code, "$1" is usually a regex backreference, so demand cents or a period.
PRICE_IN_CODE_PATTERN = _CUR + r"\d{1,4}(?:[.,]\d{2}(?![\dkK])(?:" + _PERIOD + r")?|(?:[.,]\d{2})?" + _PERIOD + r")"

# Matched against each path segment of a short link, so a job ad whose slug
# happens to contain "billing" isn't mistaken for the site's billing policy.
POLICY_SEGMENT = re.compile(
    r"^(pricing|prices?|plans?|premium|subscri\w*|billing|terms|tos|legal|"
    r"refund\w*|money-?back\w*|cancel\w*|faq)(?:$|[-_.])",
    re.I,
)
COMMON_POLICY_PATHS = [
    "/pricing", "/plans", "/terms", "/terms-of-use", "/terms-of-service",
    "/legal/terms-of-use", "/refund-policy", "/legal/money-back-policy",
]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts, self.links, self.text = [], [], []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            self._skip += 1
            if a.get("src"):
                self.scripts.append(a["src"])
        elif tag == "style":
            self._skip += 1
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "link" and a.get("href") and a.get("as") == "script":
            self.scripts.append(a["href"])

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self.text.append(data.strip())


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(MAX_BYTES)
            charset = r.headers.get_content_charset() or "utf-8"
            return r.status, r.geturl(), body.decode(charset, errors="replace")
    except Exception as e:  # network errors are reported, not fatal
        return None, url, f"__ERROR__ {type(e).__name__}: {e}"


def snippets(text, pattern, limit=MAX_HITS_PER_SIGNAL, width=70):
    out = []
    for m in re.finditer(pattern, text, re.I):
        s = text[max(0, m.start() - width): m.end() + width]
        out.append(re.sub(r"\s+", " ", s).strip())
        if len(out) >= limit:
            break
    return out


def same_site(a, b):
    ha, hb = urllib.parse.urlparse(a).hostname or "", urllib.parse.urlparse(b).hostname or ""
    root = lambda h: ".".join(h.split(".")[-2:])
    return root(ha) == root(hb)


def probe(url):
    report = {"url": url, "errors": []}
    status, final_url, html = fetch(url)
    if status is None:
        report["errors"].append(html)
        return report
    report["final_url"] = final_url

    p = LinkParser()
    p.feed(html)
    visible = " ".join(p.text)
    report["visible_text_chars"] = len(visible)
    report["looks_like_js_shell"] = len(visible) < 400  # page needs a real browser to render

    # 1. Policy / pricing links that a visitor can reach without signing up.
    policy_links = set()
    for h in p.links:
        full = urllib.parse.urljoin(final_url, h).split("#")[0]
        segs = [x for x in urllib.parse.urlparse(full).path.split("/") if x]
        if 0 < len(segs) <= 3 and any(POLICY_SEGMENT.match(x) for x in segs):
            policy_links.add(full)
    policy_links = sorted(policy_links)
    report["policy_links_found_on_page"] = policy_links[:20]
    report["has_pricing_link"] = any(re.search(r"pric|plan|premium", l, re.I) for l in policy_links)

    # 2. Download the site's own scripts and search them.
    scripts = []
    for s in p.scripts:
        full = urllib.parse.urljoin(final_url, s)
        if full not in scripts:
            scripts.append(full)
    scripts = scripts[:MAX_SCRIPTS]
    corpus = [html]
    third_party_hosts = {
        urllib.parse.urlparse(s).hostname for s in scripts if not same_site(s, final_url)
    }
    with ThreadPoolExecutor(max_workers=8) as pool:
        for st, _, js in pool.map(fetch, scripts):
            if st is not None:
                corpus.append(js)
    report["scripts_scanned"] = len(corpus) - 1
    report["third_party_script_hosts"] = sorted(h for h in third_party_hosts if h)
    blob = "\n".join(corpus)

    report["payment_providers"] = {
        name: snippets(blob, pat, limit=1) for name, pat in PAYMENT_PROVIDERS.items()
        if re.search(pat, blob, re.I)
    }
    report["funnel_signals"] = {
        name: snippets(blob, pat) for name, pat in FUNNEL_PATTERNS.items()
        if re.search(pat, blob, re.I)
    }
    report["free_claims_in_visible_text"] = {
        name: snippets(visible, pat) for name, pat in FREE_PATTERNS.items()
        if re.search(pat, visible, re.I)
    }
    report["prices_in_visible_text"] = snippets(visible, PRICE_PATTERN, limit=6, width=40)
    report["prices_in_code"] = snippets(blob, PRICE_IN_CODE_PATTERN, limit=6, width=40)

    # 3. Read the terms / refund / pricing pages for billing language.
    candidates = [l for l in policy_links if same_site(l, final_url)]
    for path in COMMON_POLICY_PATHS:
        candidates.append(urllib.parse.urljoin(final_url, path))
    candidates = list(dict.fromkeys(candidates))[:10]
    policy_hits = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        pages = list(pool.map(fetch, candidates))
    for st, got, page in pages:
        if st is None or st >= 400 or got in policy_hits:
            continue
        lp = LinkParser()
        lp.feed(page)
        text = " ".join(lp.text)
        hits = snippets(text, r"auto(matically)?[- ]?renew|recurring|charge your|subscription fee|money[- ]?back|refund|free trial|\bper (day|week|month|year)\b", limit=3)
        if hits:
            policy_hits[got] = hits
    report["billing_language_in_policy_pages"] = policy_hits
    return report


LABELS = {
    "en": {
        "fetch_fail": "  could not fetch: ",
        "fetch_hint": [
            "  many large sites block non-browser requests; this says nothing about the",
            "  site itself. Open its pricing/terms pages in a browser tool instead.",
        ],
        "yes": "YES", "no": "no", "none": "none found",
        "renders": "  page renders without JS:      ",
        "renders_hint": "  (open it in a real browser to read it)",
        "pricing": "  pricing link on page:         ",
        "free": "  says 'free' out loud:         ",
        "price": "  price visible on page:        ",
        "provider": "  payment provider in code:     ",
        "funnel": "  paywall/funnel code signals:  ",
        "policy": "  billing terms in policy pages: ",
        "scripts": "  scripts scanned:              ",
        "tag_policy": "policy", "tag_price": "price in code",
        "signals": {},
    },
    "zh": {
        "fetch_fail": "  抓取失败：",
        "fetch_hint": [
            "  很多大网站会拦截非浏览器的访问，这不代表网站本身有问题。",
            "  请改用浏览器工具打开它的价格页和条款页查看。",
        ],
        "yes": "是", "no": "否", "none": "未发现",
        "renders": "  不用 JS 也能显示页面：  ",
        "renders_hint": "（需要用真正的浏览器打开才能读到内容）",
        "pricing": "  页面上有价格页链接：    ",
        "free": "  明确写了免费：          ",
        "price": "  页面上能看到价格：      ",
        "provider": "  代码里的收款服务：      ",
        "funnel": "  代码里的付费流程信号：  ",
        "policy": "  政策页里有收费条款：    ",
        "scripts": "  扫描的脚本数：          ",
        "tag_policy": "政策页", "tag_price": "代码里的价格",
        "signals": {
            "paywall route/component": "付费墙页面",
            "choose-plan step": "选方案步骤",
            "checkout / payment step": "结账付款步骤",
            "upsell / limited offer": "加价推销或限时优惠",
            "subscription API": "订阅接口",
            "pricing API": "价格接口",
            "auto-renew wording": "自动续费字样",
            "trial wording": "试用字样",
        },
    },
}


def summarize(r, lang="en"):
    L = LABELS[lang]
    sig = lambda name: L["signals"].get(name, name)
    sep = "、" if lang == "zh" else ", "
    lines = [f"\n=== {r['url']}"]
    if r["errors"]:
        lines.append(L["fetch_fail"] + "; ".join(r["errors"]))
        lines += L["fetch_hint"]
        return "\n".join(lines)
    yes = lambda b: L["yes"] if b else L["no"]
    lines += [
        L["renders"] + yes(not r["looks_like_js_shell"])
        + (L["renders_hint"] if r["looks_like_js_shell"] else ""),
        L["pricing"] + yes(r["has_pricing_link"]),
        L["free"] + yes(bool(r["free_claims_in_visible_text"])),
        L["price"] + yes(bool(r["prices_in_visible_text"])),
        L["provider"] + (sep.join(r["payment_providers"]) or L["none"]),
        L["funnel"] + (sep.join(sig(n) for n in r["funnel_signals"]) or L["none"]),
        L["policy"] + yes(bool(r["billing_language_in_policy_pages"])),
        L["scripts"] + str(r["scripts_scanned"]),
    ]
    for name, hits in r["funnel_signals"].items():
        lines.append(f"    [{sig(name)}] {hits[0][:160]}")
    for page, hits in r["billing_language_in_policy_pages"].items():
        lines.append(f"    [{L['tag_policy']}] {page}: {hits[0][:160]}")
    if r["prices_in_code"]:
        lines.append(f"    [{L['tag_price']}] {r['prices_in_code'][0][:120]}")
    return "\n".join(lines)


if __name__ == "__main__":
    args = sys.argv[1:]
    as_json = "--json" in args
    lang = "zh" if "--zh" in args else "en"
    urls = [a for a in args if not a.startswith("--")]
    if not urls:
        print(__doc__)
        sys.exit(1)
    results = [probe(u) for u in urls]
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(summarize(r, lang))
