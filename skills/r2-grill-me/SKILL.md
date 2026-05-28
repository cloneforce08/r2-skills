---
name: r2-grill-me
description: Questiona o usuário incansavelmente sobre um plano ou design até chegar a um entendimento compartilhado, resolvendo cada ramificação da árvore de decisões.
argument-hint: Sobre qual idéia ou plano gostaria de discutir?
disable-model-invocation: true
---

Vamos conversar sobre um plano ou uma ideia que tenho.

Me questione incansavelmente sobre cada aspecto deste plano até chegarmos a um entendimento compartilhado. Percorra cada ramificação da árvore de design, resolvendo as dependências entre decisões uma a uma. Para cada pergunta, forneça sua resposta recomendada.

Faça uma pergunta de cada vez. Se a pergunta puder ser feita com a tool `askQuestions` (ou similar disponível) sem prejuízo para a qualidade da pergunta e da resposta, use a tool. Caso contrário, faça a pergunta diretamente.

Após cada resposta, só passe para a próxima pergunta se tivermos chegado a um entendimento compartilhado sobre a resposta. Se não, continue questionando até chegarmos lá.