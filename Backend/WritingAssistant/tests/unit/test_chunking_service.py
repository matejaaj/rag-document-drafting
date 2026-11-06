from app.services.rag.chunking_service import ChunkingService

MODEL_LIMIT_TOKENS = 40
CHARS_PER_TOKEN = 4


def test_long_text_is_split_into_overlapping_chunks_within_the_model_limit():
    words = [f"rec{number:03}" for number in range(100)]
    chunking = ChunkingService(
        max_model_tokens=MODEL_LIMIT_TOKENS, target_tokens=100, overlap_tokens=10, avg_chars_per_token=CHARS_PER_TOKEN
    )

    chunks = chunking.make_chunks(" ".join(words))

    assert len(chunks) > 1
    assert all(len(text) <= MODEL_LIMIT_TOKENS * CHARS_PER_TOKEN for text in chunks)
    assert all(any(word in text for text in chunks) for word in words)
    assert all(chunks[index][-8:] in chunks[index + 1] for index in range(len(chunks) - 1))
