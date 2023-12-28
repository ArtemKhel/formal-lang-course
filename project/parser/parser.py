from pathlib import Path

import pydot

from project.parser.antlr.LanguageListener import LanguageListener
from project.parser.antlr.LanguageParser import LanguageParser
from project.parser.antlr.LanguageLexer import LanguageLexer
from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker, ParserRuleContext, TerminalNode


class DotListener(LanguageListener):
    def __init__(self):
        self.dot = pydot.Dot(strict=True)
        self._curr = 0
        self._stack = []

    def enterEveryRule(self, ctx: ParserRuleContext):
        self.dot.add_node(pydot.Node(self._curr, label=LanguageParser.ruleNames[ctx.getRuleIndex()]))
        if len(self._stack) > 0:
            self.dot.add_edge(pydot.Edge(self._stack[-1], self._curr))
        self._stack.append(self._curr)
        self._curr += 1

    def exitEveryRule(self, ctx: ParserRuleContext):
        self._stack.pop()

    def visitTerminal(self, node: TerminalNode):
        self.dot.add_node(pydot.Node(self._curr, label=f'{node}'))
        self.dot.add_edge(pydot.Edge(self._stack[-1], self._curr))
        self._curr += 1


def save_to_dot(parser: LanguageParser, file: str | Path) -> None:
    if parser.getNumberOfSyntaxErrors() > 0:
        raise SyntaxError()

    listener = DotListener()
    ParseTreeWalker().walk(listener, parser.program())
    listener.dot.write(file)


def parse(code: str) -> LanguageParser:
    return LanguageParser(CommonTokenStream(LanguageLexer(InputStream(code))))


def check_correctness(code: str) -> bool:
    parser = parse(code)
    parser.removeErrorListeners()
    parser.program()
    return parser.getNumberOfSyntaxErrors() == 0
