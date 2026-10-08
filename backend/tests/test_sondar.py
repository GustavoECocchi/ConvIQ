import importlib.util
from pathlib import Path

CAMINHO = Path(__file__).resolve().parents[1] / "scripts" / "sondar.py"


def _carregar():
    especificacao = importlib.util.spec_from_file_location("sondar", CAMINHO)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def test_sondar_devolve_a_analise_com_recortes_literais():
    """O script de sondagem usa a composição real e valida recortes e referências."""

    resultado = _carregar().sondar("Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig.", "cliente")

    assert resultado["churn"] == "sinal_detectado"
    assert resultado["churn_evidencias"] == ["insatisfeitos com o suporte"]
    assert resultado["oportunidades"] == [["Queremos conhecer o Fluig"]]
    assert resultado["produtos"] == ["Fluig"]
    assert Path(resultado["app"]).resolve() == CAMINHO.parents[1] / "app"
    for _id, trecho, inicio, fim in resultado["evidencias"]:
        assert "Estamos insatisfeitos com o suporte. Queremos conhecer o Fluig."[inicio:fim] == trecho


def test_sondar_importa_o_app_do_proprio_checkout():
    modulo = _carregar()

    assert Path(modulo.RAIZ_BACKEND).resolve() == CAMINHO.parents[1]
    import app

    assert Path(app.__file__).resolve().parents[1] == CAMINHO.parents[1]
