from download import download_multithreading

import requests

if __name__ == "__main__":
    session = requests.Session()
    with open("headers.txt", "r") as f:
        for line in f.readlines():
            try:
                key, value = line.strip().split(": ")
                session.headers.update({key: value})
            except:
                pass

    url = "https://murray-lab.caltech.edu/CTX/V01/tiles/MurrayLab_GlobalCTXMosaic_V01_E076_N84.zip"
    download_multithreading(url, session, num_threads=4, cont=True)
