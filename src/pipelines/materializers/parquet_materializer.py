import os
import pandas as pd
from zenml.materializers.base_materializer import BaseMaterializer
from zenml.enums import ArtifactType

class ParquetDataFrameMaterializer(BaseMaterializer):
    ASSOCIATED_TYPES = (pd.DataFrame,)
    ASSOCIATED_ARTIFACT_TYPE = ArtifactType.DATA

    def load(self, data_type: type) -> pd.DataFrame:
        filepath = os.path.join(self.uri, "data.parquet")
        with self.artifact_store.open(filepath, "rb") as f:
            return pd.read_parquet(f)

    def save(self, data: pd.DataFrame) -> None:
        filepath = os.path.join(self.uri, "data.parquet")
        with self.artifact_store.open(filepath, "wb") as f:
            data.to_parquet(f)