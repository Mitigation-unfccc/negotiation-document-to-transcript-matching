from __future__ import annotations

import subprocess
import re

from enum import Enum
from pydantic import BaseModel


class NaiveDecisionParserTextLevel(Enum):
	Undefined = 0
	Heading = 1
	Subheading = 2
	Subsubheading = 3
	Subsubsubheading = 4
	Subsubsubsubheading = 5
	Paragraph = 6
	Subparagraph = 7
	Subsubparagraph = 8
	Subsubsubparagraph = 9


class NaiveDecisionParserText(BaseModel):
	level: NaiveDecisionParserTextLevel
	parent: NaiveDecisionParserText | None
	children: list[NaiveDecisionParserText] = []
	numbering: str
	text: str

	def __str__(self):
		return f"{self.parent.__str__() if self.parent is not None else ''}\n{'    ' * self.level.value}{self.numbering} => {self.text}"


NaiveDecisionParserDocument = list[NaiveDecisionParserText]


class NaiveDecisionParser:
	"""
	Basic .docx document file parser for decision documents,
	 naive in the sense that it just parses the text into a string list representation,
	 and then custom regex templates to capture the structure of the decision document
	Using libreoffice under the hood to simulate the export .txt option.

	It does not parse text that is not numbered or tables.
	"""

	heading_numbering_pattern: str = r"((?:M{0,3})(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})\.)"  # Uppercase roman numerals.
	subheading_numbering_pattern: str = r"([A-Z]+\.)"  # Uppercase letters.
	subsubheading_numbering_pattern: str = r"(\d+\.)"  # Numbers.
	subsubsubheading_numbering_pattern: str = r"(\([a-z]+\))"  # (Lowercase roman numerals)

	paragraph_numbering_pattern: str = r"(\d+\.)"  # Numbers.
	subparagraph_numbering_pattern: str = r"(\([a-z]+\))"  # (Lowercase letters)
	subsubparagraph_numbering_pattern: str = r"(\((?:m{0,3})(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})\))"  # (Lowercase roman numerals)
	subsubsubparagraph_numbering_pattern: str = r"([a-z]+\.)"  # Lowercase letters.

	def get_numbering_pattern_from_text_level(self, level: NaiveDecisionParserTextLevel) -> str:
		"""Obtains the corresponding numbering regex pattern for a given 
		 NaiveDecisionParserTextLevel, which are defined above.

		:param level: NaiveDecisionParserTextLevel object
		:raises ValueError: When no correspondent regex numbering pattern defined for the level
		:return: Regex numbering pattern
		"""
		match level:
			case NaiveDecisionParserTextLevel.Heading:
				return self.heading_numbering_pattern
			case NaiveDecisionParserTextLevel.Subheading:
				return self.subheading_numbering_pattern
			case NaiveDecisionParserTextLevel.Subsubheading:
				return self.subsubheading_numbering_pattern
			case NaiveDecisionParserTextLevel.Subsubsubheading:
				return self.subsubsubheading_numbering_pattern
			case NaiveDecisionParserTextLevel.Paragraph:
				return self.paragraph_numbering_pattern
			case NaiveDecisionParserTextLevel.Subparagraph:
				return self.subparagraph_numbering_pattern
			case NaiveDecisionParserTextLevel.Subsubparagraph:
				return self.subsubparagraph_numbering_pattern
			case NaiveDecisionParserTextLevel.Subsubsubparagraph:
				return self.subsubsubparagraph_numbering_pattern
			case _:
				raise ValueError(f"Cannot find regex numbering pattern for: {level}")

	def __init__(self, input_path: str) -> None:
		self.input_path = input_path
		self.txt_path = f"{self.input_path.removesuffix('.docx')}.txt"

		# Convert and load .docx document as .txt raw string list representation
		self.convert_docx_to_text(input_path=self.input_path)
		self.raw_doc_content = self.load_parsed_docx_content(txt_path=self.txt_path)

		self.clean_doc_content = self._clean_raw_doc_content()
		self.doc_content: NaiveDecisionParserDocument = self._structure_clean_doc_content()

	@staticmethod
	def convert_docx_to_text(input_path: str) -> None:
		"""Converts .docx to plain .txt using libreoffice command,
		 the output file will have the same name as the input file but with the .txt extension

		:param input_path: Path of the input .docx file
		"""
		# File extension validation already taken care of by libreoffice
		try:
			# Run LibreOffice headless command to convert the file from .docx to .txt
			subprocess.run(
				[
					"libreoffice", "--headless", "--convert-to", "txt:Text",
					input_path, "--outdir", "."
				],
				check=True
			)
			print("Conversion to .txt using libreoffice successful")
		except subprocess.CalledProcessError as e:
			print(f"Error during export: {e}")

	@staticmethod
	def load_parsed_docx_content(txt_path: str) -> list[str]:
		"""Loads the previously parsed .docx to .txt document into a raw list of strings

		:param txt_path: Path of the input .txt file
		:raises ValueError: If .txt is empty and therefore no lines were loaded
		:return: String list representation of the .txt file
		"""

		doc_content: list[str] = []
		with open(file=txt_path, mode="r", encoding="utf-8") as f:
			doc_content = f.readlines()

		if len(doc_content) > 0:
			return doc_content
		else:
			raise ValueError("Document to be processed is empty")

	def _clean_raw_doc_content(self) -> list[str]:
		"""Cleans raw string list representation of the parsed .docx file:
		 - Remove empty lines
		 - Remove lines that do not start with:
		 	- Uppercase roman numeral.
			- Uppercase letters.
			- Number.
			- (Lowercase letters)
			- (Lowercase roman numeral)
			- (Number)

		:return: Clean string list representation of the .txt file
		"""

		clean_doc_content: list[str] = [
			line for line in self.raw_doc_content if line.strip() != ""
		]

		pattern: str = (
			rf"^("
			rf"{self.heading_numbering_pattern}|"
			rf"{self.subheading_numbering_pattern}|"
			rf"{self.subsubheading_numbering_pattern}|"
			rf"{self.subsubsubheading_numbering_pattern}|"
			rf"{self.paragraph_numbering_pattern}|"
			rf"{self.subparagraph_numbering_pattern}|"
			rf"{self.subsubparagraph_numbering_pattern}|"
			rf"{self.subsubsubparagraph_numbering_pattern}"
			rf")\s"
		)
		clean_doc_content = [
			line for line in clean_doc_content if re.match(pattern, line.lstrip())
		]

		return clean_doc_content

	@staticmethod
	def get_text_level(line: str) -> NaiveDecisionParserTextLevel:
		"""Obtains the correspondent NaiveDecisionParserTextLevel
		 based on the left indentation depth, where each depth level is represented by
		 either 4 spaces or a \t character.

		:param line: Raw line string
		:return: NaiveDecisionParserTextLevel based on the left indentation depth
		"""

		# Match leading tabs or groups of 4 spaces
		match = re.match(r'^((\t| {4})*)', line)
		if match:
			# Count the total number of matched indentations
			return NaiveDecisionParserTextLevel(len(match.group(1)) // 4 + match.group(1).count('\t'))
		return NaiveDecisionParserTextLevel(0)

	def _get_parent_text(
			self, prev_text: NaiveDecisionParserText, text_level: NaiveDecisionParserTextLevel
		) -> NaiveDecisionParserText:
		"""Given a previous text and a the text level of the current text,
		 find the parent text of the current text.
		Recursive algorithm where:
		 - When current text is a sublevel of the previous text, then it is assigned as the parent
		 - When current text is of the same level of the previous text, then they share the parent
		 - Otherwise, recursively do the same but with the previous text parent instead

		:param prev_text: Previous text used to capture the parent of the current text
		:param text_level: Current text level (
		 as the full current text object has not been yet constructed
		)
		:return: The current text parent object (None if it is a root text)
		"""

		if prev_text is not None:
			if prev_text.level.value < text_level.value:
				return prev_text
			elif prev_text.level.value == text_level.value:
				return prev_text.parent
			elif prev_text.level.value > text_level.value:
				return self._get_parent_text(prev_text=prev_text.parent, text_level=text_level)

		return None

	def _structure_clean_doc_content(self) -> NaiveDecisionParserDocument:
		"""
		From the clean text representation of the .txt file,
		parse the document into its structured version following the levels logic, where:
			- \t{1}Roman numeral....X... is a heading
			- \t{2}Uppercase letters....X... is a subheading
			- \t{3}Number....X... is a subsubheading
			- \t{4}(Lower case letter)...X... is a subsubsubheading
			- \t{5} ? is a subsubsubsubheading
			- \t{6}Number....X...Ending character is a paragraph
			- \t{7}(Lower case letter)...X...Ending character is a subparagraph
			- \t{8}(Lower case roman numeral)...X...Ending character is a subsubparagraph
		
		The left indentation level is needed to differentiate in confusing cases,
		 for example when in a subparagraph the lower case letters numbering and in a subsubparagraph
		 the lower case roman numerals can be confused:
		Subparagraph => (h) ...
		Subsubparagraph => (i) ...

		:return: Structured document content following the designed structure
		"""

		structured_doc_content: NaiveDecisionParserDocument = []
		prev_text: NaiveDecisionParserText | None = None
		for line in self.clean_doc_content:
			text_level: NaiveDecisionParserTextLevel = NaiveDecisionParserTextLevel(
				self.get_text_level(line=line)
			)
			clean_text: str = line.strip()
			match = re.match(
				rf"^(?:{self.get_numbering_pattern_from_text_level(level=text_level)})(.*)$",
				clean_text
			)

			if match is not None:
				current_text: NaiveDecisionParserText = NaiveDecisionParserText(
					level=text_level,
					parent=self._get_parent_text(prev_text=prev_text, text_level=text_level),
					numbering=match.group(1),
					text=match.group(2)
				)

				# Assign as a root of the doc content or as the child of the parent text
				if current_text.parent is None:
					structured_doc_content.append(current_text)
				else:
					current_text.parent.children.append(current_text)
				prev_text = current_text
			else:
				raise RuntimeError(
					f"Failed to match line: {line}. Expected pattern: {
						self.get_numbering_pattern_from_text_level(level=text_level)
					}"
				)	
		
		return structured_doc_content
	