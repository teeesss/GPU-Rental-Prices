# Neocloud GPU Intelligence Engine (V4.2.25)

> Institutional-grade GPU rental price tracking and market intelligence.

**Live Dashboard**: [bmwseals.com/gpus](https://bmwseals.com/gpus/?v=425)

---

## 🚀 Overview
Tracks and visualizes GPU rental prices across AI Neoclouds, cloud marketplaces, and institutional indices. High-density market intelligence delivered through an automated pipeline.

## 🛠️ Tech Stack
- **Frontend**: Vanilla HTML/JS, Chart.js, Luxon
- **Backend**: Python 3.12 (Playwright, SQLite)
- **Deployment**: Autonomous SFTP Sync

## 📐 Standards (V4.2.25)
- **50% Scaling Rule**: GPU Labels boosted to 27px (Desktop) / 10px (Mobile).
- **Universal Responsive**: Precision scaling across Desktop, Tablet, and Mobile.
- **Color Sync**: UI elements color-matched to GPU model chart palettes.

## ⚙️ Usage
```bash
./gpu.sh         # Run automated pipeline (2-day stale gate)
./gpu.sh --force # Force production update
```
