---
title: Modelo de Notas Fiscais
---
classDiagram

namespace model {

    class EstrategiaExtracaoDadosNotaFiscal {
        <<Interface>>
        +extrairDados() DadosNotaFiscal
    }

    class DadosNotaFiscal {
        <<Value Object>>
        -chaveAcesso: String
        -serie: String
        -modelo: String
        -numero: Int
        -naturezaDaOperacao: String
        -dataEmissao: String
        -eventoMaisRecente: String[0..1]
        -dataHoraEventoMaisRecente: String[0..1]
        -emitente: DadosNotaFiscal.Pessoa
        -destinatario: DadosNotaFiscal.Pessoa
        -itens: DadosNotaFiscal.Item[*]
        -valorNota: Float
    }

    class DadosNotaFiscal.Item {
        <<Value Object>>
        -cfop: String
        -produto: DadosNotaFiscal.Produto
        -quantidade: Float
        -unidade: String
        -valorUnitario: Float
        -valorTotal: Float
    }


    class DadosNotaFiscal.Produto {
        <<Value Object>>
        -numero: Int
        -descricao: String
        -codigoNcm: String
        -descricaoNcm: String
    }

    class DadosNotaFiscal.Pessoa {
        <<Value Object>>
        -cpfCnpj: String
        -inscricaoEstadual: String[0..1]
        -nome: String
        -endereco: DadosNotaFiscal.Endereco
    }

    class DadosNotaFiscal.Endereco {
        <<Value Object>>
        -municipio: String
        -uf: String
    }

}

namespace nfe {

    class EstrategiaExtracaoDadosNFe {
        +extrairDados() DadosNotaFiscal
    }
}

EstrategiaExtracaoDadosNotaFiscal .. DadosNotaFiscal
EstrategiaExtracaoDadosNotaFiscal <|-- EstrategiaExtracaoDadosNFe
DadosNotaFiscal.Pessoa ..> DadosNotaFiscal.Endereco
DadosNotaFiscal *..> "*" DadosNotaFiscal.Item
DadosNotaFiscal.Item ..> DadosNotaFiscal.Produto
DadosNotaFiscal ..> DadosNotaFiscal.Pessoa

class NotaFiscal {
    <<Entity>>
    -serie: ChaveAcesso
    -valoresTotais: ValoresTotais
    -tipo: TipoNotaFiscal[0..1]
}

class TipoNotaFiscal {
    <<Enumeration>>
    NFE
    NFSE
    NFCE
    CTE
    NFA
}

class ValoresTotais {
    <<Value Object>>
    -subTotal: Float
    -frete: Float[0..1]
    -seguro: Float[0..1]
    -descontos: Float[0..1]
    -valorTotalTributos: Float
    -valorTotalDaNota: Float
}

class ItemNotaFiscal {
    << Entity>>
    - cfop : CFOP
    - numero: Integer
    - ean: EAN[0..1]
    - descricao: String[0..1]
    - quantidade: Float
    - unidade: String
    - valorUnitario: Float
    - valorTotal: Float
}

class ProdutoServico {
    <<Tributavel>>
    -ncm: NCM 
    -codigo: String
    -descricao: String
    -quantidade: Float
    -unidade: String
    -valorUnitario: Float
    -\valorTotal: Float
}

class Tributacao {
    <<Entity>>
    -valor: Float
}

NotaFiscal "1 notaFiscal" *-- "* itens" ItemNotaFiscal: contém 
NotaFiscal ..> ValoresTotais
NotaFiscal "1 notaFiscal" --* "* tributacoes" Tributacao
Tributacao "* tributacoes" *-- "1 tributo" Tributo

ItemNotaFiscal "*" --> "produtoServico" ProdutoServico: contém
NotaFiscal "*" --> "emitente" Pessoa: emitida por
NotaFiscal "*" --> "destinatario" Pessoa: emite para


class ChaveAcesso {
    <<Validavel>>
    -valor: String
}

class NCM {
    -valor: String
}

class EAN {
    -valor: String
}

Produto .. NCM

ItemNotaFiscal .. CFOP
ItemNotaFiscal .. EAN

class CFOP {
    <<Validavel>>
    - valor: String
    +validar() Boolean
}

class Pessoa {
    - tipoPessoa: TipoPessoa
    - nome: String
    - endereco: Endereco
}

Pessoa <|-- PessoaFisica
Pessoa <|-- PessoaJuridica
Pessoa .. TipoPessoa

class TipoPessoa {
    <<Enumeration>>
    PF
    PJ
}

class Endereco {
    -municipio: String
    -UF: String
}

class PessoaFisica {
    -cpf: CPF
    -nome: String
    -tipo: TipoPessoa = PF
}

PessoaFisica .. CPF

class CPF {
    <<Validavel>>
    -valor: String
    +validar: Boolean
}

class PessoaJuridica {
    -cnpj: CNPJ
    -InscricaoMunicipal: InscricaoMunicipal
    -InscricaoEstadual: InscricaoEstadual[0..1]
    -razaoSocial: String
    -tipo: TipoPessoa = PJ
    -regimeTributacao: RegimeTributacao
}

PessoaJuridica .. CNPJ
PessoaJuridica .. InscricaoMunicipal
PessoaJuridica .. InscricaoEstadual
PessoaJuridica .. RegimeTributacao

class CNPJ {
    <<Validavel>>
    -codigo: String
    +validar() Boolean
}

class InscricaoMunicipal {
    <<Validavel>>
    -codigo: String
    +validar() Boolean
}

class InscricaoEstadual {
    <<Validavel>>
    -valor: String
    -validar() Boolean
}

class RegimeTributacao {
    <<Enumeration>>
    SIMPLES_NACIONAL
    LUCRO_PRESUMIDO
    LUCRO_REAL
}

class Tributavel {
    <<Interface>>
}


class RamoAtividade {
    <<Tributavel>>
    -CNAE: String
    -descricao: String
}

RamoAtividade *-- "*" PessoaJuridica: ramoAtividade

RamoAtividade --* "*" Produto

class Tributo {
    -codigo: String
    -nome: String
    -/tipo: TipoTributo
    -tipoPessoa: TipoPessoa
    -ambito: Ambito
    -estrategiaCalculo: CalculoTributo
    +calcular()
}

class TributoFederal {
    -aliquota : Float
    -lucroPresumido: Float
}

RamoAtividade ..* "*" TributoFederal
Tributo ..* "*" TributoFederal

class Estado {
    -uf: String
    -nome: String
}

class TributoEstadual {
    -aliquotaIntraEstadual: Float
    -aliquotaInterEstadual: Float
}

Estado ..* "*" TributoEstadual
Tributo ..* "*" TributoEstadual

class Municipio {
    -codigo: String
    -nome: String
}

Estado "1" ..* "*" Municipio

class TributoMunicipal {
    -aliquota: Float
}

Municipio ..* "*" TributoMunicipal
Tributo ..* "*" TributoMunicipal

class Ambito {
    <<Enumeration>>
    MUNICIPAL
    ESTADUAL
    FEDERAL
}

Tributo .. TipoPessoa
Tributo .. Ambito

class TipoTributo {
    <<Enumeration>>
    IMPOSTO
    CONTRIBUICAO
    TAXA
}

Tributo ..> TipoTributo

class CalculoTributo {
    <<Interface>>
    +calcular(tributo: Tributo, ramoAtividade: RamoAtividade) Float
}

CalculoTributo .. Tributo
CalculoTributo .. RamoAtividade

note for CalculoTributo "Estratégia para cálculo de impostos"

