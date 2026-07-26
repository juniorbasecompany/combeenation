# ComBEEnation

Site institucional estático da ComBEEnation (remoção humana de abelhas e mel local no South Florida).

## Deploy no Railway

O repositório já está preparado para deploy estático via **Railpack** (`index.html` + `Staticfile`).

### 1. Publicar o código

Faça push da branch `main` para o GitHub:

```bash
git push -u origin main
```

### 2. Criar o projeto no Railway

1. Abra [railway.com/new](https://railway.com/new)
2. Escolha **Deploy from GitHub repo**
3. Selecione o repositório `combeenation`
4. Aguarde o build — o Railpack detecta o site estático e sobe o Caddy automaticamente

### 3. Expor a URL pública

1. No serviço, abra **Settings → Networking**
2. Clique em **Generate Domain** (ou adicione um **Custom Domain**)
3. Pronto: o site responde em `https://…up.railway.app`

### O que não vai para o deploy

A pasta `docs/` e arquivos internos ficam fora do upload (ver `.railwayignore`), para não publicar dossiês, transcrições e orçamentos.

### Arquivos de configuração

| Arquivo | Função |
| --- | --- |
| `Staticfile` | Marca o projeto como site estático e define a raiz servida |
| `railway.toml` | Builder Railpack, healthcheck `/health` e watch patterns |
| `.railwayignore` | Exclui material interno do upload de build |

Não é necessário `package.json`, Dockerfile nem comando de start manual.
## Estrutura do site

| Caminho | Conteúdo |
| --- | --- |
| `index.html` | Estrutura semântica da página |
| `assets/css/styles.css` | Estilos, animações e regras responsivas |
| `assets/js/translations.js` | Dicionários de tradução |
| `assets/js/app.js` | Navegação, idioma, formulário e interações |
| `assets/images/` | Imagens otimizadas usadas pelo site |
