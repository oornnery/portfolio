---
title: "Database Migrations Without Downtime"
slug: "database-migrations-without-downtime"
description: "Safe migration patterns for adding columns, renaming fields, and changing constraints in live databases."
date: "2025-09-12"
author: "Fabio Souza"
tags:
  - "postgres"
  - "backend"
  - "infra"
featured: false
discussion_url: "https://github.com/oornnery/proj/site/discussions"
---

Zero-downtime migrations require thinking about schema changes in two phases:
what the database can safely do while old code is running, and what the new
code assumes after deployment.

## Adding a nullable column

Safe to do with old code running. New code reads the column; old code ignores
it. Make the column non-nullable in a separate migration after backfilling.

## Renaming a column

Dangerous with a single migration. The safe sequence:

1. Add the new column.
2. Write to both columns in the application.
3. Backfill the new column.
4. Switch reads to the new column.
5. Drop writes to the old column.
6. Drop the old column.

## Adding indexes concurrently

`CREATE INDEX` locks the table by default. Use `CREATE INDEX CONCURRENTLY`
to build the index without blocking reads or writes.

## Changing column type

Most type changes require a full table rewrite. Use a new column, backfill,
and swap in stages. Never change a column type in a single migration on a
large table in production.

## Keep migrations reversible

Every migration should have a `downgrade` path. Not because you will use it
often, but because it forces you to reason about the schema change completely.
