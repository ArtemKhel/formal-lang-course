from pathlib import Path

from pyformlang.cfg import CFG, Variable, Terminal, Production


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


# if __name__ == '__main__':
#     cfg = cfg_from_file('./_cfg')
