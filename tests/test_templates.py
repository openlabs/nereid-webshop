'''

    Test Templates

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) LTD
    :license: GPLv3, see LICENSE for more details
'''
import random
import unittest
from trytond.tests.test_tryton import USER, DB_NAME, CONTEXT
from trytond.transaction import Transaction
from test_base import BaseTestCase
from trytond.config import CONFIG
from decimal import Decimal
from nereid import request

CONFIG['smtp_from'] = 'from@xyz.com'


class TestTemplates(BaseTestCase):
    """
    Test case for templates in nereid-webshop.
    """

    def create_test_products(self):
        # Create product templates with products
        self._create_product_template(
            'product 1',
            [{
                'category': self.category.id,
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
            }],
            uri='product-1',
        )
        self._create_product_template(
            'product 2',
            [{
                'category': self.category2.id,
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('20'),
                'cost_price': Decimal('5'),
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
            }],
            uri='product-2',
        )
        self._create_product_template(
            'product 3',
            [{
                'category': self.category3.id,
                'type': 'goods',
                'list_price': Decimal('30'),
                'cost_price': Decimal('5'),
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
            }],
            uri='product-3',
        )
        self._create_product_template(
            'product 4',
            [{
                'category': self.category3.id,
                'type': 'goods',
                'list_price': Decimal('30'),
                'cost_price': Decimal('5'),
                'account_expense': self._get_account_by_kind('expense').id,
                'account_revenue': self._get_account_by_kind('revenue').id,
            }],
            uri='product-4',
            displayed_on_eshop=False
        )

    def _create_product_template(
        self, name, vlist, uri, uom=u'Unit', displayed_on_eshop=True
    ):
        """
        Create a product template with products and return its ID

        :param name: Name of the product
        :param vlist: List of dictionaries of values to create
        :param uri: uri of product template
        :param uom: Note it is the name of UOM (not symbol or code)
        :param displayed_on_eshop: Boolean field to display product
                                   on shop or not
        """
        _code_list = []
        code = random.choice('ABCDEFGHIJK')
        while code in _code_list:
            code = random.choice('ABCDEFGHIJK')
        else:
            _code_list.append(code)

        for values in vlist:
            values['name'] = name
            values['default_uom'], = self.Uom.search(
                [('name', '=', uom)], limit=1
            )
            values['sale_uom'], = self.Uom.search(
                [('name', '=', uom)], limit=1
            )
            values['products'] = [
                ('create', [{
                    'uri': uri,
                    'displayed_on_eshop': displayed_on_eshop,
                    'code': code,
                }])
            ]
        return self.ProductTemplate.create(vlist)

    def cart(self, to_login):
        """
        Checking cart functionality with and without login.
        Used by test_cart.
        """
        qty = 7

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()
            self.create_test_products()
            product1, = self.ProductTemplate.search([
                ('name', '=', 'product 1')
            ])

            with app.test_client() as c:
                if to_login:
                    self.login(c, "email@example.com", "password")

                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)
                sales = self.Sale.search([])
                self.assertEqual(len(sales), 0)

                c.post(
                    '/cart/add',
                    data={
                        'product': product1.id,
                        'quantity': qty
                    }
                )

                rv = c.get('/cart')
                self.assertEqual(rv.status_code, 200)

                sales = self.Sale.search([])
                self.assertEqual(len(sales), 1)
                sale = sales[0]
                self.assertEqual(len(sale.lines), 1)
                self.assertEqual(
                    sale.lines[0].product, product1.products[0]
                )
                self.assertEqual(sale.lines[0].quantity, qty)

    def test_0010_home_template(self):
        """
        Test for home template.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                rv = c.get('/')
                self.assertEqual(rv.status_code, 200)
                self.assertEqual(request.path, '/')

    def test_0015_login(self):
        """
        Test for login template.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                rv = c.get('/login')
                self.assertEqual(rv.status_code, 200)

                rv2 = self.login(c, 'email@example.com', 'password')
                self.assertIn('Redirecting', rv2.data)
                self.assertTrue(rv2.location.endswith('localhost/'))

                with self.assertRaises(AssertionError):
                    self.login(c, 'email@example.com', 'wrong')

    def test_0020_registration(self):
        """
        Test for registration template.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                rv = c.get('/registration')
                self.assertEqual(rv.status_code, 200)

                data = {
                    'name': 'Registered User',
                    'email': 'regd_user@openlabs.co.in',
                    'password': 'password'
                }

                response = c.post('/registration', data=data)
                self.assertEqual(response.status_code, 200)

                data['confirm'] = 'password'
                response = c.post('/registration', data=data)
                self.assertEqual(response.status_code, 302)

    def test_0025_nodes(self):
        """
        Tests for nodes/subnodes.
        Tests node properties.
        """

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            uom, = self.Uom.search([], limit=1)

            values1 = {
                'name': 'Product-1',
                'category': self.category.id,
                'type': 'goods',
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-1',
                        'displayed_on_eshop': True
                    }])
                ]
            }

            values2 = {
                'name': 'Product-2',
                'category': self.category.id,
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-2',
                        'displayed_on_eshop': True
                    }, {
                        'uri': 'product-21',
                        'displayed_on_eshop': True
                    }])
                ]
            }

            values3 = {
                'name': 'Product-3',
                'category': self.category.id,
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'default_uom': uom.id,
                'products': [
                    ('create', [{
                        'uri': 'product-3',
                        'displayed_on_eshop': True
                    }])
                ]
            }

            template1, template2, template3, = self.ProductTemplate.create([
                values1, values2, values3
            ])

            node1, = self.Node.create([{
                'name': 'Node1',
                'type_': 'catalog',
                'slug': 'node1',
            }])

            self.assert_(node1)

            node2, = self.Node.create([{
                'name': 'Node2',
                'type_': 'catalog',
                'slug': 'node2',
                'display': 'product.template',
            }])

            node3, = self.Node.create([{
                'name': 'Node3',
                'type_': 'catalog',
                'slug': 'node3',
            }])

            self.Node.write([node2], {
                'parent': node1
            })

            self.Node.write([node3], {
                'parent': node2
            })

            # Create Product-Node relationships.
            self.ProductNodeRelationship.create([{
                'product': pro,
                'node': node1,
            } for pro in template1.products])
            self.ProductNodeRelationship.create([{
                'product': pro,
                'node': node2,
            } for pro in template2.products])
            self.ProductNodeRelationship.create([{
                'product': pro,
                'node': node3,
            } for pro in template3.products])

            app = self.get_app()

            for node in [node1, node2, node3]:
                self.assert_(node)

            self.assertEqual(node2.parent, node1)

            with app.test_client() as c:
                url = 'nodes/{0}/{1}/{2}'.format(
                    node1.id, node1.slug, 1
                )
                rv = c.get('/nodes/{0}/{1}'.format(node1.id, node1.slug))
                self.assertEqual(rv.status_code, 200)

                url = 'nodes/{0}/{1}/{2}'.format(
                    node2.id, node2.slug, 1
                )
                rv = c.get(url)
                self.assertEqual(rv.status_code, 200)

    def test_0030_articles(self):
        """
        Tests the rendering of an article.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            article, = self.Article.search([
                ('uri', '=', 'test-article')
            ])
            categ, = self.ArticleCategory.search([
                ('title', '=', 'Test Categ')
            ])

            self.assertEqual(len(categ.published_articles), 0)
            self.Article.publish([article])
            self.assertEqual(len(categ.published_articles), 1)

            with app.test_client() as c:
                response = c.get('/article/test-article')
                self.assertEqual(response.status_code, 200)
                self.assertIn('Test Content', response.data)
                self.assertIn('Test Article', response.data)

    def test_0035_cart(self):
        """
        Test the cart.
        """
        for to_login in [True, False]:
            print("Login?: {0}".format(to_login))
            self.cart(to_login)

    def test_0040_addresses(self):
        """
        Test addresses.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                rv = c.get('/view-address')
                self.assertEqual(rv.status_code, 302)

                self.login(c, 'email@example.com', 'password')
                rv = c.get('/view-address')
                self.assertEqual(rv.status_code, 200)

                # Creating an address
                rv = c.get('/create-address')
                self.assertEqual(rv.status_code, 200)

                data = {
                    'name': 'Some Dude',
                    'street': 'Test Street',
                    'zip': 'zip',
                    'city': 'city',
                    'email': 'email@example.com',
                    'phone': '123456789',
                    'country': self.available_countries[0].id,
                    'subdivision': self.Country(
                        self.available_countries[0]
                    ).subdivisions[0].id
                }

                # Check if zero addresses before posting.
                self.assertEqual(
                    len(self.registered_user.party.addresses),
                    0
                )

                response = c.post(
                    '/create-address',
                    data=data
                )
                self.assertEqual(response.status_code, 302)

                # Check that our address info is present in template data.
                address, = self.registered_user.party.addresses
                rv = c.get('/view-address')
                self.assertIn(data['name'], rv.data)
                self.assertIn(data['street'], rv.data)
                self.assertIn(data['city'], rv.data)

                self.assertEqual(rv.status_code, 200)
                self.assertEqual(
                    len(self.registered_user.party.addresses),
                    1
                )

                # Now edit some bits of the address and view it again.
                rv = c.get('/edit-address/{0}'.format(address.id))
                self.assertEqual(rv.status_code, 200)

                response = c.post(
                    '/edit-address/{0}'.format(address.id),
                    data={
                        'name': 'Some Other Dude',
                        'street': 'Street',
                        'streetbis': 'StreetBis',
                        'zip': 'zip',
                        'city': 'City',
                        'email': 'email@example.com',
                        'phone': '1234567890',
                        'country': self.available_countries[0].id,
                        'subdivision': self.Country(
                            self.available_countries[0]).subdivisions[0].id,
                    }
                )
                self.assertEqual(response.status_code, 302)

                rv = c.get('/view-address')
                self.assertIn('Some Other Dude', rv.data)
                with self.assertRaises(AssertionError):
                    self.assertIn(data['name'], rv.data)

                # Now remove the address.
                rv = c.post(
                    '/remove-address/{0}'
                    .format(address.id)
                )
                self.assertEqual(rv.status_code, 302)
                self.assertEqual(
                    len(self.registered_user.party.addresses),
                    0
                )

    def test_0045_wishlist(self):
        """
        Tests the wishlist.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            self.create_test_products()
            app = self.get_app()

            with app.test_client() as c:
                # Guests will be redirected.
                rv = c.post(
                    '/wishlists',
                    data={
                        'name': 'Testlist'
                    }
                )
                self.assertEquals(rv.status_code, 302)

                self.login(c, 'email@example.com', 'password')

                # No wishlists currently.
                self.assertEqual(
                    len(self.registered_user.wishlists),
                    0
                )
                rv = c.post(
                    '/wishlists',
                    data={
                        'name': 'Testlist'
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertEqual(
                    len(self.registered_user.wishlists),
                    1
                )
                rv = c.get('/wishlists')
                self.assertIn('Testlist', rv.data)

                # Remove this wishlist.
                rv = c.delete(
                    '/wishlists/{0}'.format(
                        self.registered_user.wishlists[0].id
                    )
                )
                self.assertEqual(rv.status_code, 200)

                # Now add products.
                product1, = self.ProductTemplate.search([
                    ('name', '=', 'product 1')
                ])
                product2, = self.ProductTemplate.search([
                    ('name', '=', 'product 2')
                ])

                # Adding a product without creating a wishlist
                # creates a wishlist automatically.
                rv = c.post(
                    'wishlists/products',
                    data={
                        'product': product1.products[0].id,
                        'action': 'add'
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertEqual(len(self.registered_user.wishlists), 1)
                self.assertEqual(
                    len(self.registered_user.wishlists[0].products),
                    1
                )
                rv = c.get(
                    '/wishlists/{0}'
                    .format(self.registered_user.wishlists[0].id)
                )
                self.assertIn(product1.name, rv.data)

                # Add another product.
                rv = c.post(
                    'wishlists/products',
                    data={
                        'product': product2.products[0].id,
                        'action': 'add',
                        'wishlist': self.registered_user.wishlists[0].id
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertEqual(
                    len(self.registered_user.wishlists[0].products),
                    2
                )

                rv = c.get(
                    '/wishlists/{0}'
                    .format(self.registered_user.wishlists[0].id)
                )
                self.assertIn(product2.name, rv.data)

                # Remove a product
                rv = c.post(
                    'wishlists/products',
                    data={
                        'product': product2.products[0].id,
                        'wishlist': self.registered_user.wishlists[0].id,
                        'action': 'remove'
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertEqual(
                    len(self.registered_user.wishlists[0].products),
                    1
                )

                rv = c.get(
                    '/wishlists/{0}'
                    .format(self.registered_user.wishlists[0].id)
                )
                self.assertNotIn(product2.name, rv.data)

    @unittest.skip("Not implemented yet.")
    def test_0050_profile(self):
        """
        Test the profile.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                # Without login.
                rv = c.get('/me')
                self.assertEqual(rv.status_code, 302)

                self.login(c, 'email@example.com', 'password')

                rv = c.post(
                    '/me',
                    data={
                        'display_name': 'Pritish C',
                        'timezone': 'Asia/Kolkata'
                    }
                )
                self.assertEqual(rv.status_code, 302)
                rv = c.get('/me')
                self.assertIn('Pritish C', rv.data)
                self.assertIn('Asia/Kolkata', rv.data)

    def test_0055_guest_checkout(self):
        """
        Test for guest checkout.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            self.create_test_products()
            app = self.get_app()

            product1, = self.ProductTemplate.search([
                ('name', '=', 'product 1')
            ])
            product2, = self.ProductTemplate.search([
                ('name', '=', 'product 2')
            ])

            country = self.Country(self.available_countries[0])
            subdivision = country.subdivisions[0]

            with app.test_client() as c:
                rv = c.post(
                    '/cart/add',
                    data={
                        'product': product1.products[0].id,
                        'quantity': 5
                    }
                )
                self.assertEqual(rv.status_code, 302)

                rv = c.get('/checkout/sign-in')
                self.assertEqual(rv.status_code, 200)

                # Trying to checkout with a registered email.
                # Should fail.
                rv = c.post(
                    '/checkout/sign-in',
                    data={
                        'email': 'email@example.com'
                    }
                )
                self.assertEqual(rv.status_code, 200)
                self.assertIn(
                    '{0}'.format(self.registered_user.email),
                    rv.data
                )
                self.assertIn(
                    'is tied to an existing account',
                    rv.data
                )

                # Now with a new email.
                rv = c.post(
                    '/checkout/sign-in',
                    data={
                        'email': 'new@example.com',
                        'checkout_mode': 'guest'
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertTrue(
                    rv.location.endswith('/checkout/shipping-address')
                )

                # Shipping address page should render.
                rv = c.get('/checkout/shipping-address')
                self.assertEqual(rv.status_code, 200)

                # Copied from nereid-checkout - adding shipping address.
                rv = c.post(
                    '/checkout/shipping-address',
                    data={
                        'name': 'Sharoon Thomas',
                        'street': 'Biscayne Boulevard',
                        'streetbis': 'Apt. 1906, Biscayne Park',
                        'zip': 'FL33137',
                        'city': 'Miami',
                        'phone': '1234567890',
                        'country': country.id,
                        'subdivision': subdivision.id,
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertTrue(
                    rv.location.endswith('/checkout/validate-address')
                )

                # Copied from nereid-checkout - adding billing address.
                rv = c.post(
                    '/checkout/billing-address',
                    data={
                        'name': 'Sharoon Thomas',
                        'street': 'Biscayne Boulevard',
                        'streetbis': 'Apt. 1906, Biscayne Park',
                        'zip': 'FL33137',
                        'city': 'Miami',
                        'phone': '1234567890',
                        'country': country.id,
                        'subdivision': subdivision.id,
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertTrue(
                    rv.location.endswith('/checkout/payment')
                )

                with Transaction().set_context(company=self.company.id):
                    self._create_auth_net_gateway_for_site()

                # Try to pay using credit card
                rv = c.post(
                    '/checkout/payment',
                    data={
                        'owner': 'Joe Blow',
                        'number': '4111111111111111',
                        'expiry_year': '2018',
                        'expiry_month': '01',
                        'cvv': '911',
                        'add_card_to_profiles': 'y',
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertTrue('/order/' in rv.location)
                self.assertTrue('access_code' in rv.location)

                sale, = self.Sale.search([('state', '=', 'confirmed')])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)

                rv = c.get('/order/{0}'.format(sale.id))
                self.assertEqual(rv.status_code, 302)  # Orders page redirect

    def test_0060_registered_checkout(self):
        """
        Test for registered user checkout.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            self.create_test_products()
            app = self.get_app()

            product1, = self.ProductTemplate.search([
                ('name', '=', 'product 1')
            ])
            product2, = self.ProductTemplate.search([
                ('name', '=', 'product 2')
            ])

            country = self.Country(self.available_countries[0])
            subdivision = country.subdivisions[0]

            with app.test_client() as c:
                rv = c.post(
                    '/cart/add',
                    data={
                        'product': product1.products[0].id,
                        'quantity': 5
                    }
                )
                self.assertEqual(rv.status_code, 302)

                # Now sign in to checkout.
                rv = c.post(
                    '/checkout/sign-in',
                    data={
                        'email': 'email@example.com',
                        'password': 'password',
                        'checkout_mode': 'account'
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertTrue(rv.location.endswith('/shipping-address'))

                # Shipping address page should render.
                rv = c.get('/checkout/shipping-address')
                self.assertEqual(rv.status_code, 200)

                # Copied from nereid-checkout - adding shipping address.
                rv = c.post(
                    '/checkout/shipping-address',
                    data={
                        'name': 'Sharoon Thomas',
                        'street': 'Biscayne Boulevard',
                        'streetbis': 'Apt. 1906, Biscayne Park',
                        'zip': 'FL33137',
                        'city': 'Miami',
                        'phone': '1234567890',
                        'country': country.id,
                        'subdivision': subdivision.id,
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertTrue(
                    rv.location.endswith('/checkout/validate-address')
                )

                # Copied from nereid-checkout - adding billing address.
                rv = c.post(
                    '/checkout/billing-address',
                    data={
                        'name': 'Sharoon Thomas',
                        'street': 'Biscayne Boulevard',
                        'streetbis': 'Apt. 1906, Biscayne Park',
                        'zip': 'FL33137',
                        'city': 'Miami',
                        'phone': '1234567890',
                        'country': country.id,
                        'subdivision': subdivision.id,
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertTrue(
                    rv.location.endswith('/checkout/payment')
                )

                with Transaction().set_context(company=self.company.id):
                    self._create_auth_net_gateway_for_site()

                # Try to pay using credit card
                rv = c.post(
                    '/checkout/payment',
                    data={
                        'owner': 'Joe Blow',
                        'number': '4111111111111111',
                        'expiry_year': '2018',
                        'expiry_month': '01',
                        'cvv': '911',
                        'add_card_to_profiles': '',
                    }
                )
                self.assertEqual(rv.status_code, 302)
                self.assertTrue('/order/' in rv.location)
                self.assertTrue('access_code' in rv.location)

                sale, = self.Sale.search([('state', '=', 'confirmed')])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)

                rv = c.get('/order/{0}'.format(sale.id))
                self.assertEqual(rv.status_code, 200)

                rv = c.get(
                    '/order/{0}?access_code={1}'
                    .format(sale.id, sale.guest_access_code)
                )
                self.assertEqual(rv.status_code, 200)

    def test_0065_password_reset(self):
        """
        Test for password reset.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:

                # Resetting without login
                rv = c.get('/reset-account')
                self.assertEqual(rv.status_code, 200)

                # Resetting through email
                response = c.post(
                    '/reset-account',
                    data={
                        'email': 'email@example.com'
                    }
                )
                self.assertEqual(response.status_code, 302)

                # Login after requesting activation code.
                self.login(c, 'email@example.com', 'password')

            # Reset properly.
            with app.test_client() as c:
                response = c.post(
                    '/reset-account',
                    data={
                        'email': 'email@example.com'
                    }
                )
                self.assertEqual(response.status_code, 302)

                # Resetting with an invalid code.
                # Login with new pass should be rejected.

                invalid = 'badcode'
                response = c.post(
                    '/new-password/{0}/{1}'.format(
                        self.registered_user.id,
                        invalid
                    ),
                    data={
                        'password': 'reset-pass',
                        'confirm': 'reset-pass'
                    }
                )
                self.assertEqual(response.status_code, 302)

                response = c.post(
                    '/login',
                    data={
                        'email': 'email@example.com',
                        'password': 'reset-pass'
                    }
                )
                # rejection
                self.assertEqual(response.status_code, 200)

                # Now do it with the right code.
                # This time, login with old pass should be rejected.

                response = c.post(
                    self.registered_user.get_reset_password_link(),
                    data={
                        'password': 'reset-pass',
                        'confirm': 'reset-pass'
                    }
                )
                self.assertEqual(response.status_code, 302)

                response = c.post(
                    '/login',
                    data={
                        'email': 'email@example.com',
                        'password': 'password'
                    }
                )
                self.assertEqual(response.status_code, 200)

                self.login(c, 'email@example.com', 'reset-pass')

    def test_0070_change_password(self):
        """
        Test for password change.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            data = {
                'party': self.party2.id,
                'display_name': 'Registered User',
                'email': 'email@example.com',
                'password': 'password',
                'company': self.company.id
            }

            with app.test_client() as c:
                response = c.get('/change-password')
                # Without login
                self.assertEqual(response.status_code, 302)

                # Try POST, but without login
                response = c.post('/change-password', data={
                    'password': data['password'],
                    'confirm': data['password']
                })
                self.assertEqual(response.status_code, 302)

                # Now login
                self.login(c, data['email'], data['password'])

                # Incorrect password confirmation
                response = c.post(
                    '/change-password',
                    data={
                        'password': 'new-password',
                        'confirm': 'oh-no-you-dont'
                    }
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue("must match" in response.data)

                # Send proper confirmation but without old password.
                response = c.post(
                    '/change-password',
                    data={
                        'password': 'new-pass',
                        'confirm': 'new-pass'
                    }
                )
                self.assertEqual(response.status_code, 200)

                # Send proper confirmation with wrong old password
                response = c.post(
                    '/change-password',
                    data={
                        'old_password': 'passw',
                        'password': 'new-pass',
                        'confirm': 'new-pass'
                    }
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(
                    'current password you entered is invalid' in response.data
                )

                # Do it right
                response = c.post(
                    '/change-password',
                    data={
                        'old_password': data['password'],
                        'password': 'new-pass',
                        'confirm': 'new-pass'
                    }
                )
                self.assertEqual(response.status_code, 302)

                # Check login with new pass
                c.get('/logout')
                self.login(c, data['email'], 'new-pass')

    def test_0075_products(self):
        """
        Tests product templates and variants.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                self.create_test_products()

                rv = c.get('/products')
                self.assertIn('product 1', rv.data)
                self.assertIn('product 2', rv.data)
                self.assertIn('product 3', rv.data)

                rv = c.get('/product/product-1')
                self.assertEqual(rv.status_code, 200)
                self.assertIn('product 1', rv.data)

                template1, = self.ProductTemplate.search([
                    ('name', '=', 'product 1')
                ])
                template1.active = False
                template1.save()

                rv = c.get('/product/product-1')
                self.assertEqual(rv.status_code, 404)

    def test_0080_search_results(self):
        """
        Test the search results template.
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()
            app = self.get_app()

            with app.test_client() as c:
                self.create_test_products()

                rv = c.get('/search?q=product')
                self.assertIn('product 1', rv.data)
                self.assertIn('product-1', rv.data)
                self.assertIn('product 2', rv.data)
                self.assertIn('product-2', rv.data)
                self.assertIn('product 3', rv.data)
                self.assertIn('product-3', rv.data)
