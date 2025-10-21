from notas_fiscais.langchain_nf_runnables import NFe_Danfe_Runnable

import os
from dotenv import load_dotenv
load_dotenv()


def test_parsing_danfe() -> None:
    file_path = "tests/unit/resources/NFe35250401166372001127550030002655131523445210.pdf"

    llm_danfe = NFe_Danfe_Runnable()

    print(llm_danfe.invoke({"file_path":file_path}))


