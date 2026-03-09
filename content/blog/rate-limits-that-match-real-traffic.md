---
title: "Rate Limits That Match Real Traffic"
slug: "rate-limits-that-match-real-traffic"
description: "How I choose practical rate limits without punishing normal users."
date: "2026-02-07"
author: "Fabio Souza"
tags:
  - "security"
  - "api"
  - "fastapi"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Rate limits only help when they reflect real usage.

If limits are too loose, abuse still gets through. If they are too strict,
normal users become collateral damage and the team stops trusting the control.

## Start from route intent

I do not pick limits from generic blog posts. I start from route intent.

A read-heavy public endpoint, a contact form, and an analytics ingestion route
do not need the same policy. Their threat model and normal burst patterns are
different.

The first useful split is:

- public read routes: broader limits, mostly protection against scraping bursts
- mutation routes: tighter limits, especially when they trigger side effects
- sensitive routes: aggressive limits and better visibility into blocked traffic

That keeps the policy tied to behavior instead of superstition.

## Burst tolerance matters

People do not interact with websites at perfectly even intervals.

Browsers retry. Pages refresh. Mobile networks reconnect. Bots probe in short
spikes. A limit that ignores bursts often creates false positives.

What I usually want is not "exactly N requests every minute." I want "reasonable
bursts are okay, sustained abuse is not."

In practice that means:

- one broad default for most routes
- tighter route-specific overrides for contact or analytics endpoints
- logging around blocked requests to confirm the policy matches reality

## Proxy-aware limits are not optional

If the app sits behind Traefik, Nginx, or a platform proxy, source IP handling
needs to be explicit.

A rate limiter that trusts the wrong header is worse than no limiter because it
creates false confidence. Every environment should answer:

- which proxy headers are trusted
- whether forwarded headers are enabled
- what happens in local dev and tests

That is why I prefer a shared source-IP extraction function instead of route code
guessing request identity ad hoc.

## Observe the control, not just the app

Once a limit exists, it becomes part of production behavior.

I want to know:

- which routes are hitting the limiter
- whether blocked requests are clustered by IP or path
- whether the volume is rising gradually or spiking
- whether legitimate traffic is being penalized

Those signals help decide whether the issue is abuse, bad client behavior, or a
policy mistake on our side.

## A rollout pattern that stays sane

When adding rate limiting to an existing service, I use a simple order:

1. add a safe default limit
2. instrument blocked responses
3. tighten sensitive routes
4. review logs after real traffic
5. adjust only with evidence

That sequence prevents the common failure mode where limits feel random and are
disabled the first time a normal user hits them.

Good rate limiting is not about looking strict. It is about applying friction in
the right place with minimal damage to normal use.
