

Aqui está a documentação técnica final, focada na integração com a nuvem:
📑 Referência de API: Módulo de Uploads (Cloudinary)

Este módulo gerencia o armazenamento de arquivos binários (imagens) em um serviço de Terceiros (SaaS), garantindo que o banco de dados PostgreSQL armazene apenas as referências (URLs), mantendo o sistema leve e escalável.
🗄️ Infraestrutura de Nuvem (RNF 03)

O sistema utiliza a API do Cloudinary para o processamento e entrega de mídia.

    Segurança de Tráfego: Configurado com secure=True para garantir que todas as URLs geradas utilizem o protocolo HTTPS.

    Otimização Automática: Utiliza os parâmetros quality="auto" e fetch_format="auto" para entregar a imagem no formato mais leve possível (como WebP), economizando dados móveis do usuário no App Expo.

🚀 Endpoints de Mídia (/uploads)
1. Upload de Imagem Seguro

    Rota: POST /uploads/image

    Entrada: file (Multipart/form-data) e folder (opcional).

    Requisito: Dependência get_current_user. Apenas usuários autenticados podem consumir o seu bucket na nuvem.

    Processamento:

        Validação de Extensão: Filtra arquivos para aceitar apenas formatos de imagem (jpg, png, webp).

        Organização em Pastas: Os arquivos são salvos no caminho smart_forms/{folder} para facilitar a gestão no painel do Cloudinary.

        Rastreabilidade (Tags): Cada imagem recebe uma tag com o ID do usuário (user_{id}), permitindo auditoria de quem enviou o quê diretamente no storage.

    Resposta: Retorna a secure_url, que deve ser salva no campo formData da submissão ou no logoUrl do projeto.

🔐 Regras de Validação e Segurança
Regra	Implementação	Motivo
Whitelisting	allowed_extensions	Impede o upload de scripts maliciosos ou arquivos pesados não suportados.
Proteção de Custo	Depends(get_current_user)	Evita que robôs ou usuários anônimos usem sua quota de upload do Cloudinary.
Abstração de Arquivo	file.file	O FastAPI lê o fluxo de bytes sem precisar salvar o arquivo temporariamente no disco do servidor, aumentando a performance.