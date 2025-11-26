"""
Manejadores de pagos para diferentes pasarelas.
Cada handler implementa la lógica específica de la pasarela de pago.
"""
import requests
from django.conf import settings
from decimal import Decimal


class PaymentHandler:
    """Clase base para manejadores de pago."""
    
    def create_payment(self, solicitud, return_url, cancel_url):
        """Crea un pago en la pasarela. Retorna dict con payment_url y payment_id."""
        raise NotImplementedError
    
    def verify_payment(self, payment_id, transaction_data):
        """Verifica un pago. Retorna (success: bool, data: dict)."""
        raise NotImplementedError


class StripePaymentHandler(PaymentHandler):
    """Handler para pagos con Stripe."""
    
    def create_payment(self, solicitud, return_url, cancel_url):
        """Crea una sesión de Checkout de Stripe."""
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'{solicitud.plan_solicitado.nombre} - {solicitud.nombre_clinica}',
                            'description': solicitud.plan_solicitado.descripcion,
                        },
                        'unit_amount': int(solicitud.plan_solicitado.precio * 100),  # Centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=return_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                client_reference_id=str(solicitud.id),
                metadata={
                    'solicitud_id': str(solicitud.id),
                    'clinica_nombre': solicitud.nombre_clinica,
                    'plan': solicitud.plan_solicitado.nombre,
                }
            )
            
            return {
                'success': True,
                'payment_url': session.url,
                'payment_id': session.id,
                'session_data': {
                    'id': session.id,
                    'amount_total': session.amount_total / 100,
                    'currency': session.currency,
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id, transaction_data=None):
        """Verifica el pago de Stripe."""
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            session = stripe.checkout.Session.retrieve(payment_id)
            
            success = session.payment_status == 'paid'
            
            return success, {
                'session_id': session.id,
                'payment_intent': session.payment_intent,
                'amount_total': session.amount_total / 100,
                'currency': session.currency,
                'payment_status': session.payment_status,
                'customer_email': session.customer_details.email if session.customer_details else None,
            }
        except Exception as e:
            return False, {'error': str(e)}


class PayPalPaymentHandler(PaymentHandler):
    """Handler para pagos con PayPal."""
    
    def create_payment(self, solicitud, return_url, cancel_url):
        """Crea un pago de PayPal."""
        # Configuración de PayPal
        client_id = settings.PAYPAL_CLIENT_ID
        secret = settings.PAYPAL_SECRET
        mode = settings.PAYPAL_MODE  # 'sandbox' o 'live'
        
        base_url = "https://api-m.sandbox.paypal.com" if mode == 'sandbox' else "https://api-m.paypal.com"
        
        # Obtener token de acceso
        auth_response = requests.post(
            f"{base_url}/v1/oauth2/token",
            headers={"Accept": "application/json", "Accept-Language": "en_US"},
            auth=(client_id, secret),
            data={"grant_type": "client_credentials"}
        )
        
        if auth_response.status_code != 200:
            return {'success': False, 'error': 'Error obteniendo token de PayPal'}
        
        access_token = auth_response.json()['access_token']
        
        # Crear orden
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "reference_id": str(solicitud.id),
                "description": f"{solicitud.plan_solicitado.nombre} - {solicitud.nombre_clinica}",
                "amount": {
                    "currency_code": "USD",
                    "value": str(solicitud.plan_solicitado.precio)
                }
            }],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
                "brand_name": "Clínica Dental",
                "user_action": "PAY_NOW"
            }
        }
        
        order_response = requests.post(
            f"{base_url}/v2/checkout/orders",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            json=order_data
        )
        
        if order_response.status_code not in [200, 201]:
            return {'success': False, 'error': 'Error creando orden de PayPal'}
        
        order = order_response.json()
        approve_link = next(link['href'] for link in order['links'] if link['rel'] == 'approve')
        
        return {
            'success': True,
            'payment_url': approve_link,
            'payment_id': order['id'],
            'order_data': order
        }
    
    def verify_payment(self, payment_id, transaction_data=None):
        """Verifica el pago de PayPal."""
        client_id = settings.PAYPAL_CLIENT_ID
        secret = settings.PAYPAL_SECRET
        mode = settings.PAYPAL_MODE
        
        base_url = "https://api-m.sandbox.paypal.com" if mode == 'sandbox' else "https://api-m.paypal.com"
        
        # Obtener token
        auth_response = requests.post(
            f"{base_url}/v1/oauth2/token",
            headers={"Accept": "application/json"},
            auth=(client_id, secret),
            data={"grant_type": "client_credentials"}
        )
        
        if auth_response.status_code != 200:
            return False, {'error': 'Error obteniendo token'}
        
        access_token = auth_response.json()['access_token']
        
        # Verificar orden
        order_response = requests.get(
            f"{base_url}/v2/checkout/orders/{payment_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if order_response.status_code != 200:
            return False, {'error': 'Error verificando orden'}
        
        order = order_response.json()
        success = order['status'] == 'COMPLETED'
        
        return success, {
            'order_id': order['id'],
            'status': order['status'],
            'amount': order['purchase_units'][0]['amount']['value'],
            'currency': order['purchase_units'][0]['amount']['currency_code'],
            'payer_email': order.get('payer', {}).get('email_address'),
        }


class MercadoPagoPaymentHandler(PaymentHandler):
    """Handler para pagos con MercadoPago."""
    
    def create_payment(self, solicitud, return_url, cancel_url):
        """Crea una preferencia de pago de MercadoPago."""
        import mercadopago
        
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        preference_data = {
            "items": [{
                "title": f"{solicitud.plan_solicitado.nombre} - {solicitud.nombre_clinica}",
                "description": solicitud.plan_solicitado.descripcion,
                "quantity": 1,
                "currency_id": "USD",
                "unit_price": float(solicitud.plan_solicitado.precio)
            }],
            "back_urls": {
                "success": return_url,
                "failure": cancel_url,
                "pending": return_url
            },
            "auto_return": "approved",
            "external_reference": str(solicitud.id),
            "metadata": {
                "solicitud_id": str(solicitud.id),
                "clinica_nombre": solicitud.nombre_clinica
            }
        }
        
        try:
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            
            return {
                'success': True,
                'payment_url': preference['init_point'],
                'payment_id': preference['id'],
                'preference_data': preference
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id, transaction_data=None):
        """Verifica el pago de MercadoPago."""
        import mercadopago
        
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        try:
            payment_info = sdk.payment().get(payment_id)
            payment = payment_info["response"]
            
            success = payment['status'] == 'approved'
            
            return success, {
                'payment_id': payment['id'],
                'status': payment['status'],
                'amount': payment['transaction_amount'],
                'currency': payment['currency_id'],
                'payer_email': payment.get('payer', {}).get('email'),
            }
        except Exception as e:
            return False, {'error': str(e)}


# Factory para obtener el handler correcto
def get_payment_handler(metodo_pago):
    """Retorna el handler apropiado según el método de pago."""
    handlers = {
        'STRIPE': StripePaymentHandler,
        'PAYPAL': PayPalPaymentHandler,
        'MERCADOPAGO': MercadoPagoPaymentHandler,
    }
    
    handler_class = handlers.get(metodo_pago)
    if not handler_class:
        raise ValueError(f"Método de pago '{metodo_pago}' no soportado")
    
    return handler_class()
