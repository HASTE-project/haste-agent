import asyncio
import time
import os
import shutil
import logging
import haste.desktop_agent.config
import sys

# num_preproc_core, source_dir, enable_prio_by_splines
CONFIGS = [
    (0, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_NATURAL),

    (1, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_SPLINES),
    (1, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_NATURAL),
    (1, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_GOLDEN),

    (2, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_SPLINES),
    (2, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_NATURAL),
    (2, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_GOLDEN),

    # Don't use more than 3 threads, there are only 2 cores.
    # (3, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_SPLINES),
    # (3, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_NATURAL),
    # (3, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', haste.desktop_agent.config.MODE_GOLDEN),

    (0, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/ffill/', haste.desktop_agent.config.MODE_NATURAL),
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

            num_threads, source_dir, mode = c

            proc_simulator = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'haste.desktop_agent.simulator', source_dir)

            await asyncio.sleep(5)

            cmd = [sys.executable,
                   '-m', 'haste.desktop_agent',
                   '--include', haste.desktop_agent.config.EXTENSION,
                   '--tag', 'trash',
                   '--host', 'haste-gateway.benblamey.com:80',
                   '--username', 'haste',
                   '--password', 'mr_frumbles_bad_day',
                   haste.desktop_agent.config.TARGET_DIR,
                   '--x-preprocessing-cores', str(num_threads),
                   '--x-mode', str(mode)]
            # if not c[2]:
            #     cmd.append("--x-disable-prioritization")

            logging.info(cmd)
            proc_agent = await asyncio.create_subprocess_exec(*cmd)

            await proc_simulator.wait()
            await proc_agent.wait()

            logging.info(f'Finished Benchmarking Run {i}.{j}')

            await asyncio.sleep(3)

        await asyncio.sleep(10)



if __name__ == '__main__':
    asyncio.run(main())
