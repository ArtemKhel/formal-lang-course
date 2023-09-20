from project.utils.graphs import *
from project.utils.rpq import *


def main():
    expected = NondeterministicFiniteAutomaton()
    expected.add_start_state(0)
    expected.add_final_state(4)
    expected.add_transition(0, 'a', 0)
    expected.add_transition(0, 'a', 1)
    expected.add_transition(0, 'b', 1)
    expected.add_transition(0, 'b', 3)
    expected.add_transition(3, 'c', 4)
    one = NondeterministicFiniteAutomaton()
    one.add_start_state(0)
    one.add_final_state(1)
    one.add_transition(0, 'a', 0)
    one.add_transition(0, 'b', 0)
    one.add_transition(0, 'b', 1)
    one.add_transition(1, 'c', 1)
    two = NondeterministicFiniteAutomaton()
    two.add_start_state(0)
    two.add_final_state(2)
    two.add_transition(0, 'a', 0)
    two.add_transition(0, 'a', 1)
    two.add_transition(0, 'b', 1)
    two.add_transition(1, 'c', 2)

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
    res = rpq(one.to_networkx(), ss, {0}, {1})

    save_graph_as_dot(inter.to_networkx(), './_inter.dot')
    save_graph_as_dot(inter.minimize().to_networkx(), './_inter_min.dot')

    # assert not inter.accepts(['a'])
    # assert inter.accepts(['b'])
    # assert inter.accepts(['a','b'])
    assert inter.is_equivalent_to(expected)
    print('YAY')

    pass


if __name__ == '__main__':
    main()
