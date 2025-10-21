from pytest_csv_params.decorator import csv_params
from pynfe.entidades import NotaFiscal
from notas_fiscais.serializacao_nf import SerializacaoXMLNFe400
from pathlib import Path
from pytest_csv_params.decorator import csv_params

class TestNFe:

    @csv_params(data_file="tests/unit/resources/test_nfe.csv")
    def test_importacao_nfe_xml(self,
                                ID, 
                                total_itens,
                                vBC,
                                vICMS,
                                vICMSDeson,
                                vFCPUFDest,
                                vICMSUFDest,
                                vICMSUFRemet,
                                vFCP,
                                vBCST,
                                vST,
                                vFCPST,
                                vFCPSTRet,
                                vProd,
                                vFrete,
                                vSeg,
                                vDesc,
                                vII,
                                vIPI,
                                vIPIDevol,
                                vCOFINS,
                                vOutro,
                                vTotTrib,
                                vPIS,
                                numero_obs
                            ) -> None:

        serializacaoNFe = SerializacaoXMLNFe400(fonte_dados=None)

        filename = f"tests/unit/resources/{ID}.xml"

        nf: NotaFiscal = serializacaoNFe.importar(filename)

        assert nf.emitente != None
        assert nf.cliente_final != None
        assert nf.retirada != None
        assert nf.transporte_transportadora != None
        assert nf.identificador_unico == Path(filename).stem
        assert len(nf.produtos_e_servicos) == int(total_itens)
        assert float(nf.totais_icms_base_calculo) == float(vBC)
        assert float(nf.totais_icms_total) == float(vICMS)
        assert float(nf.totais_icms_desonerado) == float(vICMSDeson)
        assert float(nf.totais_fcp_destino) == float(vFCPUFDest)
        assert float(nf.totais_icms_inter_destino) == float(vICMSUFDest)
        assert float(nf.totais_icms_inter_remetente) == float(vICMSUFRemet)
        assert float(nf.totais_fcp) == float(vFCP)
        assert float(nf.totais_icms_st_base_calculo) == float(vBCST)
        assert float(nf.totais_fcp_st) == float(vFCPST)
        assert float(nf.totais_fcp_st_ret) == float(vFCPSTRet)
        assert float(nf.totais_icms_st_total) == float(vST)
        assert float(nf.totais_icms_total_produtos_e_servicos) == float(vProd)
        assert float(nf.totais_icms_total_frete) == float(vFrete)
        assert float(nf.totais_icms_total_seguro) == float(vSeg)
        assert float(nf.totais_icms_total_desconto) == float(vDesc)
        assert float(nf.totais_icms_total_ii) == float(vII)
        assert float(nf.totais_icms_total_ipi) == float(vIPI)
        assert float(nf.totais_icms_total_ipi_dev) == float(vIPIDevol)
        assert float(nf.totais_icms_cofins) == float(vCOFINS)
        assert float(nf.totais_icms_outras_despesas_acessorias) == float(vOutro)
        assert float(nf.totais_tributos_aproximado) == float(vTotTrib)
        assert float(nf.totais_icms_pis) == float(vPIS)
        assert len(nf.observacoes_contribuinte) == int(numero_obs)

        


    
    