# Diagramas do projeto

Os arquivos `.mmd` são diagramas Mermaid. O GitHub costuma renderizar Mermaid em arquivos Markdown; para editar/visualizar, cole o conteúdo em https://mermaid.live.

- `01-fluxograma-sistema.mmd`: fluxo geral de autenticação e funcionalidades.
- `02-modelo-banco-dados.mmd`: entidades e relacionamentos conforme os modelos SQLAlchemy de `app.py`.
- `03-c4-contexto.mmd`: usuários e sistema no contexto externo.
- `04-c4-container.mmd`: aplicação Flask, interface Jinja2/HTML/CSS, arquivos estáticos e SQLite.

Nota: o diagrama C4 representa containers de software (componentes executáveis/deploy), não containers Docker. O projeto não foi convertido para Docker, pois o pedido selecionado foi o diagrama C4 Container.
