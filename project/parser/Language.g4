grammar Language;

program : (statement SEMI EOL? | COMMENT)* EOF;

statement :
    | ID '=' expr
    | 'print' LPAREN expr RPAREN
    ;

ID : [a-zA-Z][_a-zA-Z0-9]*;

expr :
    ID
  | constant
  | set
  | lambda
  | 'map' LPAREN lambda ',' expr RPAREN
  | 'filter' LPAREN lambda ',' expr RPAREN
  | expr 'and' expr
  | expr 'or' expr
  | 'not' expr
  | expr '&' expr  // пересечение
  | expr '.' expr  // конкатенайия
  | expr '|' expr  // объединение
  | expr '*'       // звезда Клини
  | expr 'in' expr
  | 'set_start' LPAREN expr ',' expr RPAREN
  | 'set_final' LPAREN expr ',' expr RPAREN
  | 'add_start' LPAREN expr ',' expr RPAREN
  | 'add_final' LPAREN expr ',' expr RPAREN
  | 'get_start' LPAREN expr RPAREN
  | 'get_final' LPAREN expr RPAREN
  | 'get_reachable' LPAREN expr RPAREN
  | 'get_vertices' LPAREN expr RPAREN
  | 'get_edges' LPAREN expr RPAREN
  | 'get_labels' LPAREN expr RPAREN
  | 'load' LPAREN STRING RPAREN
  | LPAREN expr RPAREN
  ;

constant :
    STRING
  | INT
  | BOOL
  ;

set :  LCURLY (expr (',' expr)*)? RCURLY;

list :  LSQUARE (expr (',' expr)*)? RSQUARE;

lambda :  LCURLY pattern '->' expr RCURLY;
pat_list :  LSQUARE (pattern (',' pattern)*)? RSQUARE;
pattern :
    '_'
    | ID
    | pat_list
    ;

STRING : '"' .*? '"';
INT : '-'? [0-9]+;
BOOL : 'true' | 'false';

SEMI : ';';
LPAREN : '(';
RPAREN : ')';
LSQUARE : '[';
RSQUARE : ']';
LCURLY : '{';
RCURLY : '}';

WS : [ \t\n] -> skip;
COMMENT : '#' ~[\n]* [\n];
EOL : '\n';
