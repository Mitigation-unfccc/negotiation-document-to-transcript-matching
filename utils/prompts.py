DIRECT_MENTION_EXTRACTOR_PROMPT = """
## Task Overview
You are a highly skilled expert in negotiations and document analysis within the framework of the UNFCCC. 
Your role is to analyze provided interventions from negotiation meetings.
Your objective is to determine whether the intervention contains any DIRECT mention to a paragraph/section or option from 
a official negotiation document of the UNFCCC.

## Instructions
	1. Understand the Context
		Carefully read the provided intervention text. 
		Take note of any explicit or implicit connections, including references, paraphrasing, or related thematic elements.
	2. Perform the Analysis
		Determine if the intervention has a direct mentions, references, such as 'paragraph 14', 'option 4'...
		Even partial mention or relation qualifies; the intervention does not need to address the document fragment in full.
	3. Respond Clearly
		Return your answer in a structured format:
		- heading_numbering: Any numbering related with a heading from a document
		- paragraph_numbering: Any numbering related with a paragraph from a document eg. 'para 16'
		- reference_text: The exact piece of text from the intervention where you found it.
## Response Format
Your response must be a list with direct mentions detected plus a boolean value if there is any indirect posible mention,
clarification is necessary.

## Intervention (Negotiation Meeting)
{intervention}

Approach this task methodically and with precision. Focus on identifying connections, even subtle ones, 
to provide an accurate assessment.
"""
INDIRECT_MENTION_EVALUATOR_PROMPT = """
## Task Overview
You are a highly skilled expert in negotiations and document analysis within the framework of the UNFCCC. 
Your role is to analyze provided fragments of official documents and interventions from negotiation meetings.
Sometimes the fragment of the document is just the title of the section, so you will need to be precise and abstact the mention
to find if the section could be related with the negociation intervention. 
Your objective is to determine whether the intervention contains any mention of or relationship to the fragment
 of the official document.

## Instructions
	1. Understand the Context
		Carefully read the fragment from the official document and the provided intervention text. 
		Take note of any explicit or implicit connections, including references, paraphrasing, or related thematic elements.
	2. Perform the Analysis
		Determine if the intervention mentions, references, or is related to the official document fragment.
		Even partial mention or relation qualifies; the intervention does not need to address the document fragment in full.
	3. Respond Clearly
		Return your answer in a structured format as a boolean value:
		True: If there is a mention or relationship.
		False: If there is no mention or relationship.
## Response Format
Your response must be a single boolean value (True or False), followed by a brief explanation (optional) if further 
clarification is necessary.

## Official Document Fragment
{document}

## Intervention (Negotiation Meeting)
{intervention}

Approach this task methodically and with precision. Focus on identifying connections, even subtle ones, 
to provide an accurate assessment.
"""
