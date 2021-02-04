import asyncio
import logging

import haste.desktop_agent.benchmarking.benchmarking_config as benchmarking_config
import haste.desktop_agent.config
import sys

# num_preproc_core, source_dir, enable_prio_by_splines
from haste.desktop_agent.benchmarking.benchmarking_config import HASTE_GATEWAY_PASSWORD, HASTE_GATEWAY_USERNAME, \
    HASTE_GATEWAY_HOST

CONFIGS = [
    (0, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_NATURAL),

    (1, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_SPLINES),
    # (1, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_GOLDEN),

    (2, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_SPLINES),
    # (3, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_SPLINES),

    (1, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_NATURAL),
    (2, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_NATURAL),
    # (2, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_GOLDEN),

    # Don't use more than 3 threads, there are only 2 cores.
    # (3, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_NATURAL),
    # (3, benchmarking_config.GREYSCALE_DIR, haste.desktop_agent.config.MODE_GOLDEN),

    #
    (0, benchmarking_config.FFILL_DIR, haste.desktop_agent.config.MODE_NATURAL),
]


async def main():
    LOGGING_FORMAT_DATE = '%Y-%m-%d %H:%M:%S.%d3'
    LOGGING_FORMAT = '%(asctime)s - BENCHMARKING - %(threadName)s - %(levelname)s - %(message)s'

    logging.basicConfig(level=logging.INFO,
                        format=LOGGING_FORMAT,
                        datefmt=LOGGING_FORMAT_DATE)

    run_index = -1
    # while time.time() < 1553760000:  # 03/28/2019 @ 8:00am (UTC)
    while True:
        run_index += 1
        for config_index, config in enumerate(CONFIGS):
            logging.info(f'Starting Benchmarking Run {run_index}.{config_index}')

            num_threads, source_dir, mode = config

            proc_simulator = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'haste.desktop_agent.simulator', source_dir)

            await asyncio.sleep(5)

            cmd = [sys.executable,
                   '-m', 'haste.desktop_agent',
                   '--include', haste.desktop_agent.benchmarking.benchmarking_config.EXTENSION,
                   '--tag', 'trash',
                   '--host', HASTE_GATEWAY_HOST,
                   '--username', HASTE_GATEWAY_USERNAME,
                   '--password', HASTE_GATEWAY_PASSWORD,
                   haste.desktop_agent.benchmarking.benchmarking_config.TARGET_DIR,
                   '--x-preprocessing-cores', str(num_threads),
                   '--x-mode', str(mode)]
            # if not c[2]:
            #     cmd.append("--x-disable-prioritization")

            logging.info(cmd)
            proc_agent = await asyncio.create_subprocess_exec(*cmd)

            await proc_simulator.wait()
            await proc_agent.wait()

            logging.info(f'Finished Benchmarking Run {run_index}.{config_index}')

            await asyncio.sleep(3)

        await asyncio.sleep(10)



if __name__ == '__main__':
    asyncio.run(main())
