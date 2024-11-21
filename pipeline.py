import os
from typing import Optional, Literal
from pydantic import BaseModel

from parser import NaiveDecisionParser, NaiveDecisionParserDocument, NaiveDecisionParserText, NaiveDecisionParserTextLevel
from utils.transcript_parser import TranscriptParser

from utils.prompts import MENTION_TREE_SEARCH_EVALUATOR_PROMPT
from utils.request_schemas import MentionTreeSearchEvaluator

from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback

from dotenv import load_dotenv, find_dotenv
if load_dotenv(find_dotenv()):
	os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
else:
	raise ValueError("Please set environment variables (.env not found)")


class Mention(BaseModel):
	content: NaiveDecisionParserText
	textual_reference: str
	mention_type: str


class Intervention(BaseModel):
	oid: int
	hour: str
	participant: str
	paragraph: str
	mentions: Optional[list[Mention]] = None

	def __str__(self):
		s: str = f"{self.participant} - [{self.hour}]\n"
		s += f"{self.paragraph}\n"
		if self.mentions is not None:
			s += f"{len(self.mentions)} mentions:\n"
			for mention in self.mentions:
				s += f"Document fragment:\n\t{mention.content.__str__()}\n"
				s += f"~[{mention.mention_type}]~>\t{mention.textual_reference}\n"
		return s


class NegotiationDocumentToTranscriptMatching:

	def __init__(self, doc_content: NaiveDecisionParserDocument, transcript: list[Intervention]):
		self.doc_content: NaiveDecisionParserDocument = doc_content
		self.transcript: list[Intervention] = transcript
		self._load_models()
		self.total_cost = 0.0

	def _load_models(self):
		"""Load the necessary LLMs
		"""
		llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
		self.mention_tree_search_evaluator = llm.with_structured_output(MentionTreeSearchEvaluator)

	def mention_tree_search(self, intervention: Intervention) -> list[Mention]:
		"""_summary_

		:return: _description_
		"""

		# Root level pass
		selected_content, decided_content = self._mention_tree_search_iteration(
			selected_content=self.doc_content,
			intervention=intervention
		)
		
		# Tree traverse
		while len(selected_content) != 0:
			selected_content, _decided_content = self._mention_tree_search_iteration(
				selected_content=selected_content,
			intervention=intervention
			)
			decided_content += _decided_content

		return decided_content

	def _mention_tree_search_iteration(
			self, selected_content: NaiveDecisionParserDocument,
			intervention: Intervention
		) -> tuple[NaiveDecisionParserDocument, list[Mention]]:
		"""_summary_

		:param selected_content: _description_
		:return: _description_
		"""

		prompts = [
			[{
				"role": "system",
				"content": MENTION_TREE_SEARCH_EVALUATOR_PROMPT.format(
					document=document_text.__str__(), intervention=intervention.paragraph
				)
			}]
			for document_text in selected_content
		]
		with get_openai_callback() as cb:
			continue_search_batch: list[MentionTreeSearchEvaluator] = self.mention_tree_search_evaluator.batch(prompts)
		self.total_cost += cb.total_cost

		_selected_content: NaiveDecisionParserDocument = []
		decided_content: NaiveDecisionParserDocument = []
		for content, continue_search in zip(selected_content, continue_search_batch):
			if continue_search.contains_mention:
				if len(content.children) == 0:
					decided_content.append(
						Mention(
							content=content,
							textual_reference=continue_search.textual_reference,
							mention_type=continue_search.mention_type
						)
					)
				else:
					if content.level.value >= NaiveDecisionParserTextLevel.Paragraph.value:
						_selected_content += self._unpack_paragraph_children(content=content)
					else:
						_selected_content += content.children

		return _selected_content, decided_content
	
	def _unpack_paragraph_children(
			self, content: NaiveDecisionParserText
		) -> NaiveDecisionParserDocument:
		"""_summary_

		:param content: _description_
		:return: _description_
		"""

		# Root case
		if len(content.children) == 0:
			return [content]
		
		# Recursive case
		unpacked_children_content: NaiveDecisionParserDocument = []
		for children_content in content.children:
			unpacked_children_content += self._unpack_paragraph_children(content=children_content)
		
		return unpacked_children_content

	def __call__(self):
		for intervention in self.transcript:
			intervention.mentions = self.mention_tree_search(intervention=intervention)
			print(intervention)


if __name__ == "__main__":
	f_input = "Art_6.2_CMA_15a_DD_Party Inputs.docx"
	negotiation_document = NaiveDecisionParser(input_path=f_input).doc_content

	transcript_path = "A62 IC 3.txt"
	parser = TranscriptParser(input_file=transcript_path, folder_name="")
	interventions = [Intervention(**intervention_dict) for intervention_dict in parser()]

	x = NegotiationDocumentToTranscriptMatching(
		doc_content=negotiation_document, transcript=interventions
	)
	x()
	with open("test.txt", "w") as f:
		f.writelines([f"{intervention.__str__()}\n{'-'*42}\n" for intervention in x.transcript])
		
	print("#"*42)
	print(x.total_cost)
