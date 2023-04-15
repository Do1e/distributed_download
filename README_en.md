# Distributed File Download

[简体中文](README.md) | English

## Function List

### download_multithreading

```python
def download_multithreading(url: str, session: requests.Session,
                            start: int = 0, end: Optional[int] = None, cont: bool = False,
                            save_name: Optional[str] = None, num_threads: int = 4,
                            tmpdir: str = ".tmp") -> Optional[str]:
```

Download a file using multiple threads.

- `url`: The URL of the file.
- `session`: A login session that has been constructed beforehand.
- `start`: Optional parameter that specifies the starting download position. The default value is 0.
- `end`: Optional parameter that specifies the ending download position. The default value is the length of the file.
- `cont`: Optional parameter that specifies whether to continue a previous download. If `True`, the download will continue from the last disconnected position. The default value is `False`.
- `save_name`: Optional parameter that specifies the downloaded file name. The default value is the last part of the URL.
- `num_threads`: Optional parameter that specifies the number of threads to use. The default value is 4.
- `tmpdir`: Optional parameter that specifies the name of the temporary directory used during the download process. The default value is ".tmp".

### download_dist

```python
def download_dist(url: str, session: requests.Session, is_server: bool, num_clients: Optional[int] = None,
                  save_name: Optional[str] = None, server_ip: str = "127.0.0.1",
                  port: int = 9999, num_threads: int = 4, server_download: bool = True):
```

Download a file using distributed multithreading and synchronize with the server.

- `url`: The URL of the file.
- `session`: A login session that has been constructed beforehand.
- `is_server`: A boolean parameter that specifies whether it is the server.
- `num_clients`: Optional parameter that specifies the number of clients when it is the server.
- `save_name`: Optional parameter that specifies the downloaded file name. The default value is the last part of the URL.
- `server_ip`: Optional parameter that specifies the IP address of the server when it is the client.
- `port`: Optional parameter that specifies the port number of the server. The default value is 9999.
- `num_threads`: Optional parameter that specifies the number of threads per client. The default value is 4.
- `server_download`: Optional parameter that specifies whether to download a portion of the file on the server. The default value is `True`.
