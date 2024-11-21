from pydantic import BaseModel, Field

class MentionTreeSearchEvaluator(BaseModel):
	contains_mention: bool = Field(description="True if contains mention or relation False otherwise")
	textual_reference: str = Field(description="Exact textual reference used for evaluation, it is imperative that it is exactly the same text from the input.")
	mention_type: str = Field(description="Whether the mention is 'DIRECT' (explicit) or 'INDIRECT' (implicit)")
