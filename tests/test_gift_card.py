"""
    Test Gift Card

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) LTD
    :license: GPLv3, see LICENSE for more details
"""
import unittest
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT
from trytond.transaction import Transaction
from test_base import BaseTestCase


class TestGiftCard(BaseTestCase):
    """
    Test case for gift cards.
    """

    def create_product(
        self, type='goods', mode='physical', is_gift_card=False,
        allow_open_amount=False
    ):
        """
        Create default product
        """
        Template = POOL.get('product.template')
        Uom = POOL.get('product.uom')

        uom, = Uom.search([('name', '=', 'Unit')])

        values = {
            'name': 'product',
            'type': type,
            'list_price': Decimal('20'),
            'cost_price': Decimal('5'),
            'default_uom': uom.id,
            'salable': True,
            'sale_uom': uom.id,
            'account_revenue': self._get_account_by_kind('revenue').id,
        }
        product_values = {
            'code': 'Test Product'
        }

        if is_gift_card:
            product_values.update({
                'is_gift_card': True,
                'gift_card_delivery_mode': mode
            })

            if not allow_open_amount:
                product_values.update({
                    'gift_card_prices': [
                        ('create', [{
                            'price': 500,
                        }, {
                            'price': 600,
                        }])
                    ]
                })
            else:
                product_values.update({
                    'allow_open_amount': True,
                    'gc_min': 100,
                    'gc_max': 400
                })

        values.update({
            'products': [
                ('create', [product_values])
            ]
        })

        return Template.create([values])[0].products[0]

    def test0010_render_gift_card_on_website(self):
        """
        Test the rendering of gift card on website
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            gift_card_product = self.create_product(is_gift_card=True)
            gift_card_product.displayed_on_eshop = True
            gift_card_product.uri = "gift-card-product"
            gift_card_product.save()

            product = self.create_product(is_gift_card=False)
            product.displayed_on_eshop = True
            product.uri = "test-product"
            product.save()

            with app.test_client() as c:
                rv = c.get('/product/%s' % gift_card_product.uri)
                self.assertEqual(rv.status_code, 302)
                self.assertTrue(
                    rv.location.endswith('/gift-card/gift-card-product')
                )

                rv = c.get('/product/%s' % product.uri)
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, product.name)

    def test0020_add_gift_card_to_cart_case1(self):
        """
        Test adding gift card without open amounts
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            gift_card_product = self.create_product(
                is_gift_card=True, type="service", mode="virtual"
            )
            gift_card_product.displayed_on_eshop = True
            gift_card_product.uri = "gift-card-product"
            gift_card_product.save()

            with app.test_client() as c:
                data = {
                    'recipient_email': 'rec@ol.in',
                    'recipient_name': 'Recipient',
                    'selected_amount': gift_card_product.gift_card_prices[0].id,
                    'open_amount': 0.0,
                    'message': 'Test Message',
                }
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    rv.data, 'Cart:%d,1,500.00' % self.Cart.find_cart().id
                )

                # Test login handler
                self.login(c, 'email@example.com', 'password')
                cart = self.Cart.find_cart(user=self.registered_user.id)

                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    rv.data, 'Cart:%d,1,500.00' % cart.id
                )

                # Test if a new line is added if the same gift card
                # is added to cart
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,2,1000.00' % cart.id)

    def test0030_add_gift_card_to_cart_case2(self):
        """
        Test adding gift card with open amounts
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            gift_card_product = self.create_product(
                is_gift_card=True, type="service", mode="virtual",
                allow_open_amount=True
            )
            gift_card_product.displayed_on_eshop = True
            gift_card_product.uri = "gift-card-product"
            gift_card_product.save()

            with app.test_client() as c:

                data = {
                    'recipient_email': 'rec@ol.in',
                    'recipient_name': 'Recipient',
                    'selected_amount': 0,
                    'open_amount': 200,
                    'message': 'Test Message',
                }
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    rv.data, 'Cart:%d,1,200.00' % self.Cart.find_cart().id
                )

                # Test login handler
                self.login(c, 'email@example.com', 'password')
                cart = self.Cart.find_cart(user=self.registered_user.id)

                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,1,200.00' % cart.id)

                # Test if a new line is added if the same gift card
                # is added to cart
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,2,400.00' % cart.id)

    def test0040_add_gift_card_to_cart_case3(self):
        """
        Test adding gift card with invlid data
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            gift_card_product = self.create_product(
                is_gift_card=True, type="service", mode="virtual",
                allow_open_amount=True
            )
            gift_card_product.displayed_on_eshop = True
            gift_card_product.uri = "gift-card-product"
            gift_card_product.save()

            with app.test_client() as c:

                data = {
                    'recipient_email': 'rec@ol.in',
                    'recipient_name': 'Recipient',
                    'selected_amount': 0,
                    'open_amount': 500,
                    'message': 'Test Message',
                }

                # Test if nothing was added to cart because open amount is
                # not in defined range
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertTrue(self.Cart.find_cart() is None)

    def test0050_add_physical_gift_card_to_cart_case1(self):
        """
        Test adding physical gift card without open amounts
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            gift_card_product = self.create_product(is_gift_card=True)
            gift_card_product.displayed_on_eshop = True
            gift_card_product.uri = "gift-card-product"
            gift_card_product.save()

            with app.test_client() as c:

                data = {
                    'selected_amount': gift_card_product.gift_card_prices[0].id,
                    'open_amount': 0.0,
                    'message': 'Test Message',
                }
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    rv.data, 'Cart:%d,1,500.00' % self.Cart.find_cart().id
                )

                # Test login handler
                self.login(c, 'email@example.com', 'password')
                cart = self.Cart.find_cart(user=self.registered_user.id)

                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,1,500.00' % cart.id)

                # Test if a new line is added if the same gift card
                # is added to cart
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,2,1000.00' % cart.id)

    def test0060_add_physical_gift_card_to_cart_case2(self):
        """
        Test adding physical gift card with open amounts
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            gift_card_product = self.create_product(
                is_gift_card=True, allow_open_amount=True
            )
            gift_card_product.displayed_on_eshop = True
            gift_card_product.uri = "gift-card-product"
            gift_card_product.save()

            with app.test_client() as c:

                data = {
                    'selected_amount': 0,
                    'open_amount': 200,
                    'message': 'Test Message',
                }
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    rv.data, 'Cart:%d,1,200.00' % self.Cart.find_cart().id
                )

                # Test login handler
                self.login(c, 'email@example.com', 'password')
                cart = self.Cart.find_cart(user=self.registered_user.id)

                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,1,200.00' % cart.id)

                # Test if a new line is added if the same gift card
                # is added to cart
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,2,400.00' % cart.id)

    def test0070_add_combined_gift_card_to_cart_case1(self):
        """
        Test adding combined gift card without open amounts
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            gift_card_product = self.create_product(
                is_gift_card=True, mode='combined'
            )
            gift_card_product.displayed_on_eshop = True
            gift_card_product.uri = "gift-card-product"
            gift_card_product.save()

            with app.test_client() as c:

                data = {
                    'recipient_email': 'rec@ol.in',
                    'selected_amount': gift_card_product.gift_card_prices[0].id,
                    'open_amount': 0.0,
                    'message': 'Test Message',
                }
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    rv.data, 'Cart:%d,1,500.00' % self.Cart.find_cart().id
                )

                # Test login handler
                self.login(c, 'email@example.com', 'password')
                cart = self.Cart.find_cart(user=self.registered_user.id)

                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,1,500.00' % cart.id)

                # Test if a new line is added if the same gift card
                # is added to cart
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,2,1000.00' % cart.id)

    def test0080_add_gift_card_to_cart_case2(self):
        """
        Test adding combined gift card with open amounts
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            gift_card_product = self.create_product(
                is_gift_card=True, mode='combined', allow_open_amount=True
            )
            gift_card_product.displayed_on_eshop = True
            gift_card_product.uri = "gift-card-product"
            gift_card_product.save()

            with app.test_client() as c:

                data = {
                    'recipient_name': 'Test User',
                    'recipient_email': 'rec@ol.in',
                    'selected_amount': 0,
                    'open_amount': 200,
                }
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    rv.data, 'Cart:%d,1,200.00' % self.Cart.find_cart().id
                )

                # Test login handler
                self.login(c, 'email@example.com', 'password')
                cart = self.Cart.find_cart(user=self.registered_user.id)

                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,1,200.00' % cart.id)

                # Test if a new line is added if the same gift card
                # is added to cart
                c.post(
                    '/gift-card/%s' % gift_card_product.uri, data=data
                )
                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(rv.data, 'Cart:%d,2,400.00' % cart.id)


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestGiftCard)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
