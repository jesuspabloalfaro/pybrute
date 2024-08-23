import regex as re


class BruteParse:
    def __init__(self, filename: str, ssl: bool) -> None:
        self.filename = filename
        self.ssl = ssl
        self.req_type = ""
        self.url = ""
        self.content_type = ""
        self.headers = {}
        self.content_dispo_names = []

    def _parser_helper(self, pattern: str, text: str, group: int) -> str | dict[str: str]:
        match = re.search(pattern, text, re.MULTILINE)
        return (lambda: match.group(group) if match.group() else None)()

    def _parse_headers(self, pattern: str, text: str) -> dict[str: str]:
        headers = {}
        for line in text.strip().split('\n'):
            if line.strip() == "":
                break

            match = re.match(pattern, line)
            if match:
                key = match.group(1)
                value = match.group(2)
                headers[key] = value

        return headers

    def _parse_content_dispo_names(self, text: str) -> list[str]:
        return re.findall(r'name="([^"]+)"', text)

    def _get_file_content(self):
        with open(self.filename, 'r') as f:
            content = f.read()
        return content

    def parse(self) -> None:
        text = self._get_file_content()
        req_pat = r'\b(POST|GET|PUT|DEL|DELETE|PATCH|HEAD|OPTIONS)\b'
        endpoint_pat = r'(?:POST|GET|PUT|DEL|DELETE|PATCH|HEAD|OPTIONS)\b\s+(\S*)'
        host_pat = r'(?i)^\s*Host:\s*(\S+)\s*$'
        headers_pat = r'^\s*(.*?):\s*(.*?)(;.*)?\s*$'

        self.req_type = self._parser_helper(req_pat, text, 0)
        ep = self._parser_helper(endpoint_pat, text, 1)
        host = self._parser_helper(host_pat, text, 1)
        self.url = f"http{'s' if self.ssl else ''}://{host}{ep}"

        self.headers = self._parse_headers(headers_pat, text)
        self.content_type = self.headers["Content-Type"]

        self.content_dispo_names = self._parse_content_dispo_names(text)


if __name__ == "__main__":
    print("This is a library file. Do not run.")
