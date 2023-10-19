import pickle
from pathlib import Path
from typing import List, Optional

import pandas as pd
from sklearn.preprocessing import LabelEncoder


class FeaturePreprocessor:
    """
    FeaturePreprocessor is a class for fitting and transforming data using a feature preprocessing
    model.

    Args:
        model: The feature preprocessing model to be used.
        encoded_variables (List[str]): A list of encoded variable names.

    Attributes:
        _model: The feature preprocessing model.
        _encoded_variables (List[str]): A list of encoded variable names.

    Methods:
        fit(X: pd.DataFrame) -> "FeaturePreprocessor":
            Fit the feature preprocessing model on the provided DataFrame.

        transform(X: pd.DataFrame) -> pd.DataFrame:
            Transform the provided DataFrame using the fitted feature preprocessing model.

        fit_transform(X: pd.DataFrame) -> pd.DataFrame:
            Fit and transform the provided DataFrame using the feature preprocessing model.

        serialize(feature_preprocessor_path: Path):
            Serialize the feature preprocessing model to a binary file.

        deserialize(feature_preprocessor_path: Path):
            Deserialize the feature preprocessing model from a binary file.

        get_feature_names(features: List[str]) -> List[str]:
            Get the feature names after transformation, if available.

    """

    def __init__(
        self,
        model,
        encoded_variables: List[str],
        output_variables: List[str],
        transform_to_dataframe: bool = False,
    ):
        self._model = model
        self._encoded_variables = encoded_variables
        self._output_variables = output_variables
        self._transform_to_dataframe = transform_to_dataframe

    @property
    def model(self):
        """
        The feature preprocessing model used for fitting and transforming data.
        """
        return self._model

    def fit(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> "FeaturePreprocessor":
        """
        Fit the feature preprocessing model on the provided DataFrame.

        Args:
            X (pd.DataFrame): The DataFrame containing the data to be transformed.

        Returns:
            FeaturePreprocessor: The fitted FeaturePreprocessor instance.

        """
        self._model.fit(X[self._encoded_variables])

    def transform(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Transform the provided DataFrame using the fitted feature preprocessing model.

        Args:
            X (pd.DataFrame): The DataFrame to be transformed.

        Returns:
            pd.DataFrame: The transformed DataFrame.

        """
        data = X.copy()
        if self._transform_to_dataframe:
            transformed_data = self._model.transform(data[self._encoded_variables])
            nominal_columns = self.get_feature_names(self._encoded_variables)
            transformed_data = pd.DataFrame(transformed_data, index=data.index, columns=nominal_columns)
            data = pd.concat(
                [data.drop(columns=self._encoded_variables), transformed_data], axis=1
            )
        else:
            data[self._output_variables] = self._model.transform(
                data[self._encoded_variables]
            )
        return data

    def fit_transform(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Fit and transform the provided DataFrame using the feature preprocessing model.

        Args:
            X (pd.DataFrame): The DataFrame containing the data to be transformed.

        Returns:
            pd.DataFrame: The transformed DataFrame.

        """
        self.fit(X, y)
        return self.transform(X, y)

    def serialize(self, feature_preprocessor_path: Path):
        """
        Serialize the feature preprocessing model to a binary file.

        Args:
            feature_preprocessor_path (Path): The path to the binary file for serialization.

        """
        with open(feature_preprocessor_path, "wb") as f:
            pickle.dump(self.model, f)

    def deserialize(self, feature_preprocessor_path: Path):
        """
        Deserialize the feature preprocessing model from a binary file.

        Args:
            feature_preprocessor_path (Path): The path to the binary file for deserialization.

        """
        with open(feature_preprocessor_path, "rb") as f:
            self._model = pickle.load(f)

    def get_feature_names(self, features: List[str]) -> List[str]:
        """
        Get the feature names after transformation, if available.

        Args:
            features (List[str]): A list of feature names.

        Returns:
            List[str]: Transformed feature names if available, or an empty list.

        """
        try:
            return self._model.get_feature_names(features)
        except AttributeError:
            return []


class MultiColumnLabelEncoder:
    def __init__(self, encoded_variables: List[str]):
        """
        Initialize a MultiColumnLabelEncoder.

        Args:
            encoded_variables (List[str]): A list of variable names to be encoded.

        Returns:
            None
        """
        self._encoded_variables = encoded_variables
        self._model = {var: LabelEncoder() for var in encoded_variables}

    def fit(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> "MultiColumnLabelEncoder":
        """
        Fit the MultiColumnLabelEncoder.

        Args:
            X (pd.DataFrame): Input data with encoded variables.

        Returns:
            self: The MultiColumnLabelEncoder instance.
        """
        for var in self._encoded_variables:
            self._model[var].fit(X[var])

    def transform(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Transform data to encode the specified variables.

        Args:
            X (pd.DataFrame): Input data with variables to be encoded.

        Returns:
            pd.DataFrame: Transformed data with encoded variables.
        """
        data = X.copy()
        for var in self._encoded_variables:
            data[var] = self._model[var].transform(data[var])
        return data

    def fit_transform(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Fit and transform the input data to encode the specified variables.

        Args:
            X (pd.DataFrame): Input data with variables to be encoded.

        Returns:
            pd.DataFrame: Transformed data with encoded variables.
        """
        self.fit(X, y)
        return self.transform(X, y)

    def serialize(self, feature_preprocessor_path: Path):
        """
        Serialize the encoding models to binary files.

        Args:
            feature_preprocessor_path (Path): Path to the binary files.

        Returns:
            None
        """
        for var in self._encoded_variables:
            path = feature_preprocessor_path.with_name(
                f"{feature_preprocessor_path.stem}_{var}{feature_preprocessor_path.suffix}"
            )
            with open(path, "wb") as f:
                pickle.dump(self._model[var], f)

    def deserialize(self, feature_preprocessor_path: Path):
        """
        Deserialize the encoding models from binary files.

        Args:
            feature_preprocessor_path (Path): Path to the binary files.

        Returns:
            None
        """
        for var in self._encoded_variables:
            path = feature_preprocessor_path.with_name(
                f"{feature_preprocessor_path.stem}_{var}{feature_preprocessor_path.suffix}"
            )
            with open(path, "rb") as f:
                self._model[var] = pickle.load(f)


class TenureBinarizer:
    def __init__(self, bins, labels):
        """
        Initialize a TenureBinarizer.

        Args:
            bins: The bin edges for binning the tenure values.
            labels: The labels for each tenure bin.

        Returns:
            None
        """
        self._bins = bins
        self._labels = labels

    def fit(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> "TenureBinarizer":
        """
        Fit the TenureBinarizer.

        Args:
            X (pd.DataFrame): Input data (not used for fitting).

        Returns:
            self: The TenureBinarizer instance.
        """
        return self

    def transform(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Transform tenure values into bins and add a 'TenureGroup' column.

        Args:
            X (pd.DataFrame): Input data with a 'tenure' column.

        Returns:
            pd.DataFrame: Transformed data with 'TenureGroup' column added.
        """
        data = X.copy()
        data["TenureGroup"] = pd.cut(
            data["tenure"],
            bins=self._bins,
            labels=self._labels,
        )
        return data

    def fit_transform(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Fit and transform the input data.

        Args:
            X (pd.DataFrame): Input data with a 'tenure' column.

        Returns:
            pd.DataFrame: Transformed data with 'TenureGroup' column added.
        """
        self.fit(X)
        return self.transform(X)


class RatioComputer:
    def __init__(self, numerator: str, denominator: str, ratio_name: str):
        """
        Initialize a RatioComputer.

        Args:
            numerator (str): The name of the numerator column.
            denominator (str): The name of the denominator column.
            ratio_name (str): The name of the computed ratio column.

        Returns:
            None
        """
        self._numerator = numerator
        self._denominator = denominator
        self._ratio_name = ratio_name

    def fit(self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None) -> "RatioComputer":
        """
        Fit the RatioComputer.

        Args:
            X (pd.DataFrame): Input data (not used for fitting).

        Returns:
            self: The RatioComputer instance.
        """
        return self

    def transform(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Transform data to compute the specified ratio.

        Args:
            X (pd.DataFrame): Input data with appropriate columns.

        Returns:
            pd.DataFrame: Transformed data with the computed ratio added.
        """
        data = X.copy()
        data[self._ratio_name] = data[self._numerator] / data[self._denominator]
        return data

    def fit_transform(
        self, X: pd.DataFrame, y: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Fit and transform the input data to compute the specified ratio.

        Args:
            X (pd.DataFrame): Input data with appropriate columns.

        Returns:
            pd.DataFrame: Transformed data with the computed ratio added.
        """
        self.fit(X, y)
        return self.transform(X, y)
