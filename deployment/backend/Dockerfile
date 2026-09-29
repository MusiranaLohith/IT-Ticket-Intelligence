FROM python:3.14-slim

WORKDIR /home/whiteblack/Documents/IT-Ticket-Triage-System
ENV PYTHONPATH=/home/whiteblack/Documents/IT-Ticket-Triage-System/deployment/backend

COPY deployment/backend/requirements.txt deployment/backend/requirements.txt

RUN pip install --no-cache-dir -r deployment/backend/requirements.txt

COPY deployment/ deployment/
COPY modeling/FMP/deployment/runtime/ modeling/FMP/deployment/runtime/

COPY modeling/T1/baselines/t1_it_support_char_svm.joblib modeling/T1/baselines/
COPY modeling/T2/models/t2_class_weighted_tfidf_logreg.joblib modeling/T2/models/
COPY modeling/T3/models/t3_class_weighted_tfidf_logreg.joblib modeling/T3/models/

COPY modeling/T4/results/mod007_checkpoints/t4_mod007_tfidf.joblib modeling/T4/results/mod007_checkpoints/
COPY modeling/T4/results/mod007_checkpoints/t4_mod007_neighbors.joblib modeling/T4/results/mod007_checkpoints/
COPY modeling/T4/derived/t4_train.csv modeling/T4/derived/

COPY modeling/T5/models/t5_mod005_tfidf.joblib modeling/T5/models/
COPY modeling/T5/models/t5_mod005_logreg.joblib modeling/T5/models/
COPY modeling/T5/models/t5_mod007_calibrated_tfidf.joblib modeling/T5/models/
COPY modeling/T5/models/t5_mod007_calibration_models.joblib modeling/T5/models/

COPY modeling/T7/metrics/t7_mod010_log_normal_aft_model.json modeling/T7/metrics/
COPY modeling/T7/splits/t7_train.csv modeling/T7/splits/

CMD ["uvicorn", "deployment.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
