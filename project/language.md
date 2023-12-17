## Абстрактный синтаксис

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    String of string
  | Int of int
  | Bool of bool

expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | And of expr * expr           // логическое и
  | Or expr * expr               // логическое или
  | Not of expr                  // логическое отрицание
  | Set of List<expr>            // множество
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход
  | Contains of expr * expr      // проверить вхождение элемента в множество

lambda =
    Lambda of List<var> * expr
```

## Грамматика
```
program -> (statement ';' | comment)*

comment -> '#' [^\n]*

statement ->
    id '=' expr
    | 'print' '(' expr ')'

id -> [a-zA-Z][_a-zA-Z0-9]*

expr ->
    id
  | constant
  | set
  | lambda
  | 'map' '(' lambda ',' expr ')'
  | 'filter' '(' lambda ',' expr ')'
  | expr 'and' expr
  | expr 'or' expr
  | 'not' expr
  | expr '&' expr  // пересечение
  | expr '.' expr  // конкатенайия
  | expr '|' expr  // обЬединение
  | expr '*'       // звезда Клини
  | expr 'in' expr
  | 'set_start' '(' expr ',' expr ')'
  | 'set_final' '(' expr ',' expr ')'
  | 'add_start' '(' expr ',' expr ')'
  | 'add_final' '(' expr ',' expr ')'
  | 'get_start' '(' expr ')'
  | 'get_final' '(' expr ')'
  | 'get_reachable' '(' expr ')'
  | 'get_vertices' '(' expr ')'
  | 'get_edges' '(' expr ')'
  | 'get_labels' '(' expr ')'
  | 'load' '(' string ')'
  | '(' expr ')'

constant ->
    string
  | int
  | bool

set ->  '{' (expr (',' expr)*)? '}'
list<T> ->  '[' (T (',' T)*)? ']'

lambda ->  '{' pattern '->' expr '}'

pattern ->
    '_'
    | id
    | list<pattern>

string -> '"' .*? '"'
int -> '-'? [0-9]+
bool -> 'true' | 'false'

```
## Пример

```
g = load("graph_name");
g = set_start(g, {0, 1, 2});
g = set_finals(g, get_vertices(g));

q = ("a" | "b") . "c" *

res = g & q

res = filter(
    lambda label -> label in {"one", "two", "three"},
    map(
        lambda [_, label, _] -> label,
        get_edges(res)
    )
);

print(res)
```
