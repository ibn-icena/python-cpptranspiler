async def fetch_data(url: str) -> str:
    # Simulate async operation
    result = await get_url(url)
    return result

async def process_data(data: str) -> int:
    value = await compute(data)
    return value + 10

async def main() -> int:
    data = await fetch_data("http://example.com")
    result = await process_data(data)
    return result
