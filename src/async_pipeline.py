import asyncio
import re


async def sentence_chunker(stream, queue):

    buffer = ""

    async for token in stream:

        buffer += token

        if re.search(r"[.!?]\s$", buffer):

            sentence = buffer.strip()

            await queue.put(sentence)

            buffer = ""

    if buffer:
        await queue.put(buffer)