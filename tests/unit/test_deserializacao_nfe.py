from pytest_csv_params.decorator import csv_params
from pynfe.entidades import NotaFiscal
import pytest
from notas_fiscais.serializacao_nf import SerializacaoXMLNFe400
from pathlib import Path

class TestNFe:

    @pytest.mark.parametrize("filename,total_produtos_servicos_esperados",[("NFe35250401166372001127550030002655131523445210.xml",4)])
    def test_importacao_nfe_xml(self,filename: str, total_produtos_servicos_esperados: int) -> None:

        serializacaoNFe = SerializacaoXMLNFe400(fonte_dados=None)

        nf: NotaFiscal =  serializacaoNFe.importar(f"./tests/unit/resources/{filename}")

        assert nf.emitente != None
        assert nf.cliente_final != None
        assert nf.retirada != None
        assert nf.transporte_transportadora != None
        assert nf.identificador_unico == Path(filename).stem
        assert len(nf.produtos_e_servicos) == total_produtos_servicos_esperados

        


    
    