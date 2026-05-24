Feature: Processamento de Compra no E-commerce

  Scenario: Compra com Sucesso
    Given que o sistema possui o produto "teclado" em estoque
    When o cliente realiza a compra do "teclado" com o cartão "1234"
    Then a resposta da API deve ser de sucesso
    And o valor pago na resposta deve ser 200.0