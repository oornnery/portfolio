---
title: "Distributed Task Orchestrator"
slug: "distributed-task-orchestrator"
description: >-
  A queue-driven orchestrator for long-running jobs with retries, idempotency,
  and operational dashboards.
thumbnail: "/static/images/projects/distributed-task-orchestrator.svg"
tags: ["python", "distributed-systems", "queues"]
tech_stack: ["Python", "FastAPI", "Redis", "PostgreSQL"]
github_url: "https://github.com/oornnery/distributed-task-orchestrator"
live_url: ""
date: 2025-02-14
featured: false
---

## Overview

This project coordinates async workloads across workers while preserving
ordering guarantees and fault tolerance.

## Core capabilities

- Job deduplication with idempotency keys
- Exponential backoff and dead-letter policies
- Real-time execution metrics and queue health insights
- Declarative workflow steps with clear failure boundaries

## Result

The orchestrator improved reliability for background tasks and reduced manual
recovery incidents in production.
