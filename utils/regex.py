# File with all the regex expressions used on this project
import re

INTERVENTION_REGEX: re.Pattern = re.compile(r'(?P<name>.+) {2}(?P<timestamp>\b\d{1,2}:\d{1,2}:\d{1,2}\b|\b\d{1,2}:\d{1,2}\b)')

# If the Item has topics
BULLET_REGEX_TOPIC: re.Pattern = re.compile(r'\|\s*(?P<bullet_point>.*?)\s*\|\s*(?P<reference>.*?)\s*\|\s*(?P<topic>.*?)\s*\|')
# If the Item has no topics
BULLET_REGEX_NO_TOPIC: re.Pattern = re.compile(r'\|\s*(?P<bullet_point>.*?)\s*\|\s*(?P<reference>.*?)\s*\|')
