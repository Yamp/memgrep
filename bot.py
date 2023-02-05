import logging
import re
import time

import pymorphy2
import telethon
from pymystem3 import Mystem
from setuptools.namespaces import flatten
from telethon import TelegramClient, events

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = ""
api_hash = ""
receiver_name = ""
session_name = ""

receiver = None

client = TelegramClient(session=session_name, api_id=api_id, api_hash=api_hash)

search_words = []

#read words from file for ez managing words by Marina herself
with open('words.txt', 'r') as file:
    content = file.readlines()
    for line in content:
        line = line.replace('\n', '')
        search_words.append(line)

class MessageFilter:
    """Класс, который фильтрует интересные нам сообщения."""

    def __init__(
            self,
            words: list[str],
    ):
        self.mystem = Mystem()
        self.morf = pymorphy2.MorphAnalyzer()
        self.original_words = [w.strip().lower() for w in words]
        self.words: set[str] = self.flex_all_words(self.original_words)

        self.tokenize_regex = re.compile(r"[\w']+|[.,!?;]")

    def is_interesting(self, text: str) -> str | None:
        """Проверяет, есть ли в тексте интересные слова."""
        text = text.lower()
        for w in self.original_words:
            if w.strip().lower() in text:
                return w

        old_text = self.lemmatize_text(text)
        text = set(self.tokenize(text))
        for w in self.words:
            if w in text:
                logging.info("Found word: %s %s %s", w, text, old_text)
                return w

        return None

    def lemmatize_text(
            self,
            text: str,
    ) -> str:
        """Лемматизирует текст."""
        lemmas = self.mystem.lemmatize(text)
        l1 = " ".join(lemmas)

        tokens = self.tokenize(text)
        l2 = " ".join([self.morf.parse(t)[0].normal_form for t in tokens])

        return " | ".join([text, l1, l2]).strip().lower()

    def tokenize(self, text: str) -> list[str]:
        """Токенизирует текст."""
        return [
            t for t in self.tokenize_regex.split(text.strip().lower())
            if t and not t.isspace()
        ]

    def flex_word(self, word: str) -> list[str]:
        """Собирает все формы слова."""
        return [word] + [l.word for l in self.morf.parse(word)[0].lexeme]

    def flex_all_words(self, tokens: list[str]) -> set[str]:
        """Флексит все слова в тексте."""
        return set(flatten(
            [
                self.flex_word(t.strip().lower())
                for t in tokens
                if t and t.isalpha() and "скуп" not in t
            ]
        ))


async def start():
    """Main processing function."""
    global receiver
    receiver = await client.get_entity(receiver_name)
    await client.send_message(receiver, 'Бот запущен!')


@client.on(
    events.NewMessage(
        # chats=True,
        # incoming=True,
    )
)
async def handler(event: telethon.events.NewMessage.Event):
    """Обрабатываем сообщение."""
    msg = event.message

    try:
        name = f'{msg.sender.first_name} {msg.sender.last_name} ({msg.sender.id})'
    except:
        name = f'{msg.sender_id}'

    try:
        chat = f'{msg.chat.title} ({msg.chat.id})'
    except:
        chat = f'{msg.chat_id}'

    try:
        ts = msg.date.strftime("%Y-%m-%d %H:%M:%S")
    except:
        ts = ''

    try:
        url = f'https://t.me/c/{msg.chat.id}/{msg.id}'
    except:
        url = ''

    notif = f"Получено сообщение от {name}, {chat}, {ts}"

    if w := m_filter.is_interesting(msg.text):
        notif += f", найдено слово {w}"
        print(notif)
        await client.send_message(receiver, notif)

        if url:
            await client.send_message(receiver, url)
        else:
            await msg.forward_to(receiver_name)


with client:
    m_filter = MessageFilter(search_words)

    client.loop.run_until_complete(start())
    client.run_until_disconnected()

