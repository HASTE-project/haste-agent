import asyncio
import logging
import time


async def ffill_file(input_filepath):
    output_filepath = '/tmp/' + input_filepath.split('/')[-1]

    start = time.time()

    proc = await asyncio.create_subprocess_exec(
        'python3', '-m', 'haste.desktop_agent.preprocessor', input_filepath, output_filepath,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    # stdout, stderr = await proc.communicate()
    #
    # # print(f'[{cmd!r} exited with {proc.returncode}]')
    # if stdout:
    #     print(f'[stdout]\n{stdout.decode()}')
    # if stderr:
    #     print(f'[stderr]\n{stderr.decode()}')

    await proc.wait()

    logging.info(f'preprocessing took {time.time() - start} for {input_filepath}')

    return output_filepath

# asyncio.run(run('ls /zzz'))
