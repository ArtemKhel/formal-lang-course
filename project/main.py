from project.utils.graphs import *
from project.utils.rpq import *


def main():
    s = '(a|b)*.b.c*'
    ss = 'a*.(a|b).c'
    n = regex_to_dfa(s)
    nn = regex_to_dfa(ss)

    # r = Regex('(a|b)*.b.c*')
    # rr = Regex('a*.(a|b).c')
    # n = r.to_epsilon_nfa().remove_epsilon_transitions()
    # nn = rr.to_epsilon_nfa().remove_epsilon_transitions()

    save_graph_as_dot(n.to_deterministic().minimize().to_networkx(), './_r.dot')
    save_graph_as_dot(nn.to_deterministic().minimize().to_networkx(), './_rr.dot')

    # inter = intersect_nfa(one, two)
    inter = intersect_nfa(n, nn).to_nfa()

    save_graph_as_dot(inter.to_networkx(), './_inter.dot')
    save_graph_as_dot(inter.minimize().to_networkx(), './_inter_min.dot')
    pass


if __name__ == '__main__':
    main()
