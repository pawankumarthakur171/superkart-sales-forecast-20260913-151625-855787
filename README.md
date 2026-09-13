# SuperKart Sales Forecast

## Project
SuperKart is a retail sales forecasting solution that predicts `Product_Store_Sales_Total` using historical product/store information.

## Repository structure
```text
README.md
backend/
  app.py
  Dockerfile
  requirements.txt
  superkart_model.joblib
  model_metadata.json
frontend/
  app.py
  Dockerfile
  requirements.txt
```

GitHub Codespaces provides a ready-to-use Docker environment; each service ships its own `Dockerfile` under `backend/` and `frontend/`.

## Backend
Flask API: port 7860
- `GET /health`
- `POST /v1/predict`
- `POST /v1/predictbatch`

The root endpoint (`GET /`) returns an explicit SuperKart backend message so that opening the forwarded backend port directly confirms that the Flask container is working.
The health endpoint (`GET /health`) returns JSON with status, model name and feature contract.

## Frontend
Streamlit UI: port 8501
- Single prediction form
- Drag-and-drop CSV upload for batch prediction
- Downloadable prediction CSV

## Runtime dependencies
The backend installs only what it actually needs at runtime:
- Flask for the REST API
- pandas for input validation and batch CSV handling
- scikit-learn because the serialized preprocessing/model pipeline contains sklearn objects
- joblib because the backend loads `superkart_model.joblib`
- only the external estimator package required by the selected final model, if applicable

The frontend installs only:
- Streamlit for the web UI
- requests for HTTP calls to Flask
- pandas for CSV display and prediction-result tables

The frontend does **not** load the model, so it does not install joblib, scikit-learn, XGBoost, CatBoost or LightGBM.
No Hugging Face packages are used because deployment is exclusively through GitHub Codespaces.

## Docker commands
Run these from the repository root in Codespaces:
```bash
docker rm -f frontend backend 2>/dev/null || true
docker network rm rppapp-network 2>/dev/null || true
docker network create rppapp-network
docker build -t backend ./backend
docker build -t frontend ./frontend
docker run -d --name backend --network rppapp-network -p 7860:7860 --restart unless-stopped backend
docker run -d --name frontend --network rppapp-network -p 8501:8501 -e BACKEND_URL=http://backend:7860 --restart unless-stopped frontend
docker ps
# the backend loads the model on startup - wait, then poll /health until it is ready
for i in $(seq 1 10); do curl -sf http://localhost:7860/health && break || (echo "waiting for backend... ($i)"; sleep 3); done
curl http://localhost:7860/
```

## Model cache
- Cache key: `df483c976c40e0132ae0c799840a5d9ed28e0f663504f88230f63c1fa331de3c`
- Training-data SHA256: `b12ec41668e69d71d64ca96f2be78a011087f2a9cac6aba6e5cc920544b21ab2`
- Selected model: `CatBoost`
- Reused on this run: `True`

## Model performance
The notebook compares the required regressors, tunes the strongest candidates, selects the final model, serializes the complete preprocessing + model pipeline, reloads it, and tests it on the held-out test set.

Reference year: `2025`
