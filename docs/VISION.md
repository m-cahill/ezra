VISION — EZRA (Extensible Zone‑Based Runtime Architecture)
=====================================================================

Purpose
-------

This project refactors **EasyOCR** into a **general-purpose runtime perception engine** that can be embedded into games and interactive systems (e.g., chess, poker, card games, UI automation) to convert raw screen pixels into **structured, interpretable state**.

The goal is **not** to improve OCR accuracy or train new models in this repository.  
The goal is to establish **clean architectural boundaries** so that perception, learning, and domain intelligence are decoupled, testable, and reusable.

* * *

Why This Exists
---------------

Modern games and interactive systems increasingly rely on **visual interfaces without structured APIs**.

To build intelligent agents, assistive tools, accessibility layers, or analysis systems, we need a **reliable, modular perception layer** that converts pixels into structured state.

Existing approaches fall short:

* Traditional screen readers depend on accessibility trees and cannot interpret game UIs.

* Most OCR and CV libraries (including EasyOCR) are **monolithic and model-coupled**.

* Game logic, perception, and learning are often tightly interwoven, making systems brittle and untestable.

This project fills that gap by providing a **runtime perception engine** that is:

* ML-agnostic

* domain-agnostic

* deterministic and testable

* embeddable in other systems

* driven by explicit, enforceable interfaces

* * *

Core Insight
------------

A usable “screen reader” for games is **not** a text-to-speech tool.

It is a **perception stack** with clear layers:

1. Visual capture

2. Perception (OCR / detection / segmentation)

3. Structured state reconstruction

4. Interpretation and narration

This repository is responsible for **Layer 2 only** — the **runtime perception engine**.

Everything upstream (data creation, training) and downstream (game logic, narration) is intentionally out of scope.

* * *

Repository Philosophy
---------------------

This repository prioritizes:

* **Clarity over cleverness**

* **Boundaries over features**

* **Replaceability over optimization**

* **Determinism over throughput**

* **Explicit interfaces over implicit coupling**

The goal is not to be the fastest perception engine — it is to be the **cleanest, safest, and most extensible**.

* * *

Architectural Pillars
---------------------

### Pillar 1 — Separation of Concerns

This project enforces strict separation between:

* **Data creation** (annotation, labeling)

* **Model training**

* **Runtime inference**

* **Domain interpretation**

Specifically:

* **CVAT** is the _data factory_ (upstream)

* **External training pipelines** produce model artifacts

* **This repository** loads and runs those artifacts

* **Game adapters** interpret outputs elsewhere

No training logic lives here.

* * *

### Pillar 2 — ML Is a Plugin, Not the Core

The runtime engine is designed so that:

* Core logic is **ML-free**

* ML models are **loaded dynamically as plugins**

* Models are **replaceable artifacts**, not hard-coded dependencies

The engine must remain usable even if **all ML plugins are replaced with stubs**.

* * *

### Pillar 3 — Determinism and Testability

All non-ML components must be:

* deterministic

* CPU-runnable

* unit testable

* independent of GPU availability

ML plugins may be nondeterministic internally, but their **interfaces and output schemas are deterministic**.

* * *

High-Level Architecture
-----------------------

    [ Annotated Data (CVAT) ]
                ↓
       [ Training Pipelines ]
                ↓
          (Model Artifacts)
                ↓
    [ EasyOCR-Refactor Runtime ]
    ┌─────────────────────────────────┐
    │  Core Engine (ML-free)           │
    │  ├─ image loading                │
    │  ├─ preprocessing                │
    │  ├─ batching                     │
    │  ├─ device management            │
    │  ├─ postprocessing               │
    │  └─ region extraction            │
    │                                 │
    │  Plugin Loader                   │
    │  ├─ OCR Backend                  │
    │  ├─ Detector Backends            │
    │  ├─ Layout / Segmentation        │
    └─────────────────────────────────┘
                ↓
          (Raw Detections)
                ↓
       [ Game / Domain Adapters ]
                ↓
       (Structured State, Narration)

* * *

Layer Responsibilities
----------------------

### 1. Core Engine (ML-Free)

Responsibilities:

* Image I/O

* Color normalization

* Resizing and tiling

* Region cropping

* Batching and scheduling

* Device selection (CPU/GPU)

* Postprocessing utilities

Non-responsibilities:

* No neural networks

* No model weights

* No training logic

* No domain interpretation

This layer must be **fully testable without ML dependencies**.

* * *

### 2. ML Plugin Interface

ML functionality is accessed exclusively through explicit interfaces.

#### Plugin Contract (Minimum Requirements)

All ML plugins **must**:

* implement `load(model_path)`

* implement `infer(image_or_batch)`

* implement `describe_capabilities()`

* return outputs with a deterministic schema

* expose version metadata

Plugins **must not**:

* modify core engine state

* assume GPU availability

* perform domain interpretation

* depend on EasyOCR internals

This contract makes the plugin boundary **enforceable**.

* * *

### 3. Model Artifact Expectations

Model artifacts consumed by this runtime must:

* be self-contained

* include version metadata

* include preprocessing and postprocessing configs

* declare input size and normalization requirements

* be loadable without internet access

This ensures reproducibility, offline operation, and auditability.

* * *

### 4. Multi-Modal Perception

The runtime supports multiple perception modalities via plugins:

* OCR (text recognition)

* Object detection

* Layout detection

* Segmentation

These plugins may be combined at runtime but remain **independent and swappable**.

* * *

Security & Safety Considerations
--------------------------------

The runtime must:

* never execute arbitrary code from model artifacts

* validate plugin metadata before loading

* sandbox plugin execution where possible

* avoid network calls during inference

* fail closed (safe defaults) when plugins misbehave

This protects against malformed or malicious models and preserves system integrity.

* * *

Performance Philosophy
----------------------

This project optimizes for:

* correctness

* determinism

* modularity

It does **not** optimize for:

* maximum FPS

* raw GPU throughput

* real-time constraints

Performance improvements may be added later, but **never at the cost of architectural clarity**.

* * *

V1 Scope (Locked)
-----------------

### V1 Goal

Refactor EasyOCR into a modular perception runtime that can load OCR and one detector plugin, and reconstruct chess board state from screenshots.

### V1 Deliverables

* Refactored EasyOCR core (ML-free engine)

* Explicit plugin interface

* EasyOCR OCR wrapped as a plugin

* One additional detector plugin (simple or stub)

* Chess adapter that:
  
  * maps detections to an 8×8 grid
  
  * reconstructs FEN
  
  * detects move deltas between frames

* CPU-only smoke tests proving determinism

### Explicit Non-Goals (V1)

* No poker

* No narration or TTS

* No CVAT integration code

* No training automation

* No real-time performance tuning

* No UI overlays

* * *

Future Extensions (Non-Binding)
-------------------------------

The architecture should not preclude:

* multi-modal fusion (vision + audio)

* temporal models (frame-to-frame tracking)

* lightweight on-device inference

* plugin registries

* remote inference backends

* model auto-selection based on capabilities

These are **explicitly out of scope** for V1.

* * *

Glossary
--------

* **Core Engine** — ML-free runtime components

* **Plugin** — ML model wrapped behind a stable interface

* **Adapter** — domain-specific interpreter (e.g., chess, poker)

* **Artifact** — trained model file plus metadata

* **Perception** — converting pixels into raw detections

* **Interpretation** — converting detections into structured state

* * *

Summary
-------

This project transforms EasyOCR from a monolithic OCR library into a **modular, extensible perception runtime**.

By separating data creation, learning, inference, and interpretation, it creates a system that is:

* safer to change

* easier to test

* reusable across domains

* aligned with production computer vision best practices

This document is the **architectural contract**.
