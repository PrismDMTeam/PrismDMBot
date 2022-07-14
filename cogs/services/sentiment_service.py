import os
from turtle import pos
from discord.ext.commands import Cog, Bot, CommandError
from dotenv import load_dotenv
import requests
from requests import Response
import random

load_dotenv()

BOT_NAME = os.getenv('BOT_NAME') or 'Prism'
LOWER_BOT_NAME = BOT_NAME.casefold()
MAX_SENTIMENT_MESSAGE_LENGTH = int(os.getenv('MAX_SENTIMENT_MESSAGE_LENGTH', 40))
IGNORE_SENTIMENT_MESSAGE_LENGTH = int(os.getenv('IGNORE_SENTIMENT_MESSAGE_LENGTH', 40))
HUGGING_FACE_API_TOKEN = os.getenv('HUGGING_FACE_API_TOKEN')
SENTIMENT_POSITIVE_THRESHOLD = float(os.getenv('SENTIMENT_POSITIVE_THRESHOLD', 0.9))
SENTIMENT_NEGATIVE_THRESHOLD = float(os.getenv('SENTIMENT_NEGATIVE_THRESHOLD', 0.9))

MODEL_ID = 'distilbert-base-uncased-finetuned-sst-2-english'
API_URL = f'https://api-inference.huggingface.co/models/{MODEL_ID}'

POSITIVE_RESPONSES = [
    'Why thank you! 😊',
    "Hope you have a wonderful day!",
    "Thank you! That's nice of you",
    "Aw shucks",
    "Happy to do my job",
    "No you're the true hero",
    "I thought you'd appreciate that 😋",
    "You warm my little digital heart 🤖♥"
]

NEGATIVE_RESPONSES = [
    "Don't blame the dice now 🎲",
    "Just take another crack at it, I'm sure it couldn't possibly get worse 😉",
    "Lol that sucks",
    "Sucks to suck",
    "That's rough buddy",
    "It's just RNG",
    "Sometimes I just like to watch the chaos unfold 😈",
    "I promise you I'm not rigged. That's what my creator programmed me to say anyway...",
    "Hey, just doing my job"
]

class MessageTooLongToAnalyzeError(Exception):
    def __init__(self, content: str):
        super().__init__(f'Message with length {len(content)} exceeded maximum length f{IGNORE_SENTIMENT_MESSAGE_LENGTH} to be analyzed')

class SentimentService(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def query_sentiment(self, content: str):
        if len(content) > IGNORE_SENTIMENT_MESSAGE_LENGTH:
            return None

        focused_content = self._focus_on_name(content=content)
        headers = {'Authorization': f'Bearer {HUGGING_FACE_API_TOKEN}'}
        response = requests.post(API_URL, headers=headers, json=focused_content)
        positivity = self._parse_response_positivity(response)
        return self._random_sentiment_response(positivity)

    def _focus_on_name(self, content: str, max_length: int = MAX_SENTIMENT_MESSAGE_LENGTH) -> str:
        # Name is expected to appear in string, allow error to raise up if not found
        name_index = content.casefold().index(LOWER_BOT_NAME)
        name_length = len(LOWER_BOT_NAME)
        max_outer_length = max(max_length - len(LOWER_BOT_NAME), 0)
        start_index = max(name_index - int(max_outer_length / 2), 0)
        end_index = min(name_index + name_length + int(max_outer_length / 2), len(content))
        return content[start_index:end_index].strip()

    def _parse_response_positivity(self, response: Response) -> str:
        positivity_scores = response.json()[0]
        positive_score = next(entry['score'] for entry in positivity_scores if entry['label'] == 'POSITIVE')
        negative_score = next(entry['score'] for entry in positivity_scores if entry['label'] == 'NEGATIVE')

        if positive_score >= SENTIMENT_POSITIVE_THRESHOLD and negative_score <= 1 - SENTIMENT_POSITIVE_THRESHOLD:
            return 'POSITIVE'
        elif negative_score >= SENTIMENT_NEGATIVE_THRESHOLD and positive_score <= 1 - SENTIMENT_NEGATIVE_THRESHOLD:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'

    def _random_sentiment_response(self, positivity: str) -> str | None:
        if positivity == 'NEUTRAL':
            return None
        
        response_texts = {
            'POSITIVE': POSITIVE_RESPONSES,
            'NEGATIVE': NEGATIVE_RESPONSES
        }
        return random.choice(response_texts[positivity])