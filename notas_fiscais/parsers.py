from langchain_core.output_parsers import BaseOutputParser

from typing import Any
from pynfe.entidades import NotaFiscal, Emitente, Cliente, Transportadora
from pynfe.entidades.notafiscal import NotaFiscalEntregaRetirada
from pynfe.utils.flags import CODIGOS_ESTADOS
from datetime import datetime
from decimal import Decimal
import xmltodict


class NotaFiscalOutputParser(BaseOutputParser[NotaFiscal]):
    """
    Parser customizado que recebe um XML e converte para uma nota fiscal Pynfe.
    """
    def parse(self,xml_input: Any) -> NotaFiscal:

        nf = xmltodict.parse(xml_input=xml_input)

        nota_fiscal = NotaFiscal(
                                    codigo_numerico_aleatorio = nf['NFe']['infNFe']['ide'].get('cNF'),
                                    uf = self.__extrair_uf_a_partir_do_codigo(nf['NFe']['infNFe']['ide']['cUF']),
                                    modelo = int(nf['NFe']['infNFe']['ide']['mod']),
                                    serie = nf['NFe']['infNFe']['ide']['serie'],
                                    numero_nf = nf['NFe']['infNFe']['ide']['nNF'],
                                    data_emissao = datetime.strptime(nf['NFe']['infNFe']['ide']['dEmi'],'%Y-%m-%d'),
                                    data_saida_entrada = datetime.strptime(nf['NFe']['infNFe']['ide']['dSaiEnt']+' '+nf['NFe']['infNFe']['ide']['hSaiEnt'],'%Y-%m-%d %H:%M:%S') if nf['NFe']['infNFe']['ide'].get('dSaiEnt') else None,
                                    tipo_documento = int(nf['NFe']['infNFe']['ide']['tpNF']) if nf['NFe']['infNFe']['ide'].get('tpNF') else None,
                                    municipio = nf['NFe']['infNFe']['ide'].get('cMunFG'),
                                    tipo_impressao_danfe = int(nf['NFe']['infNFe']['ide']['tpImp']),
                                    forma_emissao = nf['NFe']['infNFe']['ide']['tpEmis'],
                                    finalidade_emissao = nf['NFe']['infNFe']['ide']['finNFe'],
                                    processo_emissao = nf['NFe']['infNFe']['ide'].get('procEmi'),
                                    emitente = self.__criar_emitente(nf),
                                    cliente = self.__criar_cliente(nf),
                                    retirada = self.__criar_endereco_retirada(nf),
                                    entrega = self.__criar_endereco_entrega(nf),
                            )
    
        self.__adicionar_itens_da_nota(nota_fiscal,nf)
        self.__definir_transportadora(nota_fiscal,nf)
        self.__definir_info_adicionais(nota_fiscal,nf)

        return nota_fiscal



    @property
    def _type(self) -> str:
        return "pynfe_output_parser"
    


    def __definir_info_adicionais(self,nota_fiscal: NotaFiscal,nf) -> None:
        nf_info_adic = nf['NFe']['infNFe'].get('infAdic')
        if nf_info_adic:
            nota_fiscal.informacoes_adicionais_interesse_fisco = nf_info_adic['infAdFisco']
            nota_fiscal.informacoes_complementares_interesse_contribuinte = nf_info_adic['infCpl']


    def __definir_transportadora(self,nota_fiscal: NotaFiscal,nf) -> None:
        nf_transp = nf['NFe']['infNFe'].get('transp')
        if nf_transp:
            nf_tranportadora = nf_transp['transporta']
            nota_fiscal.transporte_modalidade_frete = int(nf_transp['modFrete'])
            nota_fiscal.transporte_transportadora = Transportadora(
                                                            numero_documento = nf_tranportadora['CNPJ'],
                                                            razao_social = nf_tranportadora['xNome'],
                                                            inscricao_estadual = nf_tranportadora['IE'],
                                                            endereco_logradouro = nf_tranportadora['xEnder'],
                                                            endereco_municipio = nf_tranportadora['xMun'],
                                                            endereco_uf = nf_tranportadora['UF']
                                                         )
            
            nf_veiculo = nf_transp['veicTransp']
            nota_fiscal.transporte_veiculo_placa = nf_veiculo['placa']
            nota_fiscal.transporte_veiculo_uf = nf_veiculo['UF']
            nota_fiscal.transporte_veiculo_rntc = nf_veiculo['RNTC']

            nf_reboque = nf_transp['reboque']
            nota_fiscal.transporte_reboque_placa = nf_reboque['placa']
            nota_fiscal.transporte_reboque_uf = nf_reboque['UF']
            nota_fiscal.transporte_reboque_rntc = nf_reboque['RNTC']

            nf_vol = nf_transp['vol']

            volume = nota_fiscal.adicionar_transporte_volume(
                                                    quantidade = Decimal(nf_vol['qVol']),
                                                    especie = nf_vol['esp'],
                                                    marca = nf_vol['marca'],
                                                    numeracao = nf_vol['nVol'],
                                                    peso_liquido = Decimal(nf_vol['pesoL']),
                                                    peso_bruto = Decimal(nf_vol['pesoB'])
                                                )
            

            nf_lacres = nf_vol['lacres']
            volume.adicionar_lacre(
                                        numero_lacre = nf_lacres['nLacre']
            )
        

    def __adicionar_itens_da_nota(self,nota_fiscal: NotaFiscal, nf) -> None:

        for nf_item in nf['NFe']['infNFe']['det']:
                            nota_fiscal.adicionar_produto_servico(
                                                                    codigo = nf_item['prod']['cProd'],
                                                                    ean = nf_item['prod'].get('cEAN','SEM GTIN'),
                                                                    descricao = nf_item['prod']['xProd'],
                                                                    cfop = nf_item['prod']['CFOP'],
                                                                    unidade_comercial = nf_item['prod']['uCom'],
                                                                    quantidade_comercial = Decimal(nf_item['prod']['qCom']),
                                                                    valor_unitario_comercial = Decimal(nf_item['prod']['vUnCom']),
                                                                    valor_total_bruto = Decimal(nf_item['prod']['vProd']),
                                                                    ean_tributavel = nf_item['prod'].get('cEANTrib','SEM GTIN'),
                                                                    unidade_tributavel = nf_item['prod']['uTrib'],
                                                                    quantidade_tributavel = Decimal(nf_item['prod']['qTrib']),
                                                                    valor_unitario_tributavel = nf_item['prod']['uTrib'],
                                                                    icms_modalidade = nf_item['imposto']['ICMS']['ICMS00']['CST'],
                                                                    icms_origem = int(nf_item['imposto']['ICMS']['ICMS00']['orig']),
                                                                    icms_modalidade_determinacao_bc = int(nf_item['imposto']['ICMS']['ICMS00']['modBC']),
                                                                    icms_valor_base_calculo=Decimal(nf_item['imposto']['ICMS']['ICMS00']['vBC']),
                                                                    icms_aliquota=Decimal(nf_item['imposto']['ICMS']['ICMS00']['pICMS']),
                                                                    icms_valor=Decimal(nf_item['imposto']['ICMS']['ICMS00']['vICMS']),
                                                                    pis_situacao_tributaria=nf_item['imposto']['PIS']['PISAliq']['CST'],
                                                                    pis_valor_base_calculo=Decimal(nf_item['imposto']['PIS']['PISAliq']['vBC']),
                                                                    pis_aliquota_percentual=Decimal(nf_item['imposto']['PIS']['PISAliq']['pPIS']),
                                                                    pis_valor=Decimal(nf_item['imposto']['PIS']['PISAliq']['vPIS']),
                                                                    cofins_situacao_tributaria=nf_item['imposto']['COFINS']['COFINSAliq']['CST'],
                                                                    cofins_valor_base_calculo=Decimal(nf_item['imposto']['COFINS']['COFINSAliq']['vBC']),
                                                                    cofins_aliquota_percentual=Decimal(nf_item['imposto']['COFINS']['COFINSAliq']['pCOFINS']),
                                                                    cofins_valor=Decimal(nf_item['imposto']['COFINS']['COFINSAliq']['vCOFINS']),


                )

    @staticmethod
    def __criar_emitente(nf) -> Emitente:
        return  Emitente(
                            cnpj = nf['NFe']['infNFe']['emit']['CNPJ'],
                            razao_social=nf['NFe']['infNFe']['emit']['xNome'],
                            nome_fantasia=nf['NFe']['infNFe']['emit'].get('xFant'),
                            endereco_logradouro=nf['NFe']['infNFe']['emit']['enderEmit']['xLgr'],
                            endereco_numero=nf['NFe']['infNFe']['emit']['enderEmit']['nro'],
                            endereco_complemento=nf['NFe']['infNFe']['emit']['enderEmit'].get('xCpl'),
                            endereco_bairro=nf['NFe']['infNFe']['emit']['enderEmit'].get('xBairro'),
                            endereco_cod_municipio=nf['NFe']['infNFe']['emit']['enderEmit'].get('cMun'),
                            endereco_municipio=nf['NFe']['infNFe']['emit']['enderEmit']['xMun'],
                            endereco_uf=nf['NFe']['infNFe']['emit']['enderEmit']['UF'],
                            endereco_cep=nf['NFe']['infNFe']['emit']['enderEmit'].get('CEP'),
                            endereco_pais=nf['NFe']['infNFe']['emit']['enderEmit']['cPais'],
                            endereco_telefone=nf['NFe']['infNFe']['emit']['enderEmit'].get('fone'),
                            inscricao_estadual=nf['NFe']['infNFe']['emit']['IE'])
    

    @staticmethod
    def __criar_cliente(nf) -> Cliente:
        return Cliente(
                          numero_documento = nf['NFe']['infNFe']['dest']['CNPJ'],
                          razao_social=nf['NFe']['infNFe']['dest']['xNome'],
                          endereco_logradouro=nf['NFe']['infNFe']['dest']['enderDest']['xLgr'],
                          endereco_numero=nf['NFe']['infNFe']['dest']['enderDest']['nro'],
                          endereco_complemento=nf['NFe']['infNFe']['dest']['enderDest'].get('xCpl'),
                          endereco_bairro=nf['NFe']['infNFe']['dest']['enderDest']['xBairro'],
                          endereco_cod_municipio=nf['NFe']['infNFe']['dest']['enderDest'].get('cMun'),
                          endereco_municipio=nf['NFe']['infNFe']['dest']['enderDest']['xMun'],
                          endereco_uf=nf['NFe']['infNFe']['dest']['enderDest']['UF'],
                          endereco_cep=nf['NFe']['infNFe']['dest']['enderDest'].get('CEP'),
                          endereco_pais=nf['NFe']['infNFe']['dest']['enderDest']['cPais'],
                          endereco_telefone=nf['NFe']['infNFe']['dest']['enderDest'].get('fone'),
                          inscricao_estadual=nf['NFe']['infNFe']['dest']['IE']
        )


    @staticmethod
    def __criar_endereco_retirada(nf) -> NotaFiscalEntregaRetirada:
        if nf['NFe']['infNFe'].get('retirada'):
            return  NotaFiscalEntregaRetirada(
                            numero_documento = nf['NFe']['infNFe']['retirada']['CNPJ'],
                            endereco_logradouro=nf['NFe']['infNFe']['retirada']['xLgr'],
                            endereco_numero=nf['NFe']['infNFe']['retirada']['nro'],
                            endereco_complemento=nf['NFe']['infNFe']['retirada']['xCpl'],
                            endereco_bairro=nf['NFe']['infNFe']['retirada']['xBairro'],
                            endereco_cod_municipio=nf['NFe']['infNFe']['retirada']['cMun'],
                            endereco_municipio=nf['NFe']['infNFe']['retirada']['xMun'],
                            endereco_uf=nf['NFe']['infNFe']['retirada']['UF'],
                            endereco_cep=nf['NFe']['infNFe']['retirada'].get('CEP'),
                            endereco_pais=nf['NFe']['infNFe']['retirada'].get('cPais'),
                            endereco_telefone=nf['NFe']['infNFe']['retirada'].get('fone')
            )

    @staticmethod
    def __criar_endereco_entrega(nf) -> NotaFiscalEntregaRetirada:
        if nf['NFe']['infNFe'].get('entrega'):
            return  NotaFiscalEntregaRetirada(
                            numero_documento = nf['NFe']['infNFe']['entrega']['CNPJ'],
                            endereco_logradouro=nf['NFe']['infNFe']['entrega']['xLgr'],
                            endereco_numero=nf['NFe']['infNFe']['entrega']['nro'],
                            endereco_complemento=nf['NFe']['infNFe']['entrega']['xCpl'],
                            endereco_bairro=nf['NFe']['infNFe']['entrega']['xBairro'],
                            endereco_cod_municipio=nf['NFe']['infNFe']['entrega']['cMun'],
                            endereco_municipio=nf['NFe']['infNFe']['entrega']['xMun'],
                            endereco_uf=nf['NFe']['infNFe']['entrega']['UF'],
                            endereco_cep=nf['NFe']['infNFe']['entrega'].get('CEP'),
                            endereco_pais=nf['NFe']['infNFe']['entrega'].get('cPais'),
                            endereco_telefone=nf['NFe']['infNFe']['entrega'].get('fone')
            )
    
    @staticmethod
    def __extrair_uf_a_partir_do_codigo(codUF: str) -> str:
        for UF,codigo in CODIGOS_ESTADOS.items():
            if codigo == codUF:
                return UF
