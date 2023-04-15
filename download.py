from typing import Optional
import os, shutil
import socket
import requests
from tqdm import tqdm

from thread import Thread

def download(url: str, start: int, end: int, cont: bool,
             session: requests.Session, pbar: tqdm, tmpdir: str) -> bool:
    if cont and os.path.exists(os.path.join(tmpdir, f"{start}.part")):
        done_size = os.path.getsize(os.path.join(tmpdir, f"{start}.part"))
        pbar.update(done_size)
        down_start = start + done_size
        if down_start == end:
            return True
        if down_start > end:
            pbar.write(f"{url}: continue download failed, {start} + {done_size} >= {end}")
            return False
    else:
        down_start = start
    header = {"Range": f"bytes={down_start}-{end-1}"}
    try:
        ret = session.get(url, stream=True, headers=header)
        with open(os.path.join(tmpdir, f"{start}.part"), "ab" if cont else "wb") as f:
            for chunk in ret.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
                else:
                    pbar.write(f"{url}: {start}-{end} download failed")
                    return False
    except Exception as e:
        pbar.write(e)
        return False
    return True

def download_multithreading(url: str, session: requests.Session,
                            start: int = 0, end: Optional[int] = None, cont: bool = False,
                            save_name: Optional[str] = None, num_threads: int = 4,
                            tmpdir: str = ".tmp") -> Optional[str]:
    try:
        num_threads = int(num_threads)
        if num_threads < 1:
            raise ValueError("number of threads must be greater than 0")

        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        elif not os.path.isdir(tmpdir):
            raise ValueError(f"{tmpdir} is not a directory")

        ret = session.get(url, stream=True)
        file_size = int(ret.headers["Content-Length"])
        if save_name is None:
            save_name = url.split("/")[-1]
        if end is None:
            end = file_size
        local_size = end - start
        if local_size < 0:
            raise ValueError("start must be less than end")

        pbar = tqdm(total=local_size, unit="B", unit_scale=True)
        threads = []
        for i in range(num_threads):
            nowstart = local_size // num_threads * i
            nowend = local_size // num_threads * (i + 1) if i != num_threads - 1 else local_size
            nowstart += start
            nowend += start
            t = Thread(target=download, args=(url, nowstart, nowend, cont, session, pbar, tmpdir))
            t.setDaemon(True)
            threads.append((t, nowstart, nowend))

        for i in range(num_threads):
            threads[i][0].start()
        for i in range(num_threads):
            threads[i][0].join()
        for i in range(num_threads):
            if not threads[i][0].get_result():
                pbar.write(f"{url} download failed")
                pbar.close()
                return None

        with open(save_name, "wb") as f:
            if num_threads != 1:
                for i in range(num_threads):
                    with open(os.path.join(tmpdir, f"{threads[i][1]}.part"), "rb") as f1:
                        f.write(f1.read())
                    os.remove(os.path.join(tmpdir, f"{threads[i][1]}.part"))
            else:
                os.rename(os.path.join(tmpdir, f"{start}.part"), save_name)

        pbar.close()
        shutil.rmtree(tmpdir)
        return save_name
    except:
        pbar.close()
        return None

BUFFERSIZE = 1024

def handle_client(client_socket, client_address, save_name, now_range, index):
    start, end = now_range
    try:
        client_socket.send(f"{start} {end} {index}".encode("utf-8"))
        with open(f"{save_name}.part{index}", "wb") as f:
            while True:
                # TODO: add tqdm here
                data = client_socket.recv(BUFFERSIZE)
                if not data:
                    break
                f.write(data)
        client_socket.close()
    except:
        client_socket.close()
        print(f"\n{client_address} download failed")

def client(client_socket, url: str, session: requests.Session,
           num_threads: int, save_name: str):
    try:
        now_range = client_socket.recv(BUFFERSIZE).decode("utf-8").split(" ")
        start = int(now_range[0])
        end = int(now_range[1])
        index = int(now_range[2])
        download_multithreading(url, session, start, end, True, save_name=f"{save_name}.part{index}",
                                num_threads=num_threads, tmpdir=f".{save_name}.part{index}_tmp")
        with open(f"{save_name}.part{index}", "rb") as f:
            client_socket.sendall(f.read())
        client_socket.close()
        os.remove(f"{save_name}.part{index}")
    except:
        client_socket.close()

def download_dist(url: str, session: requests.Session, is_server: bool, num_clients: Optional[int] = None,
                  save_name: Optional[str] = None, server_ip: str = "127.0.0.1",
                  port: int = 9999, num_threads: int = 4, server_download: bool = True):
    if save_name is None:
        save_name = url.split("/")[-1]
    if is_server:
        if num_clients is None:
            raise ValueError("num_clients must be specified when is_server is True")
        if server_download:
            num_clients += 1
        ret = session.get(url, stream=True)
        url_size = int(ret.headers["Content-Length"])
        ranges = []
        clientsT = []
        for i in range(num_clients):
            ranges.append((url_size // num_clients * i,
                        url_size // num_clients * (i + 1) if i != num_clients - 1 else url_size))
        if server_download:
            num_clients -= 1
            downloadT = Thread(target=download_multithreading,
                               args=(url, session, ranges[-1][0], ranges[-1][1],
                                     True, f"{save_name}.part{num_clients}", num_threads,
                                     f".{save_name}.part{num_clients}_tmp"))
            downloadT.setDaemon(True)
            downloadT.start()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(num_clients)

        for i in range(num_clients):
            client_socket, client_address = server_socket.accept()
            print(f"\nclient {i}:{client_address} connected")
            t = Thread(target=handle_client, args=(client_socket, client_address, save_name, ranges[i], i))
            clientsT.append(t)
        for t in clientsT:
            t.start()
        for t in clientsT:
            t.join()

        server_socket.close()
        if server_download:
            downloadT.join()
            num_clients += 1
        with open(save_name, "wb") as f:
            for i in range(num_clients):
                with open(f"{save_name}.part{i}", "rb") as f1:
                    f.write(f1.read())
                os.remove(f"{save_name}.part{i}")
    else:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, port))
        client(client_socket, url, session, num_threads, save_name)
        client_socket.close()
