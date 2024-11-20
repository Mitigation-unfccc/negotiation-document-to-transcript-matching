from pydantic import BaseModel


class NegotiationDocumentReference(BaseModel):
	heading_numbering: str | None
	paragraph_numbering: str | None
	reference_text: str


class DirectMentionExtractor(BaseModel):
	references: list[NegotiationDocumentReference]


class IndirectMentionEvaluator(BaseModel):
	contains_indirect_mention: bool


class MentionTreeEvaluator(BaseModel):
	is_relevant: bool