# Написать программу, которая скачивает изображения с заданных URL-адресов и сохраняет их на диск.
# Каждое изображение должно сохраняться в отдельном файле, название которого соответствует названию изображения в URL-адресе.
# Например, URL-адрес: https://example/images/image1.jpg -> файл на диске: image1.jpg
# — Программа должна использовать многопоточный, многопроцессорный и асинхронный подходы.
# — Программа должна иметь возможность задавать список URL-адресов через аргументы командной строки.
# — Программа должна выводить в консоль информацию о времени скачивания каждого изображения и общем времени выполнения программы.


import time
import requests
import threading
from multiprocessing import Process
from urllib.parse import urlparse
import os
from sys import argv
import asyncio
import aiohttp
import httpx


def get_image(url):
    start = time.perf_counter()
    img_data = requests.get(url).content
    filename = os.path.basename(urlparse(url).path)
    with open(filename, 'wb') as f:
        f.write(img_data)
        print(f'Время выполнения: {time.perf_counter() - start}.')


async def download_files(url: str):
    start = time.perf_counter()
    filename = os.path.basename(urlparse(url).path)
    with open(filename, 'wb') as f:
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', url) as r:
                r.raise_for_status()
                async for img in r.aiter_bytes():
                    f.write(img)
                print(f'Время выполнения: {time.perf_counter() - start}.')


async def main(urls):
    loop = asyncio.get_running_loop()
    tasks = [loop.create_task(download_files(url)) for url in urls]
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    urls = ['https://i.imgur.com/ycPp6on.jpeg',
    'https://i.imgur.com/UkgrtOf.jpeg',
    'https://i.imgur.com/S7tCJwu.png',
    'https://i.imgur.com/kaDG46g.jpeg',
    'https://i.imgur.com/XOyxsrX.jpeg',
    'https://i.imgur.com/HNxiNiZ.jpeg',
    'https://i.imgur.com/vdVviPZ.jpeg',
    'https://i.imgur.com/ml0X70b.jpeg',
    'https://i.imgur.com/8cQGxFf.jpeg',
    'https://i.imgur.com/B4W0pDk.jpeg',
    'https://i.imgur.com/Gp2gKOC.jpeg']

    if len(argv) > 1:
        urls = []
        for i in range(1, len(argv)):
            urls.append(argv[i])

    # Синхронный подход

    print('\nСтарт синхронного подхода.')

    start = time.perf_counter()

    for url in urls:
        get_image(url)

    sync = time.perf_counter() - start

    print(f'Синхронный подход: {sync}.')

    # Многопоточный подход

    print('\nСтарт многопоточного подхода.')

    start = time.perf_counter()

    threads = []

    for url in urls:
        thread = threading.Thread(target=get_image, args=[url])
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    thread = time.perf_counter() - start

    print(f'Многопоточный подход: {thread}.')

    # Многопроцессорный подход

    print('\nСтарт многопроцессорного подхода.')

    start = time.perf_counter()

    processes = []

    for url in urls:
        process = Process(target=get_image, args=[url])
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    process = time.perf_counter() - start

    print(f'Многопроцессорный подход: {process}.')

    # Асинхронный подход

    print('\nСтарт асинхронного подхода.')

    start = time.perf_counter()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(urls))

    async_ = time.perf_counter() - start

    print(f'Асинхронный подход: {async_}.')

    # Общие результаты

    print(f'\nСинхронный подход: {sync}.\n'
          f'Многопоточный подход: {thread}.\n'
          f'Многопроцессорный подход: {process}.\n'
          f'Асинхронный подход: {async_}.\n')