import asyncio
import logging
import time

import aiohttp

from haste.desktop_agent.config import WAIT_AFTER_FIRST_MODIFIED_SECONDS


async def post_file(filename, stream_id_tag, stream_id, username, password, host):
    logging.info(f'Sending file: {filename}')

    auth = aiohttp.BasicAuth(login=username, password=password)

    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            extra_headers = {'X-HASTE-original_filename': filename,
                             'X-HASTE-tag': stream_id_tag,
                             'X-HASTE-unixtime': str(time.time())}

            async with session.post(f'http://{host}/stream/{stream_id}',
                                    data=open(filename, 'rb'),
                                    headers=extra_headers) as response:
                logging.info(f'HASTE Response: {response.status}')
                return await response.text()

        except Exception as ex:
            logging.error(f'Exception sending file:')
            logging.error(ex)


async def send_file(event, stream_id_tag, stream_id, username, password, host):
    logging.debug(f'handling event: {event}')

    # Wait for any subsequent modifications to the file.
    # TODO: instead, poll the last modified time incase the file is modified again

    # If the file was only just created, allow a 1 second for subsequent writes.
    # if event.timestamp + WAIT_AFTER_FIRST_MODIFIED_SECONDS > time.time():
    #     await asyncio.sleep(WAIT_AFTER_FIRST_MODIFIED_SECONDS)

    return await post_file(event.src_path, stream_id_tag, stream_id, username, password, host)
