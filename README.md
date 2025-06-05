
# chat-commerce

**chat-commerce** é uma aplicação Python para busca inteligente e conversação natural sobre catálogos de produtos, integrando IA generativa, embeddings, re-ranking neural e banco vetorial. Com uma API conversacional pronta para integração, a aplicação permite experiências avançadas de busca, recomendação e atendimento via chat para plataformas de e-commerce.

---

## Motivação

O projeto demonstra uma arquitetura moderna para busca semântica conversacional, onde usuários encontram produtos de maneira natural e precisa, combinando vetorização, reconhecimento dinâmico de entidades, busca híbrida (texto e vetores), filtros estruturados e re-ranking factual.

---

## Como funciona?

### 1. Pipeline de Ingestão e Indexação

- **Extração:** Lê produtos do [Google Shopping Dataset](https://www.kaggle.com/datasets/amulyas/google-shopping-dataset?resource=download).
- **Limpeza e Normalização:** Processa e corrige campos brutos do CSV.
- **Vetorização:** Gera embeddings dos campos textuais relevantes (`product_details`, fallback para `description` ou `product_name`) usando OpenAI Embeddings.
- **Indexação:** Insere os vetores e payloads normalizados no Qdrant, com índices textuais configurados (para buscas híbridas e full-text).

### 2. API Conversacional

- **Reconhecimento de Entidades:** Utiliza LLMs (GPT-4x) para extrair dinamicamente do texto do usuário os campos e valores mais relevantes para busca (`product_name`, `product_details`, `description`, `search_keyword` etc).
- **Busca Híbrida:** Faz uma busca vetorial no Qdrant combinada com filtros textuais precisos. Usa embeddings para semântica e índices textuais para full-text, aproveitando ao máximo as capacidades do banco.
- **Re-Rank Neural:** Passa os resultados pelo modelo GPT, que reordena, filtra e valida os produtos retornados, entregando uma resposta factual, organizada e de alta relevância ao usuário final.
- **Streaming:** A resposta final é entregue em streaming, permitindo integrações conversacionais fluidas.

---

## Principais Componentes

- `src/domain/product.py`  
  Modelos Pydantic para entidade de produto, payload e vetores.
- `src/core/pipeline/process_index.py`  
  Pipeline ETL: ingestão, limpeza, vetorização e indexação dos dados no Qdrant.
- `src/adapter/database/qdrant/driver.py`  
  Abstração para comunicação síncrona e assíncrona com o banco Qdrant, criação de coleções e índices textuais.
- `src/adapter/service/openai/client.py`  
  Cliente assíncrono para OpenAI (embeddings, completions, streaming).
- `src/core/api/business.py`  
  Orquestra a extração dinâmica de entidades, busca híbrida, rerank neural e resposta streaming.
- `src/core/api/app.py`  
  Instancia e publica a API FastAPI, incluindo o roteamento.

---

## Exemplo de Uso

1. **Ingestão dos produtos**
   ```bash
   python src/core/pipeline/process_index.py
   ```
2. **Suba a API conversacional**
   ```bash
   uvicorn src.core.api.app:api --factory --reload
   ```
3. **Exemplo de requisição:**
   ```bash
   curl -X POST http://localhost:8000/chat \
        -H "Content-Type: application/json" \
        -d '{"query_text": "Quero perfumes femininos até 200 reais com notas florais"}'
   ```

---

## Diferenciais Técnicos

- Reconhecimento dinâmico e automático dos campos do payload (código sempre atualizado com os modelos).
- Pipeline desacoplada, assíncrona, robusta para ingestão e atualização dos dados.
- Busca híbrida, combinando filtros textuais e vetoriais de alta performance.
- Neural re-rank em duas etapas para máxima factualidade e contexto real na resposta.
- Arquitetura pronta para expansão (novos campos, novos providers de LLM ou banco vetorial).

---

## Dados

O dataset utilizado é o Google Shopping Dataset (Kaggle):  
https://www.kaggle.com/datasets/amulyas/google-shopping-dataset?resource=download

---

## Como contribuir

Sinta-se à vontade para abrir issues, enviar sugestões ou Pull Requests!

---
