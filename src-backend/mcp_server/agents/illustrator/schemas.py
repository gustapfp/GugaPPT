from pydantic import BaseModel, Field


class VisualAsset(BaseModel):
    slide_number: int
    asset_type: str = Field(description="'chart' or 'image'")
    description: str = Field(description="Description of what was generated/found")
    file_path: str = Field(description="Local path or URL to the asset")


class IllustrationResult(BaseModel):
    assets: list[VisualAsset]
