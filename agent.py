from dotenv import load_dotenv
load_dotenv()

import asyncio
import os

from cogwit_sdk import cogwit, CogwitConfig
from openai import OpenAI

COGNEE_API_KEY = os.environ["COGNEE_API_KEY"]
client = cogwit(CogwitConfig(api_key=COGNEE_API_KEY))
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = "gpt-4o-mini"

DATASET_NAME = "sales-support"


def _is_error(result) -> bool:
    return type(result).__name__.endswith("Error")


def _extract_text(results) -> str:
    parts = []
    for r in results or []:
        text = getattr(r, "text", None) or getattr(r, "content", None) or str(r)
        parts.append(text)
    return "\n".join(p for p in parts if p and p.strip())


async def _cognee_context(query: str) -> str:
    results = await client.search(
        query_text=query,
        query_type=client.SearchType.CHUNKS,
    )
    if _is_error(results):
        return ""
    return _extract_text(results)


def _rewrite_query(user_message: str, conversation: list) -> str:
    """Use recent turns to make a standalone, fully-specified question --
    restores the effect of cross-turn continuity without needing it from
    the search backend itself."""
    if not conversation:
        return user_message

    recent = conversation[-6:]  # last few turns is plenty of context
    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in recent)

    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Given the recent conversation and a new question, rewrite the "
                    "new question so it's fully self-contained and makes sense on "
                    "its own, with no pronouns or implicit references to earlier "
                    "messages. If it's already self-contained, return it unchanged. "
                    "Return ONLY the rewritten question, nothing else."
                ),
            },
            {
                "role": "user",
                "content": f"RECENT CONVERSATION:\n{history_text}\n\nNEW QUESTION:\n{user_message}",
            },
        ],
    )
    return response.choices[0].message.content.strip()


def run_agent(user_message: str, conversation: list = None) -> str:
    search_query = _rewrite_query(user_message, conversation or [])
    context = asyncio.run(_cognee_context(search_query))

    if not context:
        return "I don't have that information in memory."

    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer the question naturally and conversationally, as if you "
                    "simply know this. Never refer to 'the context' or mention that "
                    "you're reading from retrieved information -- just answer directly. "
                    "Do not add any detail, number, or specific that isn't explicitly "
                    "given below -- no inferred or plausible-sounding filler. If what's "
                    "given doesn't clearly answer the question, say plainly that you "
                    "don't have that information -- don't guess.\n\n"
                    f"KNOWN INFORMATION:\n{context}"
                ),
            },
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


async def _cognee_remember(text: str) -> None:
    result = await client.add(text, dataset_name=DATASET_NAME)
    if _is_error(result):
        raise RuntimeError(f"add failed: {result}")
    cognify_result = await client.cognify(datasets=[DATASET_NAME])
    if _is_error(cognify_result):
        raise RuntimeError(f"cognify failed: {cognify_result}")


def remember(text: str) -> None:
    asyncio.run(_cognee_remember(text))


async def _cognee_ingest(file_obj, on_progress=None) -> None:
    if on_progress:
        on_progress(20, "Uploading document to memory...")
    result = await client.add([file_obj], dataset_name=DATASET_NAME)
    if _is_error(result):
        raise RuntimeError(f"add failed: {result}")

    if on_progress:
        on_progress(55, "Building knowledge graph (this can take a minute)...")
    cognify_result = await client.cognify(datasets=[DATASET_NAME])
    if _is_error(cognify_result):
        raise RuntimeError(f"cognify failed: {cognify_result}")

    if on_progress:
        on_progress(100, "Done.")


def ingest_file(file_obj, on_progress=None) -> None:
    asyncio.run(_cognee_ingest(file_obj, on_progress))