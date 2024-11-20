from parser import NaiveDecisionParser, NaiveDecisionParserDocument, NaiveDecisionParserText, NaiveDecisionParserTextLevel
import random

class NegotiationDocumentToTranscriptMatching:

	def __init__(self, doc_content: NaiveDecisionParserDocument):
		self.doc_content: NaiveDecisionParserDocument = doc_content
		pass
	
	@staticmethod
	def dummy_decide(selected_content: NaiveDecisionParserDocument) -> bool:
		prob_true = 0.00
		return [random.choice([True]*int(prob_true*100) + [False]*int((1-prob_true)*100)) for content in selected_content]

	def mention_tree_search(self) -> NaiveDecisionParserDocument:
		"""_summary_

		:return: _description_
		"""

		# Root level pass
		print("@"*42)
		selected_content, decided_content = self._mention_tree_search_iteration(
			selected_content=self.doc_content
		)
		print("@"*42)
		# Tree traverse
		while len(selected_content) != 0:
			selected_content, _decided_content = self._mention_tree_search_iteration(
				selected_content=selected_content
			)
			decided_content += _decided_content
			print("@"*42)	

		print("\n############\n".join([x.__str__() for x in decided_content]))

	
	def _mention_tree_search_iteration(
			self, selected_content: NaiveDecisionParserDocument
		) -> tuple[NaiveDecisionParserDocument, NaiveDecisionParserDocument]:
		"""_summary_

		:param selected_content: _description_
		:return: _description_
		"""

		continue_search_batch: list[bool] = self.dummy_decide(selected_content=selected_content)

		_selected_content: NaiveDecisionParserDocument = []
		decided_content: NaiveDecisionParserDocument = []
		for content, continue_search in zip(selected_content, continue_search_batch):
			if continue_search:
				if len(content.children) == 0:
					decided_content.append(content)
					print("!decided", content.numbering, content.text)
				else:
					if content.level.value >= NaiveDecisionParserTextLevel.Paragraph.value:
						_selected_content += self._unpack_paragraph_children(content=content)
					else:
						_selected_content += content.children
					print("!selected", content.numbering, content.text)

		return _selected_content, decided_content
	
	def _unpack_paragraph_children(
			self, content: NaiveDecisionParserText
		) -> NaiveDecisionParserDocument:
		"""_summary_

		:param content: _description_
		:return: _description_
		"""
		if len(content.children) == 0:
			return [content]
		
		unpacked_children_content: NaiveDecisionParserDocument = []
		for children_content in content.children:
			unpacked_children_content += self._unpack_paragraph_children(content=children_content)
		
		return unpacked_children_content

if __name__ == "__main__":
	f_input = "/home/ptarnav/cop29/negotiation-document-parser/Art_6.2_SBSTA_13a_DD_1stIteration_241114_published.docx"
	x = NegotiationDocumentToTranscriptMatching(doc_content=NaiveDecisionParser(input_path=f_input).doc_content)
	x.mention_tree_search()