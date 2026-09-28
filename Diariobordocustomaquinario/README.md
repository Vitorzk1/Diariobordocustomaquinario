# 🚜 Diário de Bordo — Custo de Maquinário Agrícola

<p align="center">
  <img src="https://img.shields.io/badge/IFRO-Campus%20Ariquemes-00875F?style=for-the-badge&logo=google-academic&logoColor=white" alt="IFRO">
  <img src="https://img.shields.io/badge/Curso-Técnico%20em%20Informática-0052CC?style=for-the-badge&logo=codeforces&logoColor=white" alt="Curso">
  <img src="https://img.shields.io/badge/Turma-3º%20Ano%20B-7952B3?style=for-the-badge" alt="Turma">
  <img src="https://img.shields.io/badge/Ano-2026-orange?style=for-the-badge" alt="Ano">
</p>

> **Sistema de Gestão e Controle Operacional de Maquinário Agrícola.**  
> Uma solução digital projetada para substituir cadernos de campo e planilhas manuais, automatizando o controle de horas de trabalho, consumo de combustível e manutenção preventiva de frotas agrícolas.

---

## 📋 Sumário
- [Sobre o Projeto](#-sobre-o-projeto)
- [Problema vs. Solução](#-problema-vs-solução)
- [Principais Funcionalidades](#-principais-funcionalidades)
- [Modelagem do Sistema (UML)](#-modelagem-do-sistema-uml)
- [Casos de Teste & Qualidade](#-casos-de-teste--qualidade)
- [Arquitetura & Tecnologias](#-arquitetura--tecnologias)
- [Como Executar o Projeto](#-como-executar-o-projeto)
- [Equipe de Desenvolvimento](#-equipe-de-desenvolvimento)

---

## 📌 Sobre o Projeto

No agronegócio moderno, a gestão eficiente do maquinário é um fator determinante para a lucratividade. O **Diário de Bordo** foi idealizado para registrar com precisão o ciclo de vida operacional de tratores, colheitadeiras e implementos, fornecendo ao produtor rural dados confiáveis para tomada de decisão e cálculo de custo/hora.

### 💡 Problema vs. Solução

| Desafio Atual (Manual) | Solução Diário de Bordo |
| :--- | :--- |
| Anotações em papel sujeitas a perda ou rasuras | Registros digitais centralizados e seguros |
| Falta de controle sobre o horímetro acumulado | Cálculo automático de horas trabalhadas por máquina |
| Manutenções realizadas apenas após quebras | Alertas e agendamento de manutenção preventiva |
| Dificuldade para apurar o custo exato da hora/máquina | Relatórios consolidados de custos e consumo |

---

## 🚀 Principais Funcionalidades

- [x] **Cadastro e Gestão de Frota:** Registro detalhado de máquinas, modelos, placas e horímetro inicial.
- [x] **Apontamento Diário de Horímetro:** Lançamento das horas trabalhadas por operador ao final de cada jornada.
- [x] **Gestão de Abastecimento:** Controle de consumo de combustível e cálculo de eficiência (L/h).
- [x] **Plano de Manutenção Preventiva:** Registro de trocas de óleo, filtros e revisões periódicas.
- [x] **Relatórios Operacionais:** Visualização clara do total de horas acumuladas e despesas operacionais.

---


## 🧪 Casos de Teste & Qualidade

Para garantir a confiabilidade do sistema, a aplicação conta com cenários de teste estruturados baseados nos critérios de aceitação:

| ID | Cenário | Ação | Resultado Esperado |
| :---: | :--- | :--- | :--- |
| **CT-01** | Cadastro de Máquina | Inserir nome, modelo e horímetro inicial | Máquina salva e disponível no sistema |
| **CT-02** | Registro Diário de Horas | Selecionar máquina e lançar horímetro atual | Registro gravado e total atualizado |
| **CT-03** | Cálculo de Horas Acumuladas | Consultar painel da máquina | Soma automática de todos os registros diários |
| **CT-04** | Validação de Entrada | Inserir valores de horas negativos ou texto | Bloqueio imediato com aviso de erro |

---

## 💻 Como Executar o Projeto

```bash
# 1. Clocar o repositório
git clone https://github.com/seu-usuario/Diariobordocustomaquinario.git

# 2. Entrar na pasta do projeto
cd Diariobordocustomaquinario

# 3. Instalar as dependências
npm install

# 4. Iniciar a aplicação
npm start
```

---

## 👥 Equipe de Desenvolvimento

Projeto desenvolvido pelos estudantes da turma do **3º Ano B (Curso Técnico em Informática)** do **Instituto Federal de Rondônia (IFRO) — Campus Ariquemes** (Ano letivo: 2026).

---

<p align="center">
  <b>IFRO Campus Ariquemes • 2026</b>
</p>
