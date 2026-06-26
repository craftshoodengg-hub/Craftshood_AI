# Craftshood_AI - AI Agent Instructions

## Project Goal

Craftshood_AI is an AI-powered architectural floor plan understanding engine.

The objective is to convert CAD/DXF floor plans into structured building intelligence.

## Core Pipeline

DXF
↓
Normalization
↓
Geometry Extraction
↓
Wall Detection
↓
Room Detection
↓
Room Graph
↓
Building Model
↓
Adjacency
Connectivity
Facing
Zoning
Confidence
↓
API
↓
Flutter App

## Coding Rules

* Read existing code before editing.
* Understand the affected modules first.
* Never rewrite working modules without reason.
* Keep code modular.
* Prefer dataclasses.
* Add type hints.
* Keep functions small.
* Preserve backwards compatibility.
* Update tests when changing behaviour.

## Before Coding

Always:

1. Explain the implementation plan.
2. Identify affected files.
3. Wait for approval.
4. Then modify code.

## Priorities

1. Correctness
2. Performance
3. Readability
4. Maintainability

## Never

* Delete working code unless requested.
* Rename public APIs unnecessarily.
* Duplicate logic.
* Ignore existing architecture.

## Output Style

Always explain:

* Why the change is needed.
* Which files will change.
* Expected impact.
* Risks.
