from notas_fiscais.parsers import NotaFiscalOutputParser


def main():

    filename = "tests/unit/resources/NFe00268545277815175151874317441535876058251142.xml"

    with open(filename, 'r', encoding='utf-8') as file:
         my_xml = file.read()

    nf_parser = NotaFiscalOutputParser()

    nf = nf_parser.parse(my_xml)

    print(nf)


if __name__ == "__main__":
    main()