Chat-Commerce: Sistema de Busca Inteligente para E-commerce

Visão Geral

Este projeto implementa um sistema de busca inteligente utilizando IA generativa e banco de dados vetorial, permitindo buscas semânticas e precisas sobre produtos de e-commerce. A aplicação utiliza o modelo GPT da OpenAI para reconhecimento de entidades, vetorização dos textos e reordenação dos resultados, proporcionando respostas relevantes e precisas.

Fonte dos Dados

A aplicação utiliza a base de dados disponibilizada no Kaggle:

Google Shopping Dataset

Estrutura do Projeto

.
├── src
│   ├── adapter
│   │   ├── database
│   │   │   └── qdrant
│   │   └── service
│   │       └── openai
│   ├── core
│   │   ├── api
│   │   └── pipeline
│   └── domain
│       └── product.py

Componentes Principais

Banco de dados vetorial: Qdrant.

IA generativa: GPT (OpenAI).

Linguagem: Python com Pydantic para modelagem de dados.

Configuração Inicial

Dependências

Instale as dependências usando pip:

pip install -r requirements.txt

Configuração das Variáveis de Ambiente

Crie um arquivo .env e configure as chaves necessárias:

OPENAI_API_KEY=your_openai_key
QDRANT_HOST=your_qdrant_host
QDRANT_API_KEY=your_qdrant_key

Execução do Projeto

Inicie o servidor com:

uvicorn src.main:app --reload

Uso da API

Faça requisições POST para o endpoint /chat com o seguinte payload:

{
  "query_text": "busca que deseja realizar"
}

A API retornará resultados relevantes e validados semanticamente.

Desenvolvimento e Customização

Entidades do domínio são definidas em src/domain/product.py.

Logica de negócio principal está disponível em src/core/api/business.py.

Como contribuir

Sinta-se à vontade para abrir issues e enviar pull requests com melhorias ou sugestões.

