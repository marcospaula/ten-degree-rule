import pytest

from verify import (
    check_bias, check_ea_sensitivity, check_published_ea, implied_ea,
    ten_degree_rule_af, ten_degree_rule_implied_ea,
)


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


def test_no_ea_707_o_resultado_e_TAUTOLOGICO_nao_validacao():
    """1.00x aqui nao valida nada: compara a regra contra Arrhenius carregando
    o Ea que a propria regra embute. O veredito registra isso no nome."""
    tabela = check_bias()
    linha = next(r for r in tabela if r["ea_real_ev"] == 0.707)
    assert linha["rule_over_arrhenius"] == 1.0
    assert linha["verdict"] == "tautological"


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


# ---- os Ea PUBLICADOS (README secao 5) -- a comparacao que nao e circular ----
# ATENCAO: so 1 das 6 linhas mede o MESMO componente da regra (eletrolitico
# de aluminio liquido). As outras 5 sao tecnologia vizinha (polimero). Ver o
# corolario "por que estamos misturando populacoes" em auditar-como-fellow.

def test_so_uma_linha_e_o_alvo_real_da_regra():
    """A distincao de tecnologia e o achado desta rodada de auditoria: nao e
    '6 estimativas da mesma incerteza', e 1 ponto confirmado + 5 de outra
    tecnologia. Nenhuma funcao pode apagar essa distincao."""
    tabela = check_published_ea()
    alvo = [r for r in tabela if r["is_rule_target"]]
    assert len(alvo) == 1
    assert alvo[0]["ea_ev"] == 0.68
    assert alvo[0]["technology"] == "liquid aluminum electrolytic"


def test_contra_o_unico_ea_do_mesmo_componente_a_regra_e_19pct_otimista():
    """Contra o 0.68 eV que a NASA enuncia PARA O MESMO COMPONENTE da regra,
    ela nao coincide: erra 1.19x. Esta e a comparacao que sustenta o post."""
    linha = next(r for r in check_published_ea() if r["is_rule_target"])
    assert linha["rule_over_real"] == 1.19
    assert linha["direction"] == "optimistic"


def test_tecnologia_vizinha_atravessa_a_neutralidade():
    """O achado sobre TRANSFERIR a regra entre tecnologias (nao sobre a
    incerteza intrinseca do proprio alvo): entre alumino/tantalo polimero,
    o erro vai de 2.4x otimista a 0.13x conservadora."""
    vizinhas = [r for r in check_published_ea() if not r["is_rule_target"]]
    assert len(vizinhas) == 5
    razoes = [r["rule_over_real"] for r in vizinhas]
    assert max(razoes) == 2.40
    assert min(razoes) == 0.13
    assert any(r > 1 for r in razoes) and any(r < 1 for r in razoes), \
        "a faixa tem que cruzar 1.0, senao o argumento da direcao cai"


def test_toda_linha_publicada_tem_fonte_e_tecnologia():
    """Nenhum Ea entra na tabela sem procedencia declarada E sem tecnologia
    explicita -- e a tecnologia que faltava antes desta correcao."""
    tabela = check_published_ea()
    assert all(r["source"].strip() for r in tabela)
    assert all(r["technology"].strip() for r in tabela)


def test_4pct_em_ea_vira_19pct_em_horas():
    """A demonstracao mais barata de que Ea nao e detalhe."""
    s = check_ea_sensitivity()
    assert s["disagreement_in_ea_pct"] == 4.0
    assert s["disagreement_in_hours_pct"] == 19.0


# ---- KELVIN: o erro classico de Arrhenius, travado por teste ----

def test_arrhenius_usa_kelvin_e_nao_celsius():
    """O erro mais comum em Arrhenius e passar Celsius onde vai Kelvin.

    Conferencia a mao (105 -> 40 C):
        1/313,15 - 1/378,15 = 5,4890e-4  1/K
        Ea = k * ln(2^6,5) / 5,4890e-4   = 0,7073 eV
    Se alguem remover a conversao, 1/40 - 1/105 = 1,5476e-2 e o Ea despenca
    para 0,025 eV -- 28x menor, e fora de qualquer faixa fisica real.
    """
    ea = ten_degree_rule_implied_ea(t_rated_c=105.0, t_use_c=40.0)
    assert round(ea, 4) == 0.7073, "o valor mudou: a conversao para Kelvin caiu?"
    assert ea > 0.1, "Ea abaixo de 0,1 eV = quase certamente Celsius passado como Kelvin"


def test_ea_implicito_cai_na_faixa_fisicamente_plausivel():
    """Guarda de sanidade fisica, nao de aritmetica: mecanismo de falha real
    fica entre ~0,3 e ~1,5 eV. Fora disso, o erro e de unidade, nao de modelo."""
    for t_hot in range(135, 25, -10):
        ea = implied_ea(t_hot, t_hot - 10, af=2.0)
        assert 0.3 < ea < 1.5, f"janela {t_hot}->{t_hot-10} deu Ea={ea:.4f} eV, implausivel"


def test_a_regra_em_si_usa_DIFERENCA_de_temperatura():
    """A regra pode usar Celsius, e esta certo: diferenca de temperatura e
    identica nas duas escalas, porque o offset de 273,15 cancela."""
    af_celsius = ten_degree_rule_af(t_rated_c=105.0, t_use_c=40.0)
    af_kelvin_equivalente = 2.0 ** (((105 + 273.15) - (40 + 273.15)) / 10.0)
    assert af_celsius == pytest.approx(af_kelvin_equivalente)
