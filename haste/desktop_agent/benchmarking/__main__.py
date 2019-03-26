import asyncio
import time
import os
import shutil
import logging
import haste.desktop_agent.config
import sys

# num_preproc_core, source_dir, enable_prio_by_splines
CONFIGS = [
    (0, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', False),

    (1, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', True),
    (2, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', True),
    (3, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', True),

    (1, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', False),
    (2, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', False),
    (3, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/greyscale/', False),

    (0, '/Users/benblamey/projects/haste/images/2019_02_04__11_34_55_vironova/all/gen/ffill/', False),
]


async def main():
    LOGGING_FORMAT_DATE = '%Y-%m-%d %H:%M:%S.%d3'
    LOGGING_FORMAT = '%(asctime)s - BENCHMARKING - %(threadName)s - %(levelname)s - %(message)s'

    logging.basicConfig(level=logging.INFO,
                        format=LOGGING_FORMAT,
                        datefmt=LOGGING_FORMAT_DATE)

    for i in range(5):

        for j, c in enumerate(CONFIGS):
            logging.info(f'Starting Benchamrking Run {i}.{j}')

            proc_simulator = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'haste.desktop_agent.simulator', c[1])

            await asyncio.sleep(5)

            cmd = [sys.executable,
                   '-m', 'haste.desktop_agent',
                   '--include', haste.desktop_agent.config.EXTENSION,
                   '--tag', 'trash',
                   '--host', 'haste-gateway.benblamey.com:80',
                   '--username', 'haste',
                   '--password', 'mr_frumbles_bad_day',
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


if __name__ == '__main__':
    asyncio.run(main())
