# 分布式文件下载

简体中文 | [English](./README_en.md)

## 函数列表

### download_multithreading

```python
def download_multithreading(url: str, session: requests.Session,
                            start: int = 0, end: Optional[int] = None, cont: bool = False,
                            save_name: Optional[str] = None, num_threads: int = 4,
                            tmpdir: str = ".tmp") -> Optional[str]:
```

使用多线程下载文件。

- `url`：文件的URL。
- `session`：请先提前构建好一个登录了的session。
- `start`：可选参数，开始下载的位置，默认为0。
- `end`：可选参数，结束下载的位置，默认为文件的长度。
- `cont`：可选参数，是否继续上一次下载。如果为True，则从上一次断开的位置继续下载。默认为False。
- `save_name`：可选参数，下载后的文件名，默认为URL的最后一部分。
- `num_threads`：可选参数，使用的线程数，默认为4。
- `tmpdir`：可选参数，下载时使用的临时文件夹名，默认为".tmp"。

### download_dist

```python
def download_dist(url: str, session: requests.Session, is_server: bool, num_clients: Optional[int] = None,
                  save_name: Optional[str] = None, server_ip: str = "127.0.0.1",
                  port: int = 9999, num_threads: int = 4, server_download: bool = True):
```

使用分布式多线程下载文件，最终同步至服务端。

- `url`：文件的URL。
- `session`：请先提前构建好一个登录了的session。
- `is_server`：是否为服务端。
- `num_clients`：如果是服务端，需要指定客户端数量。
- `save_name`：可选参数，下载后的文件名，默认为URL的最后一部分。
- `server_ip`：可选参数，如果是客户端，需要指定服务端的IP地址。
- `port`：可选参数，指定服务端的端口号，默认为9999。
- `num_threads`：可选参数，每个客户端使用的线程数，默认为4。
- `server_download`：可选参数，是否在服务端下载一部分，默认为True。
