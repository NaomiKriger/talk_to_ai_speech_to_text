import asyncio
import os
import sys
import time
from threading import Thread

import openai
import pyttsx3
from openai import ChatCompletion

from src.commons import get_system_instructions, Gender


def draw_loading_response():
    word = "Loading response..."
    for i in range(len(word)):
        sys.stdout.write("\r" + word[:i + 1] + " " * (len(word) - i - 1))
        sys.stdout.flush()
        time.sleep(0.2)
    print()


async def get_transcript(audio_file_path: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    audio_file = open(audio_file_path, "rb")
    transcript = None

    async def transcribe_audio():
        nonlocal transcript
        try:
            response = openai.Audio.transcribe(model="whisper-1", file=audio_file, language="en")
            transcript = response.get("text")
        except Exception as e:
            print(e)

    draw_thread = Thread(target=draw_loading_response)
    draw_thread.start()

    transcription_task = asyncio.create_task(transcribe_audio())
    await transcription_task

    if transcript is None:
        print("Transcription not available within the specified timeout.")

    print(f"\n{transcript}")
    return transcript


def get_gpt_response(transcript: str, chosen_figure: str) -> str:
    system_instructions = get_system_instructions(chosen_figure)
    try:
        return make_openai_request(
            system_instructions=system_instructions, user_question=transcript).choices[0].message["content"]
    except Exception as e:
        return e.args[0]


def make_openai_request(system_instructions: str, user_question: str) -> ChatCompletion:
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_question}
        ],
        max_tokens=50
    )

    return completion


def text_to_speech(text: str, gender: str = Gender.female.value):
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Set properties (optional)
    engine.setProperty("rate", 180)  # Speed of speech (words per minute)
    voices = engine.getProperty('voices')
    voice_id = voices[0].id if gender == "male" else voices[1].id
    engine.setProperty("voice", voice_id)

    # Play the text as speech
    engine.say(text)
    engine.runAndWait()


def list_voices():
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Get a list of available voices
    voices = engine.getProperty('voices')

    # Print the available voices and their properties
    for idx, voice in enumerate(voices):
        print(f"Voice {idx + 1}:")
        print(f" - ID: {voice.id}")
        print(f" - Name: {voice.name}")
        print(f" - Languages: {voice.languages}")
        print(f" - Gender: {voice.gender}")
        print(f" - Age: {voice.age}")
        print()
