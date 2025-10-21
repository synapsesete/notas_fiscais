import logging
from langchain_pymupdf4llm import PyMuPDF4LLMLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def main():

    file_path = "tests/unit/resources/NFe35250401166372001127550030002655131523445210.pdf"
    loader = PyMuPDF4LLMLoader(file_path)
    docs = loader.load()

    print(docs[0])


if __name__ == "__main__":
    main()