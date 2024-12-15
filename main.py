import os
import time
from typing import Any, List
from uuid import uuid4

class Product:
    """
    Representa um produto no inventário com ID único, nome e quantidade.
    """

    def __init__(self, name, quantity=0):
        self.__nome = name
        self.re_count(quantity)
        self.id = str(uuid4())

    def out_of_stock(self) -> bool:
        """Verifica se o produto está sem estoque."""
        return self.quantity == 0

    def re_count(self, new_quantity: int):
        """
        Atualiza a quantidade do produto.

        Levanta erro se a quantidade for negativa.
        """
        # Valida se a nova quantidade não é negativa
        if new_quantity >= 0:
            self.quantity = new_quantity
        else:
            raise ValueError("Quantidade do produto não pode ser menor que zero.")

    def matching_names(self, name: str) -> bool:
        """
        Verifica se o nome fornecido corresponde ao nome do produto.

        Implementa busca mais precisa com regras específicas de correspondência.
        """
        # Normaliza os nomes removendo espaços e convertendo para minúsculas
        s_nome = name.strip().lower()
        s_original = self.__nome.strip().lower()

        # Requer pelo menos 2 caracteres correspondentes ou correspondência exata
        return s_nome in s_original and (len(s_nome) > 3 or s_original == s_nome)

    def name(self) -> str:
        """Retorna o nome do produto com a primeira letra maiúscula."""
        return self.__nome.title()

    def info(self) -> dict:
        """
        Obtém informações detalhadas do produto.

        Retorna dicionário com detalhes do produto.
        """
        return {
            "id": self.id,
            "nome": self.name(),
            "quantidade": self.quantity,
            "fora_de_estoque": self.out_of_stock()
        }

class ProductNotFound(Exception):
    """Exceção personalizada para produto não encontrado no inventário."""

    def __init__(self, nome: str):
        super().__init__(f"Produto {nome.title()} não encontrado")

class StockManager:
    """
    Gerencia o inventário de produtos com várias operações e interface de usuário.
    """

    def __init__(self):
        # Inicializa dicionário para armazenar produtos
        self.products: dict[str, Product] = {}

    def require(self, text, type_required: Any = str, null_msg=False):
        """
        Solicita entrada do usuário e valida.

        Garante que a entrada seja do tipo correto.
        """
        resultado = input(text).strip()
        try:
            # Permite entrada vazia se o parâmetro nulo for True
            if resultado == "" and null_msg:
                return ""
            return type_required(resultado)
        except (ValueError, Exception):
            print(f"Esperado {type_required} não {resultado}. Tente novamente.")
            return self.require(text, type_required)

    def require_index(self, texto, max: int):
        """
        Solicita e valida um índice dentro de um intervalo válido.

        Garante que o índice esteja entre 1 e máximo-1.
        """
        numero = self.require(texto, int)
        if 0 <= numero <= max:
            return numero
        else:
            print(f"O número tem de ser maior que 0 e menor que {max}")
            return self.require_index(texto, max)

    def clear(self):
        """Limpa a tela do console."""
        os.system("clear")

    def biggest_name_length(self):
        """
        Encontra o comprimento do nome mais longo do produto.

        Útil para formatação de tabela.
        """
        return max((len(produto.name()) for produto in self.products.values()), default=0)

    def table(self):
        """Exibe tabela formatada de todos os produtos."""
        if len(self.products) > 0:
            # Calcula largura total baseada no maior nome
            total = self.biggest_name_length() + 10
            print("|", "-" * total, "|------------|", sep="")
            for produto in self.products.values():
                # Formata cada linha da tabela com nome do produto e quantidade
                print(
                    f"| {produto.name()}{' ' * (total - 1 - len(produto.name()))}| {str(produto.quantity) + ' ' * 9 if not produto.out_of_stock() else 'FORA DE ESTOQUE'} |"
                    )
            print("|", "-" * total, "|------------|", sep="")
            self.sleep(5)
        else:
            print("Zero produtos na base de Dados.")

    def interface(self):
        """Interface principal para gerenciamento de estoque."""
        self.clear()
        print("Olá. O que você deseja fazer:")
        print("\t-1) Adicionar Produto\n\t-2) Remover Produto\n\t-3) Recontar Produto\n\t-4) Mostrar Armazém\n\t-5) Ver Informações do Produto\n\t-0) Sair")
        escolha = self.require("Sua escolha: ", int)

        # Usa estrutura match para direcionar para diferentes métodos
        match escolha:
            case 0:
                print(":-( Adeus")
                exit(0)
            case 1:
                self.clear()
                self.add_product()
            case 2:
                self.clear()
                self.del_product()
            case 3:
                self.clear()
                self.change_qtd()
            case 4:
                self.clear()
                self.table()
            case 5:
                self.clear()
                self.info()
            case _:
                print("Não entendi")

        # Pausa e limpa a tela para próxima interação
        self.sleep(1)
        self.clear()
        self.interface()

    def add_product(self):
        """Adiciona novo produto ao inventário."""
        novo_nome = self.require("Qual é o nome do Produto: ").title()
        nova_quantidade = self.require(f"Qual é a quantidade de {novo_nome}s em armazém: ", int)
        produto = Product(novo_nome, nova_quantidade)
        # Adiciona produto ao dicionário usando seu ID único
        self.products[produto.id] = produto
        print(f"{novo_nome} foi adicionado com sucesso")

    def change_qtd(self):
        """Atualiza a quantidade de um produto existente."""
        try:
            produto = self.get_product()
            nova_quantidade = self.require("Qual é o novo número em estoque: ", int)
            produto.re_count(nova_quantidade)
        except ProductNotFound:
            print("O Produto requisitado não foi encontrado na base de dados.")
        except ValueError:
            print("O novo valor não pode ser negativo.")
        else:
            print("Salvo com sucesso.")

    def del_product(self):
        """Remove um produto do inventário."""
        try:
            produto = self.get_product()
            deseja_apagar = self.require("Deseja realmente apagar? (sim/não): ").lower().startswith("s")
            if deseja_apagar:
                del self.products[produto.id]
                print("Apagado com sucesso.")
            else:
                print("Cancelando...")
        except ProductNotFound:
            print("O Produto requisitado não foi encontrado na base de dados.")

    def info(self):
        """Exibe informações detalhadas de um produto específico."""
        try:
            produto = self.get_product()
            info = produto.info()
            print("\nInformações do Produto:")
            for chave, valor in info.items():
                print(f"{chave.capitalize().replace("_", " ")}: {valor}")
            self.sleep(5)
        except ProductNotFound:
            print("O Produto requisitado não foi encontrado na base de dados.")

    def get_product(self):
        """
        Encontra um produto pelo nome com funcionalidade de busca aprimorada.

        Permite seleção quando múltiplos produtos correspondem.
        """
        nome = self.require("Qual o nome do produto: ")
        # Filtra produtos que correspondem ao nome
        produtos: List[Product] = list(
            filter(lambda produto: self.products[produto.id].matching_names(nome), self.products.values())
            )

        if len(produtos) > 1:
            print("Encontrei os seguintes produtos: ")
            for i, p in enumerate(produtos):
                print(f" - {i}) {p.name()}")
            # Permite escolher entre produtos correspondentes
            index = self.require_index("Qual é o produto: ", len(produtos))
            return produtos[index]
        elif len(produtos) == 1:
            return produtos[0]
        else:
            raise ProductNotFound(nome)

    def execute(self):
        """Inicia a aplicação de gerenciamento de estoque."""
        self.interface()

    def sleep(self, seconds):
        try:
            time.sleep(seconds)
        except KeyboardInterrupt:
            return

if __name__ == '__main__':
    StockManager().execute()