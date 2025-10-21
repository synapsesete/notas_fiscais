from click import prompt
from langchain_core.runnables import Runnable
import logging
from typing import override, Any
from pynfe.entidades import NotaFiscal
from langchain_core.prompts import PromptTemplate
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from pathlib import Path
from notas_fiscais.parsers import NotaFiscalOutputParser
import os

logger = logging.getLogger(__name__)

class NFe_Danfe_Runnable(Runnable):

    def __init__(self):
        pass


    @override
    def invoke(self, params: dict[str,Any], config=None):

        chain = self.__llm() #| NotaFiscalOutputParser

        return chain.invoke(self.__prompt_customizado(params["file_path"]))


    def __llm(self) -> Runnable:
        """
        Carrega e retorna a LLM do Agente.
        """
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_ollama import ChatOllama

        if "GOOGLE_API_KEY" in os.environ:
            llm = ChatGoogleGenerativeAI(model=os.environ["LLM_MODEL"],
                                         temperature=0)
        else:
            llm = ChatOllama(
                temperature=0,
                model=os.environ["OLLAMA_LLM_MODEL"],
                base_url=os.environ["OLLAMA_URL"],
            )

        return llm

    def __prompt_customizado(self,file_path: str) -> PromptTemplate:
        """
        Carrega o template do prompt com as instruções de transformar os dados obtidos pela OCR em NotaFiscal Pynfe.
        """

        PROMPTS_RELATIVE_PATH = Path("resources/nf_digital_extracao_prompt.md")

        loader = PyMuPDF4LLMLoader(file_path)
        docs = loader.load()

        prompt = PromptTemplate.from_file(template_file=self.__relative_path(PROMPTS_RELATIVE_PATH))

        formatted_prompt = prompt.format(dados_ocr_nota_fiscal=docs[0],
                                         caminho_arquivo_nota_fiscal=file_path,
                                         schema_path=self.__relative_path("resources/leiauteNFe_v4.00.xsd"),
                                         exemplo_xml_nfe_path=self.__relative_path("resources/exemplo_nfe_4.0.xml")
                                        )

        return formatted_prompt
    

    def __relative_path(self,file_path_relative: str) -> Path:
        return os.path.join(os.path.dirname(__file__),file_path_relative)

