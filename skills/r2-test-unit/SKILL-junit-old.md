---
name: java-unit-tests
description: Write unit tests for Java projects in this monorepo using JUnit 5, AssertJ, and Mockito following established codebase conventions
---

# Java Unit Tests

## Stack

- **JUnit 5 (Jupiter)** is the standard test framework. Do not use JUnit 4 (`org.junit.Test`, `@RunWith`) in new tests.
- **AssertJ** is the preferred assertion library. Always prefer AssertJ fluent assertions over `org.junit.jupiter.api.Assertions.*`.
- **Mockito** (with `@ExtendWith(MockitoExtension.class)`) when mocking is needed.

## File Placement and Naming

- Test sources go in `src/test/java/` mirroring the production package of the class under test.
- Test resources (SQL scripts, fixtures) go in `src/test/resources/`.

| Pattern | When to use |
|---|---|
| `<ClassName>Test` | Standard — one test class per production class |
| `<ClassName>Test_<methodName>` | When a single method warrants its own file (large test surface) |
| `<Feature>H2Test` | Database integration tests backed by H2 |

## Class and Method Visibility

- Test classes and test methods must be **package-private** (no `public` modifier).
- Example: `class MyClassTest {` not `public class MyClassTest {`

## What to Test

- Only test `public` or package-accessible methods.
- Do **not** test trivial getters and setters unless they contain logic (e.g. validation, transformation).

## Test Structure

- Use Arrange / Act / Assert comment blocks inside each test method.
- Use `@Nested` inner classes to group test cases **only when a single method requires more than 3 test cases**. For 3 or fewer, keep them flat in the main class.
- Annotate every `@Nested` class and every `@Test` method with `@DisplayName`.
- All `@DisplayName` descriptions must be written in **Brazilian Portuguese**.
- Do not look up other test classes in the codebase to copy patterns from.

```java
class FilterCriterionTest {

  @Nested
  @DisplayName("Testes para parsing válido de FilterCriterion")
  class ValidFilterCriterionTests {

    @Test
    @DisplayName("Deve parsear um valor único com operador EQUAL")
    void shouldParseSimpleEqualFilter() {
      // Arrange
      val input = "field:eq:value";

      // Act
      val result = FilterCriterion.parse(input);

      // Assert
      assertThat(result.operator()).isEqualTo(FilterOperator.EQUAL);
      assertThat(result.value()).isEqualTo("value");
    }
  }

  @Nested
  @DisplayName("Testes para parsing inválido de FilterCriterion")
  class InvalidFilterCriterionTests {

    @Test
    @DisplayName("Deve lançar exceção para formato inválido")
    void shouldThrowForInvalidFormat() {
      // Arrange
      val input = "invalid-format";

      // Act / Assert
      assertThatThrownBy(() -> FilterCriterion.parse(input))
          .isInstanceOf(IllegalArgumentException.class)
          .hasMessageContaining("formato inválido");
    }
  }
}
```

## Assertions

Always use AssertJ fluent assertions:

```java
// Equality
assertThat(result).isEqualTo(expected);

// Nullability
assertThat(result).isNotNull();

// Booleans
assertThat(result).isTrue();
assertThat(result).isFalse();

// Collections
assertThat(list).hasSize(3).contains(item);

// Exceptions
assertThatThrownBy(() -> subject.doSomething())
    .isInstanceOf(SomeException.class)
    .hasMessageContaining("mensagem esperada");
```

Never use `assertEquals`, `assertThrows`, or other bare JUnit 5 assertions in new tests.

## Mocking with Mockito

Use mocking only when the class under test has dependencies that cannot or should not be instantiated directly. Prefer direct instantiation whenever possible.

When mocking is needed:

```java
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class MyServiceTest {

  @Mock
  MyRepository repository;

  @InjectMocks
  MyService service;

  @Test
  @DisplayName("Deve retornar resultado ao encontrar entidade")
  void shouldReturnResultWhenEntityFound() {
    // Arrange
    val id = 1L;
    val entity = new MyEntity(id, "valor");
    when(repository.findById(id)).thenReturn(Optional.of(entity));

    // Act
    val result = service.findById(id);

    // Assert
    assertThat(result).isNotNull();
    assertThat(result.id()).isEqualTo(id);
  }
}
```

## What to Avoid

- JUnit 4 imports: `org.junit.Test`, `@RunWith`, `@Before`, `@After`
- `@SpringBootTest` or any Spring context loading in unit tests
- `public` modifier on test classes or test methods
- Bare JUnit 5 assertions: `assertEquals`, `assertThrows`, `assertNotNull`, etc.
- Copying test patterns from other test classes in the codebase
- Stating variable types explicitly when `val` or `var` can be used
