import pytest
from pytest_csv_params.decorator import csv_params
from notas_fiscais.parsers import NotaFiscalDigitalizada40OutputParser
from pynfe.utils.flags import CODIGOS_ESTADOS
from pynfe.entidades import NotaFiscal
from datetime import datetime
from langchain_core.documents.base import Blob

import os
from dotenv import load_dotenv
load_dotenv()

class TestExtracaoNotasFiscaisDigitalizadas:


    @pytest.fixture
    def nfop(self) -> NotaFiscalDigitalizada40OutputParser:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model=os.environ["LLM_MODEL"], temperature=0)
        return NotaFiscalDigitalizada40OutputParser(llm=llm)

    def test_importacao_nf_imagem(self,nfop: NotaFiscalDigitalizada40OutputParser):
        image_blob = self.__carregar_blob("resources/NFSE_202500000112417_SKRA.pdf")
        nfop.parse(image_blob)


    def __carregar_blob(self,relative_path: str) -> Blob:
        script_dir = os.path.dirname(__file__)
        return Blob.from_path(os.path.join(script_dir,relative_path))


