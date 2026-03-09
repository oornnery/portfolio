---
title: "Docker Compose Habits For Production-Like Dev"
slug: "docker-compose-habits-for-production-like-dev"
description: "Small habits that make local container setups closer to real deployments."
date: "2025-11-20"
author: "Fabio Souza"
tags:
  - "docker"
  - "infra"
  - "devx"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Local Docker environments become useful when they expose real constraints early.

I do not need production parity for every side project, but I do want local dev
to reveal configuration drift, startup assumptions, and missing dependencies.

## Separate dev and prod on purpose

Trying to make one Compose file handle every environment usually creates hidden
conditionals and unclear defaults.

I prefer:

- one dev-oriented setup optimized for fast iteration
- one production-oriented setup optimized for predictability
- shared concepts, but not forced file-level symmetry

That keeps the intent of each environment easy to understand.

## Treat reverse proxy behavior as part of the app

For web apps, local environments are more realistic when the proxy is present.

That helps surface:

- trusted host issues
- forwarded header assumptions
- path and scheme handling
- security headers and body size behavior

If the app only ever runs directly on localhost during development, deployment
issues show up later than they should.

## Log startup assumptions

Containers fail in frustrating ways when startup expectations are implicit.

I want startup logs to make it obvious:

- which config file is active
- which port is bound
- whether static assets are mounted
- whether telemetry exporters are enabled
- whether dependent services are reachable

Those facts remove a lot of wasted time when a stack "starts" but does not
actually behave.

## Keep the dev loop small

Production-like does not mean slow.

I still want:

- bind mounts where iteration matters
- clear health checks
- minimal service graph for local work
- easy rebuilds when dependencies change

A good local stack should feel realistic enough to catch issues, but small enough
that people actually use it every day.

## Review container boundaries occasionally

Every few weeks, it is worth checking whether the local stack still reflects the
important production boundaries.

Questions I like:

1. Does the app still rely on anything only available outside containers?
2. Are proxy and security assumptions still exercised locally?
3. Are env vars and mounted files still explicit?
4. Is the stack small enough that developers keep it running?

That balance matters more than chasing perfect parity.
