import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ml.engine import MLEngine
from app.config import settings

if __name__ == "__main__":
    print(f"Starting training for {settings.MODEL_TYPE}...")
    engine = MLEngine(model_type=settings.MODEL_TYPE)
    metrics = engine.train()
    print(f"Training complete. Metrics: {metrics}")
