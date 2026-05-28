---
name: r2-handoff
description: Compacta a conversa atual em um documento de handoff para que outro agente possa continuar o trabalho.
argument-hint: Para que será usada a próxima sessão?
disable-model-invocation: true
---

Escreva um documento de handoff resumindo a conversa atual para que um novo agente possa continuar o trabalho.

Estruture o documento em Markdown com as seções obrigatórias: Contexto, Estado Atual, Próximos Passos, Artefatos Referenciados, Skills Sugeridas.

Não há um limite de comprimento para o documento, mas ele deve ser tão conciso quanto possível sem sacrificar contexto relevante, focando apenas nas informações essenciais para a continuidade do trabalho.

Se a conversa contiver menos de duas trocas de mensagens substanciais, informe o usuário que não há conteúdo suficiente para gerar um handoff útil e encerre sem criar o arquivo.

Salve o arquivo no diretório temporário padrão do sistema ($TMPDIR no macOS/Linux, %TEMP% no Windows) — não no workspace atual. Se não for possível determinar esse diretório, informe o usuário e pergunte onde salvar.

Se a escrita no diretório temporário falhar (por exemplo, permissão negada, ambiente sandboxado ou sistema de arquivos somente leitura), exiba o conteúdo do documento diretamente na conversa (markdown como código fonte para facilitar a cópia, não renderizado) e informe o usuário do erro de escrita.

O documento gerado deve ser escrito no idioma utilizado na conversa até então, salvo se o usuário indicar explicitamente outro idioma.

Inclua uma seção "skills sugeridas" no documento, recomendando quais skills o agente deve invocar.

Não duplique conteúdo já registrado em outros artefatos que foram consultados na conversa (PRDs, planos, ADRs, issues, commits, diffs). Em vez disso, referencie-os por caminho ou URL.

Redija ou remova quaisquer informações sensíveis, como chaves de API, senhas ou informações de identificação pessoal.

Se o usuário fornecer argumentos, trate-os como uma descrição do foco da próxima sessão e adapte o documento de acordo.
