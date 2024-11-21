import os
from typing import Optional
from pydantic import BaseModel

from parser import NaiveDecisionParser, NaiveDecisionParserDocument, NaiveDecisionParserText, NaiveDecisionParserTextLevel
from utils.prompts import DIRECT_MENTION_EXTRACTOR_PROMPT, INDIRECT_MENTION_EVALUATOR_PROMPT
from utils.transcript_parser import TranscriptParser
from utils.request_schemas import DirectMentionExtractor, IndirectMentionEvaluator
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback

from dotenv import load_dotenv, find_dotenv
if load_dotenv(find_dotenv()):
	os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
else:
	raise ValueError("Please set environment variables (.env not found)")


class Intervention(BaseModel):
	oid: int
	hour: str
	participant: str
	paragraph: str
	direct_mentions: Optional[NaiveDecisionParserDocument] = None
	indirect_mentions: Optional[NaiveDecisionParserDocument] = None
	contains_indirect: Optional[bool] = None

	def __str__(self):
		s: str = f"{self.participant} - [{self.hour}]\n"
		s += f"{self.paragraph}\n"
		if self.direct_mentions is not None:
			s += f"{len(self.direct_mentions.references)} direct mentions:\n"
			for direct_mention in self.direct_mentions:
				s += f"=>\t{direct_mention}\n"
		if self.indirect_mentions is not None:
			s += f"{len(self.indirect_mentions)} indirect mentions:\n"
			for indirect_mention in self.indirect_mentions:
				s += f"=>\t{indirect_mention.__str__()}\n"
		return s


class NegotiationDocumentToTranscriptMatching:

	def __init__(self, doc_content: NaiveDecisionParserDocument, transcript: list[Intervention]):
		self.doc_content: NaiveDecisionParserDocument = doc_content
		self.transcript: list[Intervention] = transcript
		self._load_models()
		self.total_cost = 0.0

	def _load_models(self):
		"""Load the LLM models necessary to detect mentions from the document
		:return:
		"""
		llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
		self.direct_llm = llm.with_structured_output(DirectMentionExtractor)
		self.indirect_llm = llm.with_structured_output(IndirectMentionEvaluator)

	def contains_direct_mentions(self):
		"""Loops through all the interventions in the transcript searchin for direct or possible indirect mentions
		:return:
		"""
		prompts = [
			[{"role": "system", "content": DIRECT_MENTION_EXTRACTOR_PROMPT.format(intervention=intervention.paragraph)}]
			for intervention in self.transcript
		]
		with get_openai_callback() as cb:
			self.direct_mentions: list[DirectMentionExtractor] = self.direct_llm.batch(prompts)
		self.total_cost += cb.total_cost
		for intervention, direct_mention in zip(self.transcript, self.direct_mentions):
			intervention.direct_mentions = direct_mention
			intervention.contains_indirect = direct_mention.indirect_mention
	
	def _get_content_from_direct_mention(self, direct_mention: DirectMentionExtractor) -> NaiveDecisionParserText:
		"""_summary_

		:param direct_mention: _description_
		:return: _description_
		"""
		


	def contains_indirect_mentions(self):
		"""Loops through all the interventions in the transcript searching for indirect mentions"""
		for intervention in self.transcript:
			if intervention.contains_indirect:
				intervention.indirect_mentions = self.mention_tree_search(intervention)

	def mention_tree_search(self, intervention: Intervention) -> NaiveDecisionParserDocument:
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
		) -> tuple[NaiveDecisionParserDocument, NaiveDecisionParserDocument]:
		"""_summary_

		:param selected_content: _description_
		:return: _description_
		"""

		prompts = [
			[{
				"role": "system",
				"content": INDIRECT_MENTION_EVALUATOR_PROMPT.format(
					document=document.__str__(), intervention=intervention.paragraph
				)
			}]
			for document in selected_content
		]
		with get_openai_callback() as cb:
			continue_search_batch: list[IndirectMentionEvaluator] = self.indirect_llm.batch(prompts)
		self.total_cost += cb.total_cost

		_selected_content: NaiveDecisionParserDocument = []
		decided_content: NaiveDecisionParserDocument = []
		for content, continue_search in zip(selected_content, continue_search_batch):
			if continue_search.contains_indirect_mention:
				if len(content.children) == 0:
					decided_content.append(content)
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
		self.contains_direct_mentions()
		self.contains_indirect_mentions()


if __name__ == "__main__":
	f_input = "Art_6.2_CMA_15a_DD_Party Inputs.docx"
	transcript_path = "A62 IC 3.txt"
	parser = TranscriptParser(input_file=transcript_path, folder_name="")
	interventions = [Intervention(**intervention_dict) for intervention_dict in parser()]
	x = NegotiationDocumentToTranscriptMatching(
		doc_content=NaiveDecisionParser(input_path=f_input).doc_content,
		transcript=interventions[5:11])
	x()
	for intervention in x.transcript:
		print(intervention)
		print()
	print("#"*42)
	print(x.total_cost)
