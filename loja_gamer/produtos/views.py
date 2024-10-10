import stripe
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseBadRequest
from . import models
from .models import Jogo, Equipamento
from .models import Carrinho, ItemCarrinho, Equipamento
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def pagina_inicial(request):
    return render(request, 'produtos/pagina_inicial.html')

def listar_jogos(request):
    jogos = Jogo.objects.all()
    context = {
        'jogos': jogos
    }
    return render(request, 'produtos/listar_jogos.html', context)

def listar_equipamentos(request):
    equipamentos = Equipamento.objects.all()
    return render(request, 'produtos/listar_equipamentos.html', {'equipamentos': equipamentos})


def visualizar_carrinho(request):
    # Obter o carrinho do usuário
    carrinho = Carrinho.objects.get(usuario=request.user)

    # Obter os itens do carrinho
    itens = carrinho.itens.all()

    # Calcular o total de cada item (quantidade * preco_unitario)
    for item in itens:
        item.total = item.quantidade * item.preco_unitario

    # Calcular o total geral do carrinho (somando os valores totais dos itens)
    total = sum(item.total for item in itens)

    # Passar os itens e o total para o template
    return render(request, 'produtos/carrinho.html', {'itens': itens, 'total': total})

@login_required
def adicionar_ao_carrinho(request, produto_id):
    # Verificar se o produto é um Jogo ou Equipamento
    try:
        produto = Jogo.objects.get(id=produto_id)
    except Jogo.DoesNotExist:
        produto = get_object_or_404(Equipamento, id=produto_id)

    # Obter ou criar o carrinho do usuário
    carrinho, criado = Carrinho.objects.get_or_create(usuario=request.user)

    # Verificar se o item já está no carrinho
    item, criado = ItemCarrinho.objects.get_or_create(
        carrinho=carrinho,
        produto=produto,  # Usando o objeto produto diretamente
        defaults={'preco_unitario': produto.preco_unitario, 'quantidade': 1}  # Corrigido para preco_unitario
    )

    # Se o item já existia, incrementar a quantidade
    if not criado:
        item.quantidade += 1
        item.save()

    return redirect('visualizar_carrinho')  # Verifica se essa é a URL correta


@login_required
def checkout(request):
    # Obter o carrinho do usuário
    carrinho = Carrinho.objects.get(usuario=request.user)

    # Calcular o total do carrinho
    total = carrinho.itens.aggregate(
        total=Sum('quantidade') * Sum('preco_unitario')
    )['total']

    if total is None:
        total = 0

    logger.debug(f"Total calculado no backend: {total}")

    # Converter o total para centavos (Stripe exige o valor em centavos)
    total_em_centavos = int(total * 100)

    # Criar uma sessão de checkout
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': 'Produtos no Carrinho',
                },
                'unit_amount': total_em_centavos,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('pedido_concluido')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('checkout')),
    )

    # Redirecionar para a página de checkout do Stripe
    return redirect(session.url, code=303)


@login_required
def pedido_concluido(request):
    session_id = request.GET.get('session_id')

    if session_id:
        try:
            # Recuperar a sessão do Stripe usando o ID da sessão
            session = stripe.checkout.Session.retrieve(session_id)
            # Recuperar o Payment Intent para obter mais detalhes do pagamento
            payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)

            # Limpar o carrinho após a conclusão do pagamento
            carrinho = Carrinho.objects.get(usuario=request.user)
            carrinho.itens.all().delete()  # Remove todos os itens do carrinho

            return render(request, 'produtos/pedido_concluido.html', {
                'session': session,
                'payment_intent': payment_intent,
            })
        except stripe.error.StripeError as e:
            return HttpResponseBadRequest(f"Erro com o pagamento: {str(e)}")

    # Se não houver session_id, redirecionar para a página de checkout
    return redirect('checkout')

@login_required
def remover_item(request, item_id):
    # Obtenha o carrinho do usuário logado
    carrinho = Carrinho.objects.get(usuario=request.user)

    # Encontre o item no carrinho e remova-o
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho=carrinho)
    item.delete()

    # Redireciona o usuário de volta para a página do carrinho
    return redirect('visualizar_carrinho')