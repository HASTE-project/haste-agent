import asyncio


async def foo(value):
    print(value)


asyncio.run(foo('bar'))
