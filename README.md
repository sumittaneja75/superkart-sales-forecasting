# SuperKart Sales Forecasting – Deployment

Deployment files for the SuperKart sales forecasting model (tuned Random Forest, test MAPE ≈ 3.8%).

| Path | Contents |
|---|---|
| `backend_files/` | Flask API (`superkart_api`) with `POST /v1/predict` and `POST /v1/predictbatch`, the serialized model, requirements and Dockerfile |
| `frontend_files/` | Streamlit UI for online and batch predictions, requirements and Dockerfile |
| `run_containers.sh` | Builds both images and runs them on a shared Docker network (GitHub Codespaces) |
| `.github/workflows/deploy-backend.yml` | Deploys `backend_files/` to the Hugging Face Space `Sutaneja/superkart-backend` on every push to `main` |

Live API: https://sutaneja-superkart-backend.hf.space

The workflow needs the repository secret `HF_TOKEN` (a Hugging Face **write** token).
