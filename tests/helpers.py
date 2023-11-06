import itertools
from pathlib import Path
from typing import Callable

import yaml

from tests import TEST_DIR


def flatmap(func, *iterable):
    return itertools.chain.from_iterable(map(func, *iterable))


def load_test_data(path: Path, convert: Callable = (lambda x: x), flat: bool = False) -> list[any]:
    with open(path, encoding='utf-8') as file:
        result = yaml.safe_load(file)
        map_ = flatmap if flat else map
        return list(map_(convert, result['data']))


def main():
    load_test_data(TEST_DIR / 'utils/resources/cfpq.yaml')
    pass


if __name__ == "__main__":
    main()
