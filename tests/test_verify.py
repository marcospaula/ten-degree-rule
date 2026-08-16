import pytest

from verify import check_bias, implied_ea, ten_degree_rule_af, ten_degree_rule_implied_ea


def test_the_headline_number():
    """O achado central do README: 105 -> 40 C embute Ea = 0.707 eV."""
    ea = ten_degree_rule_implied_ea(t_rated_c=105.0, t_use_c=40.0)
    assert round(ea, 3) == 0.707


# ---- a tabela de janelas deslizantes (README secao 1) ----

@pytest.mark.parametrize("t_hot,t_cold,ea_esperado", [
    (135, 125, 0.971),
    (105, 95, 0.832),
    (85, 75, 0.745),
    (65, 55, 0.663),
    (45, 35, 0.586),
    (35, 25, 0.549),
])
def test_ea_por_janela_de_10_graus(t_hot, t_cold, ea_esperado):
    ea = implied_ea(t_hot, t_cold, af=2.0)
    assert round(ea, 3) == ea_esperado


# ---- as guardas: entrada errada tem que ser recusada, nao calculada errado ----

def test_recusa_fria_maior_que_quente():
    with pytest.raises(ValueError, match="t_hot_c must be greater"):
        implied_ea(t_hot_c=25.0, t_cold_c=105.0, af=2.0)  # trocado de propósito


def test_recusa_af_menor_ou_igual_a_1():
    with pytest.raises(ValueError, match="af must be > 1"):
        implied_ea(t_hot_c=105.0, t_cold_c=25.0, af=1.0)


def test_regra_recusa_uso_acima_do_rated():
    with pytest.raises(ValueError):
        ten_degree_rule_af(t_rated_c=40.0, t_use_c=105.0)  # invertido


# ---- a tabela de vies (README secao 3) -- o gancho do repo ----

def test_tabela_de_vies_tem_seis_linhas_uma_por_ea():
    tabela = check_bias()
    assert len(tabela) == 6


def test_no_ea_707_a_regra_e_neutra():
    tabela = check_bias()
    linha = next(r for r in tabela if r["ea_real_ev"] == 0.707)
    assert linha["rule_over_arrhenius"] == 1.0
    assert linha["verdict"] == "coincides"


def test_no_ea_05_a_regra_e_perigosamente_otimista():
    """O numero que vai na primeira linha do post: quase 4x."""
    tabela = check_bias()
    linha = next(r for r in tabela if r["ea_real_ev"] == 0.50)
    assert linha["rule_over_arrhenius"] == 3.75
    assert linha["verdict"] == "OPTIMISTIC (dangerous)"


def test_acima_de_707_a_regra_fica_conservadora():
    """Verifica a INVERSAO de direcao, nao so um numero isolado."""
    tabela = check_bias()
    altos = [r for r in tabela if r["ea_real_ev"] > 0.707]
    assert altos, "esperava pelo menos uma linha com Ea > 0.707"
    assert all(r["verdict"] == "conservative" for r in altos)
