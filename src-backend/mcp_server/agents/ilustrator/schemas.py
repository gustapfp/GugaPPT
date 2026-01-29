from pydantic import BaseModel, Field
from typing import List


class VisualAsset(BaseModel):
    slide_number: int
    asset_type: str = Field(description="'chart' or 'image'")
    description: str = Field(description="Description of what was generated/found")
    file_path: str = Field(description="Local path or URL to the asset")


class IllustrationResult(BaseModel):
    assets: List[VisualAsset]
