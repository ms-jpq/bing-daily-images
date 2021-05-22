#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from http.client import HTTPResponse
from json import loads
from pathlib import Path, PurePosixPath
from typing import AbstractSet, Iterable, Tuple, Union, cast
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, build_opener


def _urlopen(req: Union[Request, str]) -> HTTPResponse:
    opener = build_opener()
    resp = opener.open(req)
    return cast(HTTPResponse, resp)


def _fetch(resource: str) -> bytes:
    with _urlopen(resource) as resp:
        return resp.read()


def _sanitize(
    path: str, replace: str = "_", safe_chars: AbstractSet[str] = {" ", ".", "_"}
) -> str:
    sanitized = (c if c.isalnum() or c in safe_chars else replace for c in path)
    return "".join(sanitized).rstrip()


def _bing(count: int) -> Iterable[Tuple[str, Path]]:
    uri = f"https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n={count}"
    res = _fetch(uri)
    hist = loads(res.decode())

    for partial in hist["images"]:
        uri = f"https://www.bing.com/{partial['url']}"
        title = partial["title"]
        date = datetime.strptime(partial["startdate"], "%Y%m%d")
        formatted_date = date.strftime("%Y_%m_%d")
        query = urlparse(uri).query
        file_name = parse_qs(query)["id"][0]
        file_path = PurePosixPath(file_name)
        filename = _sanitize(f"{formatted_date} {title}{file_path.suffix}")
        yield uri, Path(filename)


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-o", "--out", type=Path, required=True)
    parser.add_argument("-d", "--days", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    base_path = Path(args.out).resolve()
    images = _bing(args.days)

    candidates = (
        (uri, filename)
        for uri, filename in images
        if not (base_path / filename).exists()
    )

    def cont(args: Tuple[str, Path]) -> Tuple[Path, bytes]:
        uri, filename = args
        return filename, _fetch(uri)

    with ThreadPoolExecutor() as pool:
        for filename, data in pool.map(cont, candidates):
            (base_path / filename).write_bytes(data)

    print(f"-- | {datetime.now()} | --")


main()
