import asyncio


async def main(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE)

    i = 0
    while True:
        i += 1
        stdoutline = await proc.stdout.readline()
        print(stdoutline.decode())

        # add to the buffer
        proc.stdin.write(f'{i}\n'.encode())
        await proc.stdin.drain()

    # stdout, stderr = await proc.communicate()
    #
    # print(f'[{cmd!r} exited with {proc.returncode}]')
    # if stdout:
    #     print(f'[stdout]\n{stdout.decode()}')
    # if stderr:
    #     print(f'[stderr]\n{stderr.decode()}')


asyncio.run(main('python3 -m haste.desktop_agent.play-asyncio-client'))
