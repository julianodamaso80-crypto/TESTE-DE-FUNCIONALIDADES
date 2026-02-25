import logging
from django.conf import settings

logger = logging.getLogger('spritetest.billing')


def create_checkout_session(workspace, user, price_id, success_url, cancel_url):
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=user.email,
            metadata={'workspace_id': str(workspace.id)},
        )
        return {'url': session.url}
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        return {'error': str(e)}


def create_portal_session(workspace, return_url):
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not workspace.stripe_customer_id:
            return {'error': 'Nenhuma assinatura encontrada'}
        session = stripe.billing_portal.Session.create(
            customer=workspace.stripe_customer_id,
            return_url=return_url,
        )
        return {'url': session.url}
    except Exception as e:
        logger.error(f"Portal error: {e}")
        return {'error': str(e)}


def handle_webhook(payload, sig_header):
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
    return event
