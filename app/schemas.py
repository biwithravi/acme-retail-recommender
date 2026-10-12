from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.config import DEFAULT_TOP_N, MAX_TOP_N


class RecommendRequest(BaseModel):
    product_id: Optional[str] = Field(None, examples=["ACME_000001"])
    text: Optional[str] = Field(None, examples=["men's running shoes"])
    top_n: int = Field(DEFAULT_TOP_N, ge=1, le=MAX_TOP_N)
    category: Optional[str] = Field(None, description="Restrict results to one main_category")

    @model_validator(mode="after")
    def need_one_input(self):
        if not (self.product_id or (self.text and self.text.strip())):
            raise ValueError("Provide either 'product_id' or 'text'.")
        return self


class BasketRequest(BaseModel):
    product_ids: list[str] = Field(..., min_length=1, max_length=50)
    top_n: int = Field(12, ge=1, le=MAX_TOP_N)
