import asyncio
import time
import os
import shutil
import logging
import haste.desktop_agent.config
import sys
import benchmarking_config

# num_preproc_core, source_dir, enable_prio_by_splines
CONFIGS = [
    (0, benchmarking_config.GREYSCALE_DIR, False),

    (1, benchmarking_config.GREYSCALE_DIR, True),
    (2, benchmarking_config.GREYSCALE_DIR, True),
    (3, benchmarking_config.GREYSCALE_DIR, True),

    (1, benchmarking_config.GREYSCALE_DIR, False),
    (2, benchmarking_config.GREYSCALE_DIR, False),
    (3, benchmarking_config.GREYSCALE_DIR, False),

    (0, benchmarking_config.FFILL_DIR, False),
]


async def main():
    LOGGING_FORMAT_DATE = '%Y-%m-%d %H:%M:%S.%d3'
    LOGGING_FORMAT = '%(asctime)s - BENCHMARKING - %(threadName)s - %(levelname)s - %(message)s'

    logging.basicConfig(level=logging.INFO,
                        format=LOGGING_FORMAT,
                        datefmt=LOGGING_FORMAT_DATE)

    i = -1
    # while time.time() < 1553760000:  # 03/28/2019 @ 8:00am (UTC)
    while True:
        i += 1
        for j, c in enumerate(CONFIGS):
            logging.info(f'Starting Benchmarking Run {i}.{j}')

            proc_simulator = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'haste.desktop_agent.simulator', c[1])

            await asyncio.sleep(5)

            cmd = [sys.executable,
                   '-m', 'haste.desktop_agent',
                   '--include', haste.desktop_agent.config.EXTENSION,
                   '--tag', 'tag',
                   '--host', 'haste-gateway.benblamey.com:80',
                   '--username', '??????',
                   '--password', '??????',
                   haste.desktop_agent.config.TARGET_DIR,
                   '--x-preprocessing-cores', str(c[0])]
            if not c[2]:
                cmd.append("--x-disable-prioritization")

            logging.info(cmd)
            proc_agent = await asyncio.create_subprocess_exec(*cmd)

            await proc_simulator.wait()
            await proc_agent.wait()

            logging.info(f'Finished Benchmarking Run {i}.{j}')

            await asyncio.sleep(3)

        await asyncio.sleep(10)



if __name__ == '__main__':
    asyncio.run(main())
