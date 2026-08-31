# 🚜 Diário de Bordo — Custo de Maquinário Agrícola

<p align="center">
  <img src="https://img.shields.io/badge/IFRO-Campus%20Ariquemes-00875F?style=for-the-badge&logo=google-academic&logoColor=white" alt="IFRO">
  <img src="https://img.shields.io/badge/Curso-Técnico%20em%20Informática-0052CC?style=for-the-badge&logo=codeforces&logoColor=white" alt="Curso">
  <img src="https://img.shields.io/badge/Turma-3º%20Ano%20B-7952B3?style=for-the-badge" alt="Turma">
  <img src="https://img.shields.io/badge/Ano-2026-orange?style=for-the-badge" alt="Ano">
</p>

> **Sistema de Gestão e Controle Operacional de Maquinário Agrícola.**  
> Solução digital para controle diário do uso de máquinas, registro do horímetro acumulado e gestão de custos no campo.

---

## 📌 Sobre o Projeto

O **Diário de Bordo - Custo de Maquinário** substitui apontamentos manuais por um fluxo digital integrado. O sistema monitora as horas operadas por máquina agrícola, permitindo o acompanhamento preciso do tempo de uso e facilitando o cálculo de custos e manutenções.

---

## 📐 Diagrama de Sequência (Fluxo do Registro de Horímetro)

O diagrama abaixo descreve a interação contínua entre o **Usuário**, a aplicação (**Sistema Agro**) e o **Banco de Dados** durante o processo de seleção da máquina e lançamento do horímetro diário:

```plantuml
@startuml
autonumber
actor "Usuário" as user
participant "Sistema Agro" as sys
database "Banco de Dados" as db

user -> sys : Seleciona a máquina
sys -> db : Busca dados da máquina e último horímetro
db --> sys : Retorna dados
sys --> user : Exibe formulário com horímetro atual

user -> sys : Informa horas trabalhadas no dia (horímetro atual)
sys -> db : Salva registro diário e atualiza total acumulado
db --> sys : Confirmação de salvamento

sys --> user : Exibe confirmação e total de horas acumuladas

@umlend
