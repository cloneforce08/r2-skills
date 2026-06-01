# Referencia JUnit

Guia de convencoes especificas para testes unitarios em projetos Java.

## Stack padrao

- Framework de teste: JUnit 5 (Jupiter)
- Biblioteca de assercoes: AssertJ
- Mocks: Mockito (com `MockitoExtension` quando necessario)

## Estrutura de arquivos

- Fontes de teste em `src/test/java/` espelhando pacote da classe de producao
- Recursos de teste em `src/test/resources/`

Padroes de nomes comuns:

- `<ClassName>Test`
- `<ClassName>Test_<methodName>` para superficies grandes
- `<Feature>H2Test` para cenarios com H2

## Convencoes de classe e metodo

- Classe e metodos de teste sem `public` (package-private)
- Usar `@DisplayName` em classes `@Nested` e metodos `@Test`

## Organizacao de casos

- Usar `@Nested` quando um unico metodo exigir mais de 3 casos
- Para 3 ou menos, manter casos no nivel principal da classe
- Aplicar AAA em cada teste com comentarios claros

## Assercoes

- Preferir AssertJ fluent API (`assertThat`, `assertThatThrownBy`)
- Evitar assercoes basicas do JUnit (`assertEquals`, `assertThrows`, etc.)

## Mocks com Mockito

- Mockar apenas dependencias que nao devem ser instanciadas diretamente
- Em cenarios com injecao, usar `@Mock` e `@InjectMocks`
- Habilitar extensao com `@ExtendWith(MockitoExtension.class)`

## Antipadroes a evitar

- Imports/annotacoes de JUnit 4 (`org.junit.Test`, `@RunWith`, `@Before`, `@After`)
- Modificador `public` em classes/metodos de teste
- Copiar padroes de testes existentes sem avaliar qualidade

## Orientações adicionais para testes unitarios em Spring Boot

Essa seção reforça a distinção fundamental: se o teste é unitário, ele deve continuar sendo apenas
um teste de Java + JUnit + Mockito, mesmo dentro de uma aplicação Spring Boot. O framework não deve
participar da execução do teste.

- Nao devem carregar contexto Spring
- Nao utilizar `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest` ou outras anotacoes que inicializem
  partes do framework
- Instanciar a classe sob teste diretamente ou utilizar `@InjectMocks` quando apropriado
- Preferir `@ExtendWith(MockitoExtension.class)` para gerenciamento de mocks
- Dependencias Spring devem ser mockadas quando fizerem parte da colaboracao da classe testada
- Evitar uso de `@MockBean`, pois trata-se de recurso voltado a testes com contexto Spring

Exemplo recomendado:

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository repository;

    @InjectMocks
    private UserService service;

    @Test
    @DisplayName("Deve retornar usuario quando encontrado")
    void shouldReturnUserWhenFound() {
        // Arrange
        when(repository.findById(1L))
            .thenReturn(Optional.of(new User()));

        // Act
        User user = service.findById(1L);

        // Assert
        assertThat(user).isNotNull();
    }
}
```
