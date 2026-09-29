from pathlib import Path
import json
import torch

from transformers import AutoTokenizer, AutoModel


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling"
    / "T3"
    / "analysis"
    / "t3_transformer_smoke_test.json"
)

MODEL_NAME = "distilbert-base-uncased"


def main():
    print("T3_MOD_024_START")

    device = torch.device("cpu")

    print(f"TORCH_VERSION={torch.__version__}")
    print(f"DEVICE={device}")
    print(f"CUDA_AVAILABLE={torch.cuda.is_available()}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)

    model.to(device)
    model.eval()

    text = (
        "Firefox crashes when opening a page after the latest update."
    )

    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128,
    )

    encoded = {
        key: value.to(device)
        for key, value in encoded.items()
    }

    with torch.no_grad():
        output = model(**encoded)

    hidden_shape = tuple(output.last_hidden_state.shape)

    result = {
        "task": "T3_SEVERITY_PREDICTION",
        "operation": "T3-MOD-024",
        "model": MODEL_NAME,
        "torch_version": torch.__version__,
        "device": str(device),
        "cuda_available": bool(torch.cuda.is_available()),
        "tokenizer_loaded": True,
        "model_loaded": True,
        "forward_pass": True,
        "hidden_state_shape": list(hidden_shape),
        "dataset_accessed": False,
        "training_started": False,
        "test_used": False,
        "raw_mozilla_accessed": False,
        "status": "TRANSFORMER_RUNTIME_VERIFIED",
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print(f"TOKENIZER_LOADED=True")
    print(f"MODEL_LOADED=True")
    print(f"FORWARD_PASS=True")
    print(f"HIDDEN_STATE_SHAPE={hidden_shape}")
    print(f"OUTPUT={OUTPUT_PATH}")
    print("DATASET_ACCESSED=False")
    print("TRAINING_STARTED=False")
    print("TEST_USED=False")
    print("RAW_MOZILLA_ACCESSED=False")
    print("STATUS=TRANSFORMER_RUNTIME_VERIFIED")
    print("T3_MOD_024_COMPLETE")


if __name__ == "__main__":
    main()