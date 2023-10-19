import pickle
from pathlib import Path
from typing import Optional

import pandas as pd
from sklearn.pipeline import Pipeline


class ChurnModel:
    def __init__(self, preprocessors: Pipeline, model: Optional = None):
        self._preprocessors = preprocessors
        self._model = model

    def deserialize(self, processed_data_dir: Path):
        # load prediction model
        with open(processed_data_dir.joinpath("churn_model.pkl"), "rb") as f:
            self.model = pickle.load(f)

    def preprocess(self, X: pd.DataFrame) -> pd.DataFrame:
        return self._preprocessors.transform(X)

    def train(self, X: pd.DataFrame, y: pd.DataFrame) -> "ChurnModel":
        # Train your model here
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        # Use your model to make predictions here
        return self.model.predict(X)
