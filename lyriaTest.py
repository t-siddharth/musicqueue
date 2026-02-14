import asyncio
import os
import warnings
import numpy as np
import sounddevice as sd
from google import genai
from google.genai import types

warnings.filterwarnings('ignore', message='.*experimental.*', module='google.genai')

client = genai.Client(
    api_key=os.environ.get('GOOGLE_API_KEY'),
    http_options={'api_version': 'v1alpha'}
)

async def main():
    stream = sd.OutputStream(samplerate=48000, channels=1, dtype='int16')
    stream.start()

    async def receive_audio(session):
        """Background task to process incoming audio chunks."""
        while True:
            async for message in session.receive():
                if message.server_content.audio_chunks:
                    for chunk in message.server_content.audio_chunks:
                        audio_array = np.frombuffer(chunk.data, dtype=np.int16)
                        stream.write(audio_array)
            await asyncio.sleep(10**-12)

    async with (
        client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
        asyncio.TaskGroup() as tg,
    ):
        # 1. Start listening for audio
        tg.create_task(receive_audio(session))

        # 2. Send initial musical concept
        await session.set_weighted_prompts(
            prompts=[types.WeightedPrompt(text='elevator music', weight=1.0)]
        )

        # 3. Set the vibe (BPM, Temperature)
        await session.set_music_generation_config(
            config=types.LiveMusicGenerationConfig(bpm=90, temperature=1.0)
        )

        # 4. Drop the beat
        await session.play()

        # Keep the session alive
        await asyncio.sleep(30)

    stream.stop()
    stream.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPlayback stopped.")
