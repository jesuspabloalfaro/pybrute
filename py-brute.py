import json
import logging
import argparse
import requests
import threading
from bruteparse import BruteParse
from exceptions.exceptions import Exceptions
from requests_toolbelt.multipart.encoder import MultipartEncoder

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='w',
                    filename='pybrute.log')


class PyBrute():
    def __init__(self, req_type: str, url: str, headers: dict[str: str],
                 content_type: str, dispo_names: list[str], args) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.req_type = req_type
        self.url = url
        self.headers = headers
        self.content_type = content_type
        self.dispo_names = dispo_names
        self.args = args
        self.data = []

    def _write(self):
        json_data = {
            'data': self.data
        }
        with open(self.args.output, 'w') as f:
            json.dump(json_data, f)

    def _sr_multipart(self, payload: str) -> tuple[str, str]:
        files = {}
        for name in self.dispo_names:
            if (self.args.form_name == name):
                files[name] = payload
            else:
                files[name] = ('', '', 'application/octet-stream')
        multipart_data = MultipartEncoder(files)
        self.headers['Content-Type'] = multipart_data.content_type
        request = requests.Request(self.req_type.upper(),
                                   url=self.url,
                                   data=multipart_data,
                                   headers=self.headers).prepare()
        with requests.Session() as session:
            response = session.send(request)
        content_length = len(response.text)
        content_text = response.text

        self.logger.debug(content_text)

        return (content_length, content_text)

    def _threading_safe_request(self, payload: str, semaphore: threading.Semaphore) -> None:
        with semaphore:
            if (self.content_type == "multipart/form-data"):
                content_length, content_text = self._sr_multipart(payload)
                self.data.append({
                    'content_length': content_length,
                    'payload': payload,
                    'content_text': content_text
                })
            else:
                raise Exceptions("No Request Type Found", code=404)

    def send_request(self) -> None:
        # Clear the file before writing
        with open(self.args.output, 'w'):
            pass

        threads = []
        max_threads = self.args.threads
        semaphore = threading.Semaphore(max_threads)

        with open(self.args.payload) as p:
            for payload in p:
                thread = threading.Thread(target=self._threading_safe_request, args=(payload.strip(), semaphore,))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

        self._write()


def main():
    parser = argparse.ArgumentParser(prog="py-brute", description="Requests Intruder, but Python!")
    parser.add_argument('--ssl', '-s', default=False, action='store_true', help="Set SSL")
    parser.add_argument('--form-name', '-n', required=True, help='Which form data name you want to fuzz')
    parser.add_argument('--payload', '-p', required=True, help='Specify the payload file')
    parser.add_argument('--threads', '-t', default=3, type=int, help='Specify the number of threads')
    parser.add_argument('--output', '-o', required=True, help='Specify the output file')
    parser.add_argument('--input', '-i', required=True, help='Specify the request input file')

    args = parser.parse_args()
    bp = BruteParse(args.input, args.ssl)
    bp.parse()
    pybrute = PyBrute(bp.req_type, bp.url, bp.headers, bp.content_type, bp.content_dispo_names, args)
    pybrute.send_request()


if __name__ == "__main__":
    main()
