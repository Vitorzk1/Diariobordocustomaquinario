# Diário de Bordo — Integração Total

Aplicação web Flask para gerenciamento de máquinas agrícolas, horímetro, abastecimentos, custos de combustível, checklist de manutenção e usuários.

## Estrutura

- `app.py`: rotas Flask, modelos SQLAlchemy, login e regras de acesso.
- `templates/`: páginas HTML renderizadas com Jinja2.
- `static/style.css`: estilos da interface.
- `requirements.txt`: dependências Python.
- `diagramas/`: fluxograma, modelo de dados e diagramas C4 de contexto e container.

## Executar no Windows / VS Code

1. Instale Python 3.11 ou mais recente compatível com as dependências.
2. Abra esta pasta no VS Code e abra o terminal.
3. Crie e ative um ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Se usar CMD, ative com `venv\Scripts\activate.bat`.

4. Instale as dependências e inicie a aplicação:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

5. Acesse http://127.0.0.1:5000.

## Conta administrativa inicial

Na primeira inicialização, o aplicativo cria um administrador inicial, caso não exista:

- E-mail: `admin@email.com`
- Senha inicial: `admin123`

Entre e altere a senha antes de disponibilizar o sistema publicamente. Configure uma `SECRET_KEY` forte por variável de ambiente em produção. Não use o servidor de desenvolvimento Flask para hospedar o site publicamente.

## Banco de dados

O projeto usa SQLite e `db.create_all()` para criar as tabelas. O banco é criado no ambiente em que a aplicação roda; o banco local não é automaticamente transferido para o PythonAnywhere. Faça backup dos dados antes de migrações ou alterações de estrutura.

## Publicação no PythonAnywhere

1. Envie o projeto ao GitHub.
2. Clone o repositório no console Bash do PythonAnywhere.
3. Crie um virtualenv e instale `requirements.txt`.
4. Configure o WSGI para importar `app` como `application`.
5. Configure `/static/` para apontar para a pasta `static` e recarregue a aplicação.

Consulte a documentação do PythonAnywhere para os passos atualizados: https://help.pythonanywhere.com/pages/Flask/

## Diagramas

Veja os arquivos Mermaid em `diagramas/`. Eles descrevem o fluxo principal, os modelos existentes no `app.py` e os diagramas C4 de contexto e container.

## Segurança

- O administrador inicial usa uma senha conhecida: troque-a imediatamente.
- Defina `SECRET_KEY` por variável de ambiente antes da publicação.
- Revise regras de autorização e validação de dados antes de uso real.
