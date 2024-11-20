from pydantic import BaseModel, Field


class NegotiationDocumentReference(BaseModel):
	heading_numbering: str | None = Field(description="")
	paragraph_numbering: str | None = Field(description="")
	reference_text: str = Field(description="Exact textual reference used to extract the heading numbering and the paragraph numbering. It is imperative that it is exactly the same text from the input.")


class DirectMentionExtractor(BaseModel):
	references: list[NegotiationDocumentReference] = Field(description="")


class IndirectMentionEvaluator(BaseModel):
	contains_indirect_mention: bool


class MentionTreeSearchEvaluator(BaseModel):
	is_relevant: bool