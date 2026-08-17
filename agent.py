import asyncio
import os

import cognee
from cognee import SearchType
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

COGNEE_API_KEY = os.environ["COGNEE_API_KEY"]
COGNEE_URL = os.environ["COGNEE_URL"]
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
MODEL = "gpt-4o-mini"

DATASET_NAME = "sales-support"


async def _connect_cloud():
    await cognee.serve(url=COGNEE_URL, api_key=COGNEE_API_KEY)


def _extract_text(results) -> str:
    """cognee returns a list of per-dataset result dicts; pull the actual
    text out instead of stringifying the whole structure."""
    parts = []
    for r in results or []:
        if isinstance(r, dict) and "search_result" in r:
            parts.extend(str(x) for x in r["search_result"])
        else:
            parts.append(str(r))
    return "\n".join(p for p in parts if p.strip())


async def _cognee_context(query: str, session_id: str) -> str:
    await _connect_cloud()
    try:
        results = await cognee.search(
            query_text=query,
            query_type=SearchType.GRAPH_COMPLETION,
            datasets=[DATASET_NAME],
            session_id=session_id,
            only_context=True,
        )
    except Exception:
        return ""
    return _extract_text(results)


def run_agent(user_message: str, session_id: str) -> str:
    context = asyncio.run(_cognee_context(user_message, session_id))

    if not context:
        return "I don't have that information in memory."

    response = client.chat.completions.create(
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
    await _connect_cloud()
    await cognee.add(text, dataset_name=DATASET_NAME)
    await cognee.cognify(datasets=[DATASET_NAME])


def remember(text: str) -> None:
    asyncio.run(_cognee_remember(text))


async def _cognee_ingest(file_obj, on_progress=None) -> None:
    await _connect_cloud()

    if on_progress:
        on_progress(20, "Uploading document to memory...")
    await cognee.add([file_obj], dataset_name=DATASET_NAME)

    if on_progress:
        on_progress(55, "Building knowledge graph (this can take a minute)...")
    await cognee.cognify(datasets=[DATASET_NAME])

    if on_progress:
        on_progress(100, "Done.")


def ingest_file(file_obj, on_progress=None) -> None:
    asyncio.run(_cognee_ingest(file_obj, on_progress))