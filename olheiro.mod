/***
### Otimizador de Escalação para o Cartola FC
###    por André Lima
###
***/

/*** Conjuntos do modelo matemático ***/

set S_Jogadores;
set S_Posicoes;
set S_Formacoes;


/*** Parâmetros auxiliares ***/

param P_Patrimonio, >= 0;


/*** Parâmetros do Jogador ***/

param P_Preco{JOGADOR in S_Jogadores}, >= 0;
param P_Media{JOGADOR in S_Jogadores};
param Pe_Posicao{JOGADOR in S_Jogadores} symbolic in S_Posicoes;


/*** Parâmetros da Formação ***/
param P_Quantidade{FORMACAO in S_Formacoes, POSICAO in S_Posicoes}, integer, >= 0;


/*** Variáveis ***/

var V_Seleciona{JOGADOR in S_Jogadores}, binary;
var V_Esquema{FORMACAO in S_Formacoes}, binary;


/*** Restrições ***/

C_Patrimonio:
  (sum{JOGADOR in S_Jogadores} P_Preco[JOGADOR] * V_Seleciona[JOGADOR])
  <= P_Patrimonio;

C_UmaUnicaFormacao:
  (sum{FORMACAO in S_Formacoes} V_Esquema[FORMACAO]) == 1;

C_QuantPosFormacao{POSICAO in S_Posicoes}:
  (sum{JOGADOR in S_Jogadores : Pe_Posicao[JOGADOR] == POSICAO} V_Seleciona[JOGADOR])
  == (sum{FORMACAO in S_Formacoes} P_Quantidade[FORMACAO, POSICAO] * V_Esquema[FORMACAO]);

/*** Função Objetivo ***/

/* maximiza o total de ordens atendidas */
maximize z : (sum{JOGADOR in S_Jogadores} P_Media[JOGADOR] * V_Seleciona[JOGADOR]);

/*** Execução ***/

solve;

printf "Resultado da otimizacao:\n";

for {FORMACAO in S_Formacoes : V_Esquema[FORMACAO]} {
  printf "Formacao utilizada: %s\n", FORMACAO;
}

for {JOGADOR in S_Jogadores : V_Seleciona[JOGADOR]} {
  printf "%s - %s - %.2f - %.2f\n", Pe_Posicao[JOGADOR], JOGADOR, P_Preco[JOGADOR], P_Media[JOGADOR];
}

printf "Custo da selecao: %.2f\n", (sum{JOGADOR in S_Jogadores} P_Preco[JOGADOR] * V_Seleciona[JOGADOR]);
printf "Media da selecao: %.2f\n", (sum{JOGADOR in S_Jogadores} P_Media[JOGADOR] * V_Seleciona[JOGADOR]);

end;
