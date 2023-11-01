from pathlib import Path

from pyformlang.cfg import CFG, Variable, Terminal
from pyformlang.regular_expression import Regex

from project.utils.ecfg import ECFG


def cfg_from_file(p: Path | str) -> CFG:
    with open(p) as f:
        return CFG.from_text(f.read())


def cfg_to_wnf(cfg: CFG) -> CFG:
    cfg_ = cfg.eliminate_unit_productions().remove_useless_symbols()
    new_productions = cfg_._get_productions_with_only_single_terminals()
    new_productions = cfg_._decompose_productions(new_productions)
    return CFG(start_symbol=cfg_.start_symbol, productions=set(new_productions))


def cfgs_are_equivalent(cfg: CFG, cfg_: CFG):
    return (
        cfg.start_symbol == cfg.start_symbol
        and cfg.productions == cfg.productions
        and cfg.terminals == cfg.terminals
        and cfg.variables == cfg.variables
    )


def is_weak_normal_form(cfg: CFG) -> bool:
    return all(
        (len(p.body) == 2 and all(isinstance(x, Variable) for x in p.body))
        or (len(p.body) == 1 and all(isinstance(x, Terminal) for x in p.body))
        for p in cfg.productions
    )


def cfg_to_ecfg(cfg: CFG) -> ECFG:
    productions = {}
    for production in cfg.productions:
        body = Regex(" ".join(x.value for x in production.body) if production.body else "$")
        if production.head not in productions:
            productions[production.head] = body
        else:
            productions[production.head] = productions[production.head].union(body)
    return ECFG(
        variables=set(cfg.variables),
        productions=productions,
        terminals=set(cfg.terminals),
        start_symbol=cfg.start_symbol,
    )
