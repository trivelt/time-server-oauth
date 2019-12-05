import asyncio


async def wait_for(event, timeout):
    try:
        await asyncio.wait_for(event.wait(), timeout)
    except asyncio.TimeoutError:
        pass
    return event.is_set()
