from django.db import models
from django.contrib.auth.models import User

# Classe Produto, usada tanto para jogos quanto para equipamentos
class Produto(models.Model):
    nome = models.CharField(max_length=255, default='Nome padrão')
    descricao = models.TextField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_produto = models.CharField(max_length=50)  # Para identificar se é "Jogo" ou "Equipamento"
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)

    def __str__(self):
        return self.nome

# Classe Jogo, que herda da classe Produto
class Jogo(Produto):
    PLATAFORMAS_CHOICES = [
        ('PC', 'PC'),
        ('Xbox', 'Xbox'),
        ('PlayStation5', 'PlayStation5'),
        ('Nintendo', 'Nintendo'),
    ]

    GENEROS_CHOICES = [
        ('Ação', 'Ação'),
        ('Aventura', 'Aventura'),
        ('RPG', 'RPG'),
        ('Desporto', 'Desporto'),
        ('Corrida', 'Corrida'),
    ]

    plataforma = models.CharField(max_length=20, choices=PLATAFORMAS_CHOICES)
    genero = models.CharField(max_length=20, choices=GENEROS_CHOICES)
    data_lancamento = models.DateField()
    desenvolvedora = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} ({self.plataforma})"

# Classe Equipamento, que também herda de Produto
class Equipamento(Produto):
    marca = models.CharField(max_length=50)
    compatibilidade = models.CharField(max_length=100, default='Não aplicável')

    def __str__(self):
        return f"{self.nome} ({self.marca})"

# Carrinho de compras vinculado ao usuário
class Carrinho(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrinho de {self.usuario.username}"

# Itens do Carrinho vinculados ao produto e carrinho
class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome}"

    def total(self):
        return self.quantidade * self.preco_unitario