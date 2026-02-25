import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings

from apps.core.analytics import track
from .stripe_service import create_checkout_session, create_portal_session, handle_webhook
from .models import StripeEvent

logger = logging.getLogger('spritetest.billing')


@login_required
def pricing(request):
    return render(request, 'billing/pricing.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'current_plan': request.workspace.plan if request.workspace else 'free',
    })


@login_required
def checkout(request, plan):
    track(str(request.user.id), 'upgrade_initiated', {'plan': plan})

    if plan != 'pro':
        messages.error(request, 'Plano inválido')
        return redirect('billing:pricing')

    price_id = settings.STRIPE_PRO_PRICE_ID
    if not price_id:
        messages.warning(request, 'Stripe não configurado ainda. Plano Pro em breve!')
        return redirect('billing:pricing')

    result = create_checkout_session(
        workspace=request.workspace,
        user=request.user,
        price_id=price_id,
        success_url=request.build_absolute_uri('/billing/success/'),
        cancel_url=request.build_absolute_uri('/billing/pricing/'),
    )
    if 'error' in result:
        messages.error(request, result['error'])
        return redirect('billing:pricing')
    return redirect(result['url'])


@login_required
def success(request):
    messages.success(request, 'Upgrade para Pro realizado com sucesso!')
    return render(request, 'billing/success.html', {
        'workspace': request.workspace,
    })


@login_required
def manage_billing(request):
    result = create_portal_session(
        workspace=request.workspace,
        return_url=request.build_absolute_uri('/dashboard/'),
    )
    if 'error' in result:
        messages.error(request, result['error'])
        return redirect('dashboard:home')
    return redirect(result['url'])


@csrf_exempt
@require_POST
def webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse(status=200)

    try:
        event = handle_webhook(payload, sig_header)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return HttpResponse(status=400)

    StripeEvent.objects.get_or_create(
        stripe_id=event['id'],
        defaults={
            'event_type': event['type'],
            'payload': dict(event),
            'processed': False,
        }
    )

    if event['type'] == 'checkout.session.completed':
        _handle_checkout_completed(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        _handle_subscription_deleted(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        _handle_subscription_updated(event['data']['object'])

    return HttpResponse(status=200)


def _handle_checkout_completed(session):
    from apps.workspaces.models import Workspace

    workspace_id = session.get('metadata', {}).get('workspace_id')
    if not workspace_id:
        return

    try:
        workspace = Workspace.objects.get(id=workspace_id)
        workspace.plan = 'pro'
        workspace.stripe_subscription_id = session.get('subscription', '')
        workspace.save(update_fields=['plan', 'stripe_subscription_id'])
        logger.info(f"Workspace {workspace_id} upgraded to Pro")
    except Workspace.DoesNotExist:
        logger.error(f"Workspace {workspace_id} não encontrado no webhook")


def _handle_subscription_deleted(subscription):
    from apps.workspaces.models import Workspace

    try:
        workspace = Workspace.objects.get(stripe_subscription_id=subscription['id'])
        workspace.plan = 'free'
        workspace.stripe_subscription_id = ''
        workspace.save(update_fields=['plan', 'stripe_subscription_id'])
        logger.info(f"Workspace {workspace.id} downgraded para Free")
    except Workspace.DoesNotExist:
        pass


def _handle_subscription_updated(subscription):
    pass
