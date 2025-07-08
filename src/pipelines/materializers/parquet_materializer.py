import os
import pandas as pd
from zenml.materializers.base_materializer import BaseMaterializer
from zenml.enums import ArtifactType
from zenml.metadata.metadata_types import MetadataType
from typing import Dict, Any, Type

class ParquetDataFrameMaterializer(BaseMaterializer):
    ASSOCIATED_TYPES = (pd.DataFrame,)
    ASSOCIATED_ARTIFACT_TYPE = ArtifactType.DATA

    def load(self, data_type: Type[Any]) -> pd.DataFrame:
        filepath = os.path.join(self.uri, "data.parquet")
        with self.artifact_store.open(filepath, "rb") as f:
            return pd.read_parquet(f)

    def save(self, data: pd.DataFrame) -> None:
        filepath = os.path.join(self.uri, "data.parquet")
        with self.artifact_store.open(filepath, "wb") as f:
            data.to_parquet(f)

    def extract_metadata(self, data: pd.DataFrame) -> Dict[str, MetadataType]:
        """Extract useful metadata for tracking and display."""
        return {
            "num_rows": int(data.shape[0]),
            "num_columns": int(data.shape[1]),
            "columns": list(data.columns),
            # "dtypes": str(data.dtypes),
            "memory_usage": int(data.memory_usage(deep=True).sum()),
        }

    def save_visualizations(self, data: pd.DataFrame) -> Dict[str, str]:
        """Save visualizations to be shown in the ZenML dashboard."""
        # Save a CSV preview
        sample_path = os.path.join(self.uri, "sample.csv")
        with self.artifact_store.open(sample_path, "w") as f:
            f.write(data.head(10).to_csv(index=False))

        # Save summary statistics as markdown
        stats_path = os.path.join(self.uri, "summary.md")
        with self.artifact_store.open(stats_path, "w") as f:
            f.write("## DataFrame Summary\n")
            f.write(f"- **Rows:** {data.shape[0]}\n")
            f.write(f"- **Columns:** {data.shape[1]}\n")
            f.write("- **Sample Data:**\n\n")
            f.write(data.head().to_markdown(index=False))

        # Return paths and their visualization types
        return {
            sample_path: "csv",
            stats_path: "markdown"
        }