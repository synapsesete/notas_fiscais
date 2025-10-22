from notas_fiscais.langchain_nf_runnables import NFe_Danfe_Runnable
from pynfe.entidades import NotaFiscal

import os
from dotenv import load_dotenv
load_dotenv()
import pytest

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("filename",["NFe35250401166372001127550030002655131523445210.pdf","33240402558157022565550000061839161969711946.pdf"])
def test_parsing_danfe(filename: str) -> None:

    file_path = f"tests/unit/resources/{filename}"

    llm_danfe = NFe_Danfe_Runnable()

    nf: Notafiscal = llm_danfe.invoke({"file_path":file_path})

    assert nf != None



