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

# class ParquetSeriesMaterializer(BaseMaterializer):
#     ASSOCIATED_TYPES = (pd.Series,)
#     ASSOCIATED_ARTIFACT_TYPE = ArtifactType.DATA

#     def load(self, data_type: Type[pd.Series]) -> pd.Series:
#         filepath = os.path.join(self.uri, "data.parquet")
#         with self.artifact_store.open(filepath, "rb") as f:
#             return pd.read_parquet(f).iloc[:, 0]

#     def save(self, data: pd.Series) -> None:
#         filepath = os.path.join(self.uri, "data.parquet")
#         with self.artifact_store.open(filepath, "wb") as f:
#             data.to_frame().to_parquet(f)

#     def extract_metadata(self, data: pd.Series) -> Dict[str, MetadataType]:
#         return {
#             "num_elements": int(len(data)),
#             "dtype": str(data.dtype),
#             "memory_usage": int(data.memory_usage(deep=True)),
#         }

#     def save_visualizations(self, data: pd.Series) -> Dict[str, str]:
#         sample_path = os.path.join(self.uri, "sample.csv")
#         with self.artifact_store.open(sample_path, "w") as f:
#             f.write(data.head(10).to_string())

#         stats_path = os.path.join(self.uri, "summary.md")
#         with self.artifact_store.open(stats_path, "w") as f:
#             f.write("## Series Summary\n")
#             f.write(f"- **Elements:** {len(data)}\n")
#             f.write(f"- **Data Type:** {data.dtype}\n")
#             f.write("- **Sample Data:**\n\n")
#             f.write(data.head().to_string())

#         return {
#             sample_path: "csv",
#             stats_path: "markdown"
#         }


# class ParquetIndexMaterializer(BaseMaterializer):
#     ASSOCIATED_TYPES = (pd.Index,)
#     ASSOCIATED_ARTIFACT_TYPE = ArtifactType.DATA

#     def load(self, data_type: Type[pd.Index]) -> pd.Index:
#         filepath = os.path.join(self.uri, "data.parquet")
#         with self.artifact_store.open(filepath, "rb") as f:
#             df = pd.read_parquet(f)
#             return pd.Index(df.iloc[:, 0])

#     def save(self, data: pd.Index) -> None:
#         filepath = os.path.join(self.uri, "data.parquet")
#         with self.artifact_store.open(filepath, "wb") as f:
#             pd.DataFrame(data).to_parquet(f)

#     def extract_metadata(self, data: pd.Index) -> Dict[str, MetadataType]:
#         return {
#             "length": int(len(data)),
#             "dtype": str(data.dtype),
#             "is_unique": bool(data.is_unique),
#             "min": data.min() if len(data) > 0 else None,
#             "max": data.max() if len(data) > 0 else None,
#         }

#     def save_visualizations(self, data: pd.Index) -> Dict[str, str]:
#         summary_path = os.path.join(self.uri, "index_summary.md")
#         with self.artifact_store.open(summary_path, "w") as f:
#             f.write("## Index Summary\n")
#             f.write(f"- **Length:** {len(data)}\n")
#             f.write(f"- **Data Type:** {data.dtype}\n")
#             f.write(f"- **Unique:** {data.is_unique}\n")
#             f.write("- **First 5 Elements:**\n")
#             f.write(str(data[:5]))
#         return {summary_path: "markdown"}