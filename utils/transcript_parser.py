import os
from itertools import islice
from utils.exceptions import (IncorrectFileExtensionError, FileNotFoundInError)
from warnings import warn
from utils.regex import INTERVENTION_REGEX
import re


class TranscriptParser:
	"""
	Class that parses a transcript into a different paragraphs.
	:param input_file: Name of the .txt file
	:param input_folder: Name of the full path to input folder containing .txt files
	"""

	def __init__(
			self, input_file: str | None, folder_name: str | None,
			input_folder: str = os.path.join(".", "data", "input"), raw_file: str = None):
		"""
		:Attributes:
		Initialization
			- file_name: Name of the .txt file
			- input_folder: Folder where the input file is located
			. mappings_folder: Folder with mappings between aliases, participants and parties
			- meeting_id: The meeting associated to the transcript
			- file_path: Full path to the .txt file
			- transcript: Transcript object from the db
		"""
		if raw_file is None:
			if not input_file.endswith(".txt"):
				raise IncorrectFileExtensionError(f"The file {input_file} is not a .txt extension")
			self.file_name: str = input_file

			self.input_folder: str = input_folder
			self.file_path: str = os.path.join(self.input_folder, folder_name, self.file_name)

			if not os.path.isfile(self.file_path):
				raise FileNotFoundInError(f"The file {input_file} not found in {self.file_path}")

			self._read_txt()
		else:
			self.raw_transcript: str = raw_file

	def _read_txt(self):
		"""
		Reads the .txt into a python string (str)
		And it removes the last line that is the watermark "Transcribed by https://otter.ai"
		"""
		with open(self.file_path, "r", encoding="utf-8") as f:
			self.raw_transcript: list[str] = f.readlines()
		if self.raw_transcript[-1] == "Transcribed by https://otter.ai\n":
			self.raw_transcript: str = "".join(self.raw_transcript[:-1])
		else:
			warn(f"Watermark from otter not found, instead found: {self.raw_transcript[-1]}")
			self.raw_transcript: str = "".join(self.raw_transcript)

	@staticmethod
	def _group_interventions(lst: list, size: int = 3) -> list:
		"""
		Given a list of interventions from a transcript
		Groups the chunk of interventions in:
			- Name
			- Hour
			- Intervention text
		"""
		it = iter(lst)
		return list(iter(lambda: list(islice(it, size)), []))

	def _parse_transcript(self):
		"""
		Parses the transcript into the different paragraphs
		and stores them in a list of Paragraph objects
		"""
		# Split the text in interventions
		interventions: list[str] = re.split(INTERVENTION_REGEX, self.raw_transcript)[1:]
		interventions_list: list = self._group_interventions(interventions)
		self.paragraphs = []
		for oid, intervention in enumerate(interventions_list):
			self._add_paragraph(oid, intervention)

	def _add_paragraph(self, oid: int, intervention: list[str]) -> None:
		"""
		Adds a paragraph to the paragraph list extracting the party name too
		:param intervention: List with Name, Hour and Paragraph
		"""
		paragraph = {"oid": oid, "participant": intervention[0],
					"hour": intervention[1], "paragraph": intervention[2]}
		self.paragraphs.append(paragraph)

	def __call__(self):
		self._parse_transcript()
		return self.paragraphs
