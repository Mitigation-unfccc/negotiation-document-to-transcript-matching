from pydantic import BaseModel, Field


class NegotiationDocumentReference(BaseModel):
	heading_numbering: str | None = Field(description="Any numbering related with a heading from a document")
	paragraph_numbering: str | None = Field(description="Any numbering related with a paragraph from a document eg. 'para 16'")
	reference_text: str = Field(description="Exact textual reference used to extract the heading numbering and the "
									"paragraph numbering. It is imperative that it is exactly the same text from the input.")


class DirectMentionExtractor(BaseModel):
	references: list[NegotiationDocumentReference] = Field(description="List with all the direct mentions, if there are not should be an empty list")
	indirect_mention: bool = Field(description="Boolean value True if may contain a indirect mention to a document False if not")


class IndirectMentionEvaluator(BaseModel):
	contains_indirect_mention: bool = Field(description="True if contains mention or relation False if not")
	reason: str = Field(description="The reason you consider the intervention contains or not a mention/relation")


class MentionTreeSearchEvaluator(BaseModel):
	is_relevant: bool
