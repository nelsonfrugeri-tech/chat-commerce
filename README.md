# Chat-Commerce: Sistema de Busca Inteligente para E-commerce

## Visão Geral
Este projeto implementa um sistema de busca inteligente usando IA generativa e banco de dados vetorial, permitindo buscas semânticas e precisas sobre produtos de e-commerce. A aplicação utiliza modelos GPT da OpenAI para reconhecimento de entidades, vetorização de textos e reordenação de resultados, fornecendo respostas relevantes e precisas.

## Fonte de Dados
O projeto utiliza a base disponibilizada no Kaggle:

- [Google Shopping Dataset](https://www.kaggle.com/datasets/amulyas/google-shopping-dataset?resource=download)


## Componentes Principais
- **Banco de dados vetorial**: Qdrant
- **IA generativa**: GPT (OpenAI)
- **Linguagem**: Python com FastAPI e Pydantic para modelagem de dados

## Configuração Inicial

### Instalação de Dependências
```bash
pip install -r requirements.txt
