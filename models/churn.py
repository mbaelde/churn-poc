import pickle
from pathlib import Path
from typing import Optional

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

from utils.logger import setup_logger

log = setup_logger("churn_logger")


class ChurnModel:
    def __init__(self, preprocessors: Pipeline, model: Optional[BaseEstimator] = None):
        self._preprocessors = preprocessors
        self._model = model

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, new_model):
        self._model = new_model

    def deserialize(self, model_path: Path):
        # load prediction model
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def serialize(self, model_path: Path):
        with open(model_path, "wb") as model_file:
            pickle.dump(self.model, model_file)

    def _preprocess(self, X: pd.DataFrame) -> pd.DataFrame:
        return self._preprocessors.transform(X)

    def fit(self, X: pd.DataFrame, y: pd.DataFrame) -> BaseEstimator:
        self.model.fit(X, y)
        return self.model

    def train(
        self, X: pd.DataFrame, y: pd.DataFrame, preprocess_features: bool = True
    ) -> "ChurnModel":
        # Train your model here
        if preprocess_features:
            X = self._preprocess(X)
        self.fit(X, y)
        return self

    def predict(
        self, X: pd.DataFrame, preprocess_features: bool = True
    ) -> pd.DataFrame:
        # Use your model to make predictions here
        if preprocess_features:
            X = self._preprocess(X)
        return self.model.predict(X)
