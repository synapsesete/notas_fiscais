
from langchain_core.output_parsers import BaseOutputParser
from typing import override
from notas_fiscais.serializacao_nf import SerializacaoXMLNFe400
from pynfe.entidades import NotaFiscal

from sqlalchemy import over

class NotaFiscalOutputParser(BaseOutputParser):
    """
    Faz o parsing do XML para o formato de NF-e do Pynfe.
    """

    @override
    def parse(self, text: str) -> NotaFiscal:

        serializacaoNFe = SerializacaoXMLNFe400(fonte_dados=None)

        nf: NotaFiscal = serializacaoNFe.importar(text)

        return nf