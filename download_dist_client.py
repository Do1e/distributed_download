from download import download_dist

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
    download_dist(url, session, is_server=False, num_threads=16)
