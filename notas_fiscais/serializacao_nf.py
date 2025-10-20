from typing import override
from pynfe.processamento.serializacao import SerializacaoXML,Serializacao
from pathlib import Path
from typing import Any, OrderedDict
from pynfe.entidades import NotaFiscal, Emitente, Cliente, Transportadora
from pynfe.entidades.notafiscal import NotaFiscalEntregaRetirada,NotaFiscalProduto
from datetime import datetime
from sqlalchemy import over
import xmltodict
from abc import ABC, abstractmethod
from decimal import Decimal


class SerializacaoXMLNFe400(SerializacaoXML):
    """
    Implementação da classe SerializacaoXML que implementa a importação de uma NFe versão 4.00 em formato XML.
    """

    @override
    def importar(self, origem: str) -> NotaFiscal:

        if self.__string_parece_ser_nome_arquivo(origem):
            xml_content = self.__extrair_xml_arquivo(origem)
        else:
            xml_content = origem

        nf_dict: OrderedDict[str,Any] = xmltodict.parse(xml_input=xml_content)

        nota_fiscal = _SerializacaoXMLNFe400TotalDecorator(_SerializacaoXMLNFe400TranspDecorator
                                                           (_SerializacaoXMLNFe400ItensDecorator
                                                            (_SerializacaoXMLNFe400RetiradaDecorator
                                                             (_SerializacaoXMLNFe400DestDecorator
                                                              (_SerializacaoXMLNFe400EmitDecorator
                                                               (_SerializacaoXMLNFe400Ide(fonte_dados=super()._fonte_dados))))))).importar(nf_dict)

        return nota_fiscal


    def __string_parece_ser_nome_arquivo(self,origem: str) -> bool:
        from pathlib import Path
        path_obj = Path(origem)
        # Check if a suffix (extension) exists and is not an empty string
        return bool(path_obj.suffix)
    

    def __extrair_xml_arquivo(self,filename: str) -> str:
        with open(filename, 'r', encoding='utf-8') as file:
             xml_content = file.read()
        return xml_content


class _SerializacaoXMLNFe400Ide(Serializacao):
    """
    Parser privado que recebe um dicionario de uma NF-e versão 4.00 e faz o parsing do Grupo B (Identificação da NF-e)
    """
    @override
    def importar(self, nf: OrderedDict[str,Any]) -> NotaFiscal:

        ide : OrderedDict[str,Any] = nf['nfeProc']['NFe']['infNFe']['ide']

        nota_fiscal = NotaFiscal(
                                    uf = self.__extrair_uf_a_partir_do_codigo(ide['cUF']),
                                    codigo_numerico_aleatorio = int(ide['cNF']) if ide.get('cNF') else None,
                                    natureza_operacao = ide['natOp'],
                                    modelo = ide['mod'],
                                    serie = ide['serie'],
                                    numero_nf = ide['nNF'],
                                    data_emissao = datetime.strptime(ide['dhEmi'],'%Y-%m-%dT%H:%M:%S%z'),
                                    data_saida_entrada = datetime.strptime(ide['dhSaiEnt'],'%Y-%m-%d %H:%M:%S') if ide.get('dhSaiEnt') else None,
                                    indicador_destino = int(ide['idDest']),
                                    tipo_documento = int(ide['tpNF']),
                                    municipio = ide['cMunFG'],
                                    tipo_impressao_danfe = int(ide['tpImp']),
                                    forma_emissao = ide['tpEmis'],
                                    finalidade_emissao = int(ide['finNFe']),
                                    indicador_presencial = int(ide['indPres']),
                                    indicador_intermediador = int(ide['indIntermed']) if ide.get('indIntermed') else None,
                                    cliente_final = int(ide['indFinal']),
                                    processo_emissao = int(ide['procEmi']),
                                    versao_processo_emissao = ide['verProc']
                            )

        return nota_fiscal
    
    @staticmethod
    def __extrair_uf_a_partir_do_codigo(codUF: str) -> str:
        from pynfe.utils.flags import CODIGOS_ESTADOS
        for UF,codigo in CODIGOS_ESTADOS.items():
            if codigo == codUF:
                return UF


class SerializacaoXMLNFe400Decorator(Serializacao, ABC):
    """
    Classe abstrata que define a base de decorators para output parsers de notas fiscais.
    """
    def __init__(self,serializacao: Serializacao)->None:
        self.__serializacao = serializacao

    @override
    def importar(self,nf: OrderedDict[str,Any]) -> NotaFiscal:
        nota_fiscal = self.__serializacao.importar(nf)
        return self._decorate(nf,nota_fiscal)

    @abstractmethod
    def _decorate(self,nf: OrderedDict[str,Any],nota_fiscal: NotaFiscal) -> NotaFiscal:
        pass

class _SerializacaoXMLNFe400EmitDecorator(SerializacaoXMLNFe400Decorator):
    """
    Decorator que adiciona o emitente na Nota Fiscal.
    """
    @override
    def _decorate(self,nf: OrderedDict[str,Any],nota_fiscal: NotaFiscal) -> NotaFiscal:
        nota_fiscal.emitente = self.__criar_emitente(nf)
        return nota_fiscal

    def __criar_emitente(self,nf: OrderedDict[str,Any]) -> Emitente:
        emit : OrderedDict[str,Any] = nf['nfeProc']['NFe']['infNFe']['emit']
        return  Emitente(
                             cnpj = emit['CNPJ'],
                             razao_social=emit['xNome'],
                             nome_fantasia=emit.get('xFant'),
                             endereco_logradouro=emit['enderEmit']['xLgr'],
                             endereco_numero=emit['enderEmit']['nro'],
                             endereco_complemento=emit['enderEmit'].get('xCpl'),
                             endereco_bairro=emit['enderEmit'].get('xBairro'),
                             endereco_cod_municipio=emit['enderEmit'].get('cMun'),
                             endereco_municipio=emit['enderEmit']['xMun'],
                             endereco_uf=emit['enderEmit']['UF'],
                             endereco_cep=emit['enderEmit'].get('CEP'),
                             endereco_pais=emit['enderEmit']['cPais'],
                             endereco_telefone=emit['enderEmit'].get('fone'),
                             inscricao_estadual=emit['IE'],
                             inscricao_estadual_subst_tributaria=emit.get('IEST'),
                             inscricao_municipal=emit['IM'],
                             cnae_fiscal=emit.get('CNAE'),
                             codigo_de_regime_tributario=emit['CRT']

                        )
    
class _SerializacaoXMLNFe400DestDecorator(SerializacaoXMLNFe400Decorator):
    """
    Decorator que adiciona o destinatário na Nota Fiscal.
    """
    @override
    def _decorate(self,nf: OrderedDict[str,Any],nota_fiscal: NotaFiscal) -> NotaFiscal:
        nota_fiscal.cliente = self.__criar_cliente(nf)
        return nota_fiscal
    
    def __criar_cliente(self,nf: OrderedDict[str,Any]) -> Cliente:
        dest : OrderedDict[str,Any] = nf['nfeProc']['NFe']['infNFe']['dest']
        return Cliente(
                          numero_documento = dest.get('CNPJ') or dest.get('CPF'),
                          razao_social=dest.get('xNome'),
                          inscricao_suframa = dest.get('ISUF'),
                          email = dest.get('email'),
                          indicador_ie = int(dest['indIEDest']),
                          endereco_logradouro=dest['enderDest']['xLgr'],
                          endereco_numero=dest['enderDest']['nro'],
                          endereco_complemento=dest['enderDest'].get('xCpl'),
                          endereco_bairro=dest['enderDest']['xBairro'],
                          endereco_cod_municipio=dest['enderDest'].get('cMun'),
                          endereco_municipio=dest['enderDest']['xMun'],
                          endereco_uf=dest['enderDest']['UF'],
                          endereco_cep=dest['enderDest'].get('CEP'),
                          endereco_pais=dest['enderDest']['cPais'],
                          endereco_telefone=dest['enderDest'].get('fone'),
                          inscricao_estadual=dest.get('IE'),
                          inscricao_municipal=dest.get('IM')
        )

class _SerializacaoXMLNFe400RetiradaDecorator(SerializacaoXMLNFe400Decorator):
    """
    Decorator que adiciona a retirada na Nota Fiscal.
    """
    @override
    def _decorate(self,nf: OrderedDict[str,Any],nota_fiscal: NotaFiscal) -> NotaFiscal:
        nota_fiscal.retirada = self.__criar_endereco_retirada(nf)
        return nota_fiscal
    
    def __criar_endereco_retirada(self,nf: OrderedDict[str,Any]) -> NotaFiscalEntregaRetirada:
        retirada : OrderedDict[str,Any] = nf['nfeProc']['NFe']['infNFe'].get('retirada')
        if retirada:
            return  NotaFiscalEntregaRetirada(
                            numero_documento = retirada['CNPJ'],
                            endereco_logradouro=retirada['xLgr'],
                            endereco_numero=retirada['nro'],
                            endereco_complemento=retirada['xCpl'],
                            endereco_bairro=retirada['xBairro'],
                            endereco_cod_municipio=retirada['cMun'],
                            endereco_municipio=retirada['xMun'],
                            endereco_uf=retirada['UF'],
                            endereco_cep=retirada.get('CEP'),
                            endereco_pais=retirada.get('cPais'),
                            endereco_telefone=retirada.get('fone'),
                            email = retirada.get('email')
            )

class _SerializacaoXMLNFe400ItensDecorator(SerializacaoXMLNFe400Decorator):
    """
    Decorator que adiciona os detalhes dos itens da NF.
    """
    @override
    def _decorate(self,nf: OrderedDict[str,Any],nota_fiscal: NotaFiscal) -> NotaFiscal:
        for nf_item in nf['nfeProc']['NFe']['infNFe']['det']:
            nota_fiscal.adicionar_produto_servico(
                                            codigo = nf_item['prod']['cProd'],
                                            ean = nf_item['prod'].get('cEAN','SEM GTIN'),
                                            descricao = nf_item['prod']['xProd'],
                                            cfop = nf_item['prod'].get('CFOP'),
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
                                            desconto = Decimal(nf_item['prod']['vDesc'])


        )
        
        return nota_fiscal
    

class _SerializacaoXMLNFe400TranspDecorator(SerializacaoXMLNFe400Decorator):
    """
    Decorator que adiciona dados da transportadora na Nota Fiscal.
    """
    @override
    def _decorate(self,nf: OrderedDict[str,Any],nota_fiscal: NotaFiscal) -> NotaFiscal:
        nf_transp = nf['nfeProc']['NFe']['infNFe'].get('transp')
        if nf_transp:
            nf_tranportadora = nf_transp['transporta']
            nota_fiscal.transporte_modalidade_frete = int(nf_transp['modFrete'])
            nota_fiscal.transporte_transportadora = Transportadora(
                                                            numero_documento = nf_tranportadora['CNPJ'],
                                                            razao_social = nf_tranportadora['xNome'],
                                                            inscricao_estadual = nf_tranportadora.get('IE'),
                                                            endereco_logradouro = nf_tranportadora['xEnder'],
                                                            endereco_municipio = nf_tranportadora['xMun'],
                                                            endereco_uf = nf_tranportadora['UF']
                                                         )
            
            nf_veiculo = nf_transp.get('veicTransp')
            if nf_veiculo:
                nota_fiscal.transporte_veiculo_placa = nf_veiculo['placa']
                nota_fiscal.transporte_veiculo_uf = nf_veiculo['UF']
                nota_fiscal.transporte_veiculo_rntc = nf_veiculo['RNTC']

            nf_reboque = nf_transp.get('reboque')
            if nf_reboque:
                nota_fiscal.transporte_reboque_placa = nf_reboque['placa']
                nota_fiscal.transporte_reboque_uf = nf_reboque['UF']
                nota_fiscal.transporte_reboque_rntc = nf_reboque['RNTC']

            nf_vol = nf_transp.get('vol')

            if nf_vol:
                volume = nota_fiscal.adicionar_transporte_volume(
                                                        quantidade = Decimal(nf_vol['qVol']),
                                                        especie = nf_vol['esp'],
                                                        marca = nf_vol.get('marca'),
                                                        numeracao = nf_vol.get('nVol'),
                                                        peso_liquido = Decimal(nf_vol['pesoL']),
                                                        peso_bruto = Decimal(nf_vol['pesoB'])
                                                    )
                

                nf_lacres = nf_vol.get('lacres')
                if nf_lacres:
                    volume.adicionar_lacre(
                                                numero_lacre = nf_lacres['nLacre']
                    )
        
        return nota_fiscal

class _SerializacaoXMLNFe400TotalDecorator(SerializacaoXMLNFe400Decorator):
    """
    Decorator que adiciona dados totais na Nota Fiscal.
    """
    @override
    def _decorate(self,nf: OrderedDict[str,Any],nota_fiscal: NotaFiscal) -> NotaFiscal:
        total = nf['nfeProc']['NFe']['infNFe']['total']['ICMSTot']
        nota_fiscal.valor_total_nota = Decimal(total['vNF'])
        nota_fiscal.totais_tributos_aproximado = Decimal(total['vTotTrib']) if total.get('vTotTrib') else 0.0
        return nota_fiscal
