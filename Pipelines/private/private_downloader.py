import requests


def download():
    for i in range(1000, 6000):
        url = "https://thisdickpicdoesnotexist.com/stylegan2_fakes/" + str(i) + ".jpg"
        r = requests.get(url, allow_redirects=True)
        open("data/" + str(i) + ".jpg", "wb").write(r.content)


if __name__ == "__main__":
    download()
