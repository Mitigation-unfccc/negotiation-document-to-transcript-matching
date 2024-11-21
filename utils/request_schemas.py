from pydantic import BaseModel, Field


class NegotiationDocumentReference(BaseModel):
	heading_numbering: str | None = Field(
		description="""
		Any numbering related with a heading (also mentioned as section) from a document, which for negotiations documents have the following format (in order of hierarchy):
		- Heading:	Uppercase roman numerals followed by a "." (regex: r"((?:M{0,3})(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})\.)")
		- SubHeading: Uppercase letters followed by a "." (regex: r"([A-Z]+\.)")
		- SubsubHeading: Number followed by a "." (regex: r"(\d+\.)")
		- SubsubsubHeading: Lowercase letters encased between "()" (regex: r"(\([a-z]+\))")
		
		It is imperative that the output is given as solely the numbering mentioned with the correct format to be parsed by the given regexes.
		Examples: "IV.", "A.", "3.", "(v)", ...
		In the cases where several hierarchical levels are mentioned, separate them by ";".
		Examples: "IV.;B.;2.", "II.;A.", "VII.;C.;2.;(ii)", ...
		If a sublevel is mentioned but the higher hierarchical levels, replace the missing levels by "#".
		Examples: "#.;#.;2.", "#.;A.", "VII.;#.;2.;(ii)", ...
		"""
	)
	paragraph_numbering: str | None = Field(
		description="""
		Any numbering related with a paragraph (also mentioned as para or text) from a document, which for negotiations documents have the following format (in order of hierarchy):
		- Paragraph: Number followed by a "." (regex:  r"(\d+\.)")
		- SubParagraph: Lowercase letters encased between "()" (regex: r"(\([a-z]+\))")
		- SubsubParagraph: Lowercase roman numerals encased between "()" (regex: r"(\((?:m{0,3})(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})\))")
		- SubsubsubParagraph: Lowercase letters followed by "." (regex: r"([a-z]+\.)")
		
		It is imperative that the output is given as solely the numbering mentioned with the correct format to be parsed by the given regexes.
		Examples: "23.", "(a)", "(iv)", "b.", ...
		In the cases where several hierarchical levels are mentioned, separate them by ";".
		Examples: "23.;(a);(iv)", "12.;(d)", "15.;(c);(i);1.", ...
		If a sublevel is mentioned but the higher hierarchical levels, replace the missing levels by "#".
		Examples: "#.;#.;(iv)", "#.;(b)", "23.;#.;(v);3.", ...		
		"""
	)
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
