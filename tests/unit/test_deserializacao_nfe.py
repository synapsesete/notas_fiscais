from pytest_csv_params.decorator import csv_params
from notas_fiscais.parsers import NotaFiscalOutputParser
from pynfe.utils.flags import CODIGOS_ESTADOS
from pynfe.entidades import NotaFiscal
from datetime import datetime

class TestNFe:


    @csv_params(
        data_file="./tests/unit/resources/nfe.csv",
    )
    def test_importacao_nfe_xml(self,
                                chave_acesso,
                                cnf,
                                cuf,
                                modelo,
                                serie,
                                nnf,
                                demi,
                                dsaient,
                                hsaient,
                                tpnf,
                                cmunfg,
                                tpimp,
                                tpemis,
                                cdv,
                                tpamb,
                                finnfe,
                                procemi,
                                verproc
                                ):
        nf = self.__extrair_nf(chave_acesso)

        assert CODIGOS_ESTADOS[nf.uf] == cuf
        assert nf.data_emissao == datetime.strptime(demi,'%Y-%m-%d')
        assert nf.emitente.cnpj
        assert nf.modelo == int(modelo)
        assert nf.serie == serie
        assert nf.numero_nf == nnf
        assert nf.forma_emissao == tpemis
        assert nf.codigo_numerico_aleatorio == cnf
        assert nf.data_saida_entrada == datetime.strptime(dsaient+' '+hsaient,'%Y-%m-%d %H:%M:%S')
        assert nf.tipo_documento == int(tpnf)
        assert nf.municipio == cmunfg
        assert nf.tipo_impressao_danfe == int(tpimp)
        assert nf.finalidade_emissao == finnfe
        assert nf.processo_emissao == procemi
#        assert nf.identificador_unico == chave_acesso

    @csv_params(
        data_file="./tests/unit/resources/nfe_emitente.csv"
    )
    def test_importacao_nfe_dados_emitente_xml(self,
                                               chave_acesso,
                                               cnpj,
                                               xnome,
                                               xfant,
                                               xlgr,
                                               nro,
                                               xcpl,
                                               xbairro,
                                               cmun,
                                               xmun,
                                               uf,
                                               cep,
                                               cpais,
                                               xpais,
                                               fone,
                                               ie
                                              ):
        
        nf = self.__extrair_nf(chave_acesso)

        assert nf.emitente.cnpj == cnpj
        assert nf.emitente.razao_social == xnome
        assert nf.emitente.nome_fantasia == xfant
        assert nf.emitente.endereco_logradouro == xlgr
        assert nf.emitente.endereco_numero == nro
        assert nf.emitente.endereco_complemento == xcpl
        assert nf.emitente.endereco_bairro == xbairro
        assert nf.emitente.endereco_cod_municipio == cmun
        assert nf.emitente.endereco_municipio == xmun
        assert nf.emitente.endereco_uf == uf
        assert nf.emitente.endereco_cep == cep
        assert nf.emitente.endereco_pais == cpais
        assert nf.emitente.endereco_telefone == fone
        assert nf.emitente.inscricao_estadual == ie

    @csv_params(
        data_file="./tests/unit/resources/nfe_cliente.csv"
    )
    def test_importacao_nfe_dados_cliente_xml(self,
                                               chave_acesso,
                                               cnpj,
                                               xnome,
                                               xlgr,
                                               nro,
                                               xcpl,
                                               xbairro,
                                               cmun,
                                               xmun,
                                               uf,
                                               cep,
                                               cpais,
                                               xpais,
                                               fone,
                                               ie
                                              ):
        
        nf = self.__extrair_nf(chave_acesso)

        assert nf.cliente.numero_documento == cnpj
        assert nf.cliente.razao_social == xnome
        assert nf.cliente.endereco_logradouro == xlgr
        assert nf.cliente.endereco_numero == nro
        assert nf.cliente.endereco_complemento == xcpl
        assert nf.cliente.endereco_bairro == xbairro
        assert nf.cliente.endereco_cod_municipio == cmun
        assert nf.cliente.endereco_municipio == xmun
        assert nf.cliente.endereco_uf == uf
        assert nf.cliente.endereco_cep == cep
        assert nf.cliente.endereco_pais == cpais
        assert nf.cliente.endereco_telefone == fone
        assert nf.cliente.inscricao_estadual == ie

    @csv_params(
        data_file="./tests/unit/resources/nfe_retirada.csv"
    )
    def test_importacao_nfe_dados_retirada_xml(self,
                                               chave_acesso,
                                               cnpj,
                                               xlgr,
                                               nro,
                                               xcpl,
                                               xbairro,
                                               cmun,
                                               xmun,
                                               uf
                                              ):
        
        nf = self.__extrair_nf(chave_acesso)

        assert nf.retirada.numero_documento == cnpj
        assert nf.retirada.endereco_logradouro == xlgr
        assert nf.retirada.endereco_numero == nro
        assert nf.retirada.endereco_complemento == xcpl
        assert nf.retirada.endereco_bairro == xbairro
        assert nf.retirada.endereco_cod_municipio == cmun
        assert nf.retirada.endereco_municipio == xmun
        assert nf.retirada.endereco_uf == uf

    @csv_params(
        data_file="./tests/unit/resources/nfe_entrega.csv"
    )
    def test_importacao_nfe_dados_entrega_xml(self,
                                               chave_acesso,
                                               cnpj,
                                               xlgr,
                                               nro,
                                               xcpl,
                                               xbairro,
                                               cmun,
                                               xmun,
                                               uf
                                              ):
        
        nf = self.__extrair_nf(chave_acesso)

        assert nf.entrega.numero_documento == cnpj
        assert nf.entrega.endereco_logradouro == xlgr
        assert nf.entrega.endereco_numero == nro
        assert nf.entrega.endereco_complemento == xcpl
        assert nf.entrega.endereco_bairro == xbairro
        assert nf.entrega.endereco_cod_municipio == cmun
        assert nf.entrega.endereco_municipio == xmun
        assert nf.entrega.endereco_uf == uf



    def __extrair_nf(self,chave_acesso) -> NotaFiscal:
        filename = f"./tests/unit/resources/{chave_acesso}.xml"

        with open(filename, 'r', encoding='utf-8') as file:
             my_xml = file.read()

        nf_parser = NotaFiscalOutputParser()

        nf = nf_parser.parse(my_xml)

        return nf

        


    
    