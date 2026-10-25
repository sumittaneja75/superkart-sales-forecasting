---
title: SuperKart Sales Forecasting API
emoji: 🛒
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

Flask API serving the SuperKart sales forecasting model.

- `POST /v1/predict` - online prediction (JSON)
- `POST /v1/predictbatch` - batch prediction (CSV file)
