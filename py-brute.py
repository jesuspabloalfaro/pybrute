import argparse
import requests
import threading
from bruteparse import BruteParse


class PyBrute():
    def __init__(self, req_type: str, url: str, headers: dict[str: str],
                 content_type: str, dispo_names: list[str], args) -> None:
        self.req_type = req_type
        self.url = url
        self.headers = headers
        self.content_type = content_type
        self.dispo_names = dispo_names
        self.args = args

    def _write_out(self, content_length: str, content_text: str, payload: str):
        with open(self.args.o, 'a') as file:
            file.write(f"Payload: {payload}\n")
            file.write(f"Content Length: {content_length}\n")
            file.write("Content Text:\n")
            file.write(content_text)

    # Make this async or even split it up?
    def _send_request_helper(self, payload: str) -> None:
        if (self.content_type == "multipart/form-data"):
            files = {}
            for name in self.dispo_names:
                if (self.args.n == name):
                    files[name] = payload
                else:
                    files[name] = ""
            request = requests.Request(self.req_type.upper(), self.url, files=files).prepare()

            with requests.Session() as session:
                response = session.send(request)

            content_length = response.headers.get('Content-Length', 'Unknown')
            content_text = response.text

            self._write_out(content_length, content_text, payload)

    def _threading_safe_request(self, payload: str, semaphore: threading.Semaphore) -> None:
        with semaphore:
            self._send_request_helper(payload)

    def send_request(self) -> None:
        with open(self.args.o, 'w'):
            pass

        threads = []
        max_threads = self.args.t
        semaphore = threading.Semaphore(max_threads)

        with open(self.args.p) as p:
            for payload in p:
                thread = threading.Thread(target=self._threading_safe_request, args=(payload, semaphore,))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()


def main():
    parser = argparse.ArgumentParser(prog="py-brute", description="Requests Intruder, but Python!")
    parser.add_argument('-s', action='store_true', help="Set SSL")
    parser.add_argument('-n', help='Which form data name you want to fuzz')
    parser.add_argument('-p', help='Specify the payload file')
    parser.add_argument('-t', type=int, help='Specify the number of threads')
    parser.add_argument('-o', help='Specify the output file')
    parser.add_argument('-i', help='Specify the request input file')

    args = parser.parse_args()

    bp = BruteParse(args.i, args.s)
    bp.parse()

    pybrute = PyBrute(bp.req_type, bp.url, bp.headers, bp.content_type, bp.content_dispo_names, args)
    pybrute.send_request()


if __name__ == "__main__":
    main()
