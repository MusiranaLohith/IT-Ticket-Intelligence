import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_recall_fscore_support,
)
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# ============================================================
# T3-MOD-025
# Controlled DistilBERT Training Feasibility Experiment
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

DATA_PATH = PROJECT_ROOT / "modeling/T3/derived/t3_features.csv"
SPLIT_DIR = PROJECT_ROOT / "modeling/T3/splits"

OUTPUT_MODEL = PROJECT_ROOT / "modeling/T3/models/t3_distilbert_feasibility"
OUTPUT_METRICS = PROJECT_ROOT / "modeling/T3/metrics/t3_distilbert_feasibility_validation_metrics.json"
OUTPUT_ANALYSIS = PROJECT_ROOT / "modeling/T3/analysis/t3_distilbert_feasibility.json"

MODEL_NAME = "distilbert-base-uncased"

LABELS = ["S1", "S2", "S3", "S4"]
LABEL_TO_ID = {label: i for i, label in enumerate(LABELS)}
ID_TO_LABEL = {i: label for label, i in LABEL_TO_ID.items()}

MAX_LENGTH = 128
BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4
EPOCHS = 1
LEARNING_RATE = 2e-5

DEVICE = torch.device("cpu")


# ============================================================
# Dataset
# ============================================================

class TicketDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, index):
        encoding = self.tokenizer(
            self.texts[index],
            truncation=True,
            max_length=MAX_LENGTH,
            padding="max_length",
            return_tensors="pt",
        )

        item = {key: value.squeeze(0) for key, value in encoding.items()}
        item["labels"] = torch.tensor(self.labels[index], dtype=torch.long)

        return item


# ============================================================
# Helpers
# ============================================================

def build_text(df):
    summary = df["Summary"].fillna("").astype(str)
    description = df["Description"].fillna("").astype(str)

    return (
        "Summary: "
        + summary
        + "\nDescription: "
        + description
    ).tolist()


def load_split(name):
    path = SPLIT_DIR / f"t3_{name}.csv"

    if not path.exists():
        raise FileNotFoundError(f"Missing split: {path}")

    return pd.read_csv(path, keep_default_na=False)


# ============================================================
# Main
# ============================================================

print("T3_MOD_025_START")

start_time = time.time()

torch.set_num_threads(8)

print(f"TORCH_VERSION={torch.__version__}")
print(f"DEVICE={DEVICE}")
print(f"CUDA_AVAILABLE={torch.cuda.is_available()}")
print(f"MODEL={MODEL_NAME}")
print(f"MAX_LENGTH={MAX_LENGTH}")
print(f"BATCH_SIZE={BATCH_SIZE}")
print(f"GRADIENT_ACCUMULATION_STEPS={GRADIENT_ACCUMULATION_STEPS}")
print(f"EPOCHS={EPOCHS}")
print(f"LEARNING_RATE={LEARNING_RATE}")


# ------------------------------------------------------------
# Load controlled splits only
# ------------------------------------------------------------

train_df = load_split("train")
val_df = load_split("validation")

print(f"TRAIN_ROWS={len(train_df)}")
print(f"VALIDATION_ROWS={len(val_df)}")

expected_train = 21587
expected_val = 4626

if len(train_df) != expected_train:
    raise RuntimeError(
        f"UNEXPECTED_TRAIN_ROWS={len(train_df)}"
    )

if len(val_df) != expected_val:
    raise RuntimeError(
        f"UNEXPECTED_VALIDATION_ROWS={len(val_df)}"
    )


# ------------------------------------------------------------
# Verify required columns
# ------------------------------------------------------------

required_columns = {
    "ID",
    "Creation time",
    "Summary",
    "Description",
    "target_severity",
}

if not required_columns.issubset(train_df.columns):
    raise RuntimeError("TRAIN_COLUMNS_INVALID")

if not required_columns.issubset(val_df.columns):
    raise RuntimeError("VALIDATION_COLUMNS_INVALID")


# ------------------------------------------------------------
# Verify target vocabulary
# ------------------------------------------------------------

if not set(train_df["target_severity"]).issubset(LABELS):
    raise RuntimeError("TRAIN_TARGET_VOCABULARY_INVALID")

if not set(val_df["target_severity"]).issubset(LABELS):
    raise RuntimeError("VALIDATION_TARGET_VOCABULARY_INVALID")


# ------------------------------------------------------------
# Build Creation-time text
# ------------------------------------------------------------

train_texts = build_text(train_df)
val_texts = build_text(val_df)

train_labels = [
    LABEL_TO_ID[x]
    for x in train_df["target_severity"]
]

val_labels = [
    LABEL_TO_ID[x]
    for x in val_df["target_severity"]
]


# ------------------------------------------------------------
# Tokenizer
# ------------------------------------------------------------

print("LOADING_TOKENIZER=True")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("TOKENIZER_LOADED=True")


# ------------------------------------------------------------
# Dataset / DataLoader
# ------------------------------------------------------------

train_dataset = TicketDataset(
    train_texts,
    train_labels,
    tokenizer,
)

val_dataset = TicketDataset(
    val_texts,
    val_labels,
    tokenizer,
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
)

print("DATALOADERS_READY=True")


# ------------------------------------------------------------
# Model
# ------------------------------------------------------------

print("LOADING_MODEL=True")

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(LABELS),
    id2label=ID_TO_LABEL,
    label2id=LABEL_TO_ID,
)

model.to(DEVICE)

print("MODEL_LOADED=True")


# ------------------------------------------------------------
# Optimizer
# ------------------------------------------------------------

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
)


# ------------------------------------------------------------
# Training
# ------------------------------------------------------------

model.train()

optimizer.zero_grad()

training_loss = 0.0
optimizer_steps = 0

training_start = time.time()

for epoch in range(EPOCHS):

    print(f"EPOCH_START={epoch + 1}")

    for step, batch in enumerate(train_loader):

        batch = {
            key: value.to(DEVICE)
            for key, value in batch.items()
        }

        outputs = model(**batch)

        loss = outputs.loss
        loss = loss / GRADIENT_ACCUMULATION_STEPS

        loss.backward()

        training_loss += loss.item()

        if (
            (step + 1) % GRADIENT_ACCUMULATION_STEPS == 0
            or (step + 1) == len(train_loader)
        ):
            optimizer.step()
            optimizer.zero_grad()
            optimizer_steps += 1

        if (step + 1) % 500 == 0:
            print(
                f"TRAIN_STEP={step + 1}/{len(train_loader)} "
                f"LOSS={loss.item():.6f}"
            )

training_seconds = time.time() - training_start

print(f"TRAINING_SECONDS={training_seconds:.2f}")
print(f"OPTIMIZER_STEPS={optimizer_steps}")


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print("VALIDATION_START=True")

model.eval()

predictions = []
true_labels = []

validation_start = time.time()

with torch.no_grad():

    for batch in val_loader:

        labels = batch["labels"].cpu().numpy()

        inputs = {
            key: value.to(DEVICE)
            for key, value in batch.items()
            if key != "labels"
        }

        outputs = model(**inputs)

        preds = torch.argmax(
            outputs.logits,
            dim=1,
        ).cpu().numpy()

        predictions.extend(preds.tolist())
        true_labels.extend(labels.tolist())

validation_seconds = time.time() - validation_start


# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------

accuracy = accuracy_score(
    true_labels,
    predictions,
)

macro_f1 = f1_score(
    true_labels,
    predictions,
    average="macro",
    zero_division=0,
)

weighted_f1 = f1_score(
    true_labels,
    predictions,
    average="weighted",
    zero_division=0,
)

precision, recall, f1, support = precision_recall_fscore_support(
    true_labels,
    predictions,
    labels=list(range(len(LABELS))),
    zero_division=0,
)

print(f"ACCURACY={accuracy:.6f}")
print(f"MACRO_F1={macro_f1:.6f}")
print(f"WEIGHTED_F1={weighted_f1:.6f}")

for i, label in enumerate(LABELS):

    print(
        f"{label}_PRECISION={precision[i]:.6f}"
    )
    print(
        f"{label}_RECALL={recall[i]:.6f}"
    )
    print(
        f"{label}_F1={f1[i]:.6f}"
    )
    print(
        f"{label}_SUPPORT={support[i]}"
    )


# ------------------------------------------------------------
# Prediction distribution
# ------------------------------------------------------------

prediction_counts = {
    label: int(
        np.sum(
            np.array(predictions) == LABEL_TO_ID[label]
        )
    )
    for label in LABELS
}

print("PREDICTION_COUNTS")

for label in LABELS:
    print(
        f"{label}_PREDICTED="
        f"{prediction_counts[label]}"
    )


# ------------------------------------------------------------
# Save model
# ------------------------------------------------------------

OUTPUT_MODEL.mkdir(
    parents=True,
    exist_ok=True,
)

model.save_pretrained(OUTPUT_MODEL)
tokenizer.save_pretrained(OUTPUT_MODEL)


# ------------------------------------------------------------
# Save metrics
# ------------------------------------------------------------

OUTPUT_METRICS.parent.mkdir(
    parents=True,
    exist_ok=True,
)

metrics = {
    "operation": "T3-MOD-025",
    "task": "T3_SEVERITY_PREDICTION",
    "model": MODEL_NAME,
    "device": str(DEVICE),
    "train_rows": len(train_df),
    "validation_rows": len(val_df),
    "max_length": MAX_LENGTH,
    "batch_size": BATCH_SIZE,
    "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
    "epochs": EPOCHS,
    "learning_rate": LEARNING_RATE,
    "accuracy": float(accuracy),
    "macro_f1": float(macro_f1),
    "weighted_f1": float(weighted_f1),
    "per_class": {
        LABELS[i]: {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }
        for i in range(len(LABELS))
    },
    "prediction_counts": prediction_counts,
    "training_seconds": float(training_seconds),
    "validation_seconds": float(validation_seconds),
    "test_used": False,
    "raw_mozilla_accessed": False,
    "dataset_modified": False,
}

with open(
    OUTPUT_METRICS,
    "w",
    encoding="utf-8",
) as f:
    json.dump(metrics, f, indent=2)


# ------------------------------------------------------------
# Feasibility analysis
# ------------------------------------------------------------

total_seconds = time.time() - start_time

analysis = {
    "operation": "T3-MOD-025",
    "status": "FEASIBILITY_COMPLETE",
    "model": MODEL_NAME,
    "training_seconds": float(training_seconds),
    "validation_seconds": float(validation_seconds),
    "total_seconds": float(total_seconds),
    "validation_macro_f1": float(macro_f1),
    "validation_accuracy": float(accuracy),
    "validation_weighted_f1": float(weighted_f1),
    "classical_reference_macro_f1": 0.348017,
    "classical_reference_model": "T3-MOD-008",
    "test_used": False,
    "raw_mozilla_accessed": False,
    "dataset_modified": False,
}

OUTPUT_ANALYSIS.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with open(
    OUTPUT_ANALYSIS,
    "w",
    encoding="utf-8",
) as f:
    json.dump(analysis, f, indent=2)


print(f"MODEL={OUTPUT_MODEL}")
print(f"METRICS={OUTPUT_METRICS}")
print(f"ANALYSIS={OUTPUT_ANALYSIS}")
print("TEST_USED=False")
print("RAW_MOZILLA_ACCESSED=False")
print("DATASET_MODIFIED=False")
print("STATUS=FEASIBILITY_COMPLETE")
print("T3_MOD_025_COMPLETE")