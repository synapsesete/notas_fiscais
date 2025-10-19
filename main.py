import logging

from notas_fiscais.parsers import NFeOutputParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def main():

    filename = "tests/unit/resources/test.xml"

    with open(filename, 'r', encoding='utf-8') as file:
         my_xml = file.read()

    nf_parser = NFeOutputParser()

    nf = nf_parser.parse(my_xml)

    print(nf)


if __name__ == "__main__":
    main()