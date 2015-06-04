'''

    Test Base Case

    :copyright: (c) 2014-2015 by Openlabs Technologies & Consulting (P) LTD
    :license: GPLv3, see LICENSE for more details
'''
import random
import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta

import pycountry
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, CONTEXT
from nereid.testing import NereidTestCase
from trytond.transaction import Transaction
from trytond.config import config

config.set('database', 'path', '/tmp')


class BaseTestCase(NereidTestCase):
    """
    Base test Case for nereid webshop
    """
    def setUp(self):
        trytond.tests.test_tryton.install_module('nereid_webshop')

        self.FiscalYear = POOL.get('account.fiscalyear')
        self.Account = POOL.get('account.account')
        self.PaymentTerm = POOL.get('account.invoice.payment_term')
        self.Currency = POOL.get('currency.currency')
        self.Company = POOL.get('company.company')
        self.Party = POOL.get('party.party')
        self.Sale = POOL.get('sale.sale')
        self.Cart = POOL.get('nereid.cart')
        self.Product = POOL.get('product.product')
        self.ProductTemplate = POOL.get('product.template')
        self.Language = POOL.get('ir.lang')
        self.NereidWebsite = POOL.get('nereid.website')
        self.SaleChannel = POOL.get('sale.channel')
        self.Uom = POOL.get('product.uom')
        self.Country = POOL.get('country.country')
        self.Subdivision = POOL.get('country.subdivision')
        self.Currency = POOL.get('currency.currency')
        self.NereidUser = POOL.get('nereid.user')
        self.User = POOL.get('res.user')
        self.PriceList = POOL.get('product.price_list')
        self.Location = POOL.get('stock.location')
        self.Party = POOL.get('party.party')
        self.Locale = POOL.get('nereid.website.locale')
        self.Tax = POOL.get('account.tax')
        self.Node = POOL.get('product.tree_node')
        self.ArticleCategory = POOL.get('nereid.cms.article.category')
        self.Article = POOL.get('nereid.cms.article')
        self.Category = POOL.get('product.category')
        self.StaticFolder = POOL.get('nereid.static.folder')
        self.StaticFile = POOL.get('nereid.static.file')
        self.SaleConfig = POOL.get('sale.configuration')
        self.ProductNodeRelationship = POOL.get(
            'product.product-product.tree_node'
        )
        self.MenuItem = POOL.get('nereid.cms.menuitem')
        self.templates = {
            'shopping-cart.jinja':
                'Cart:{{ cart.id }},{{get_cart_size()|round|int}},'
                '{{cart.sale.total_amount}}',
            'product.jinja':
                '{{ product.name }}',
            'catalog/gift-card.html':
                '{{ product.id }}',
        }

    def _get_account_by_kind(self, kind, company=None, silent=True):
        """Returns an account with given spec

        :param kind: receivable/payable/expense/revenue
        :param silent: dont raise error if account is not found
        """

        if company is None:
            company, = self.Company.search([], limit=1)

        accounts = self.Account.search([
            ('kind', '=', kind),
            ('company', '=', company)
        ], limit=1)
        if not accounts and not silent:
            raise Exception("Account not found")
        return accounts[0] if accounts else False

    def _create_product_category(self, name, vlist):
        """
        Creates a product category

        Name is mandatory while other value may be provided as keyword
        arguments

        :param name: Name of the product category
        :param vlist: List of dictionaries of values to create
        """
        for values in vlist:
            values['name'] = name
        return self.Category.create(vlist)

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
        return self.ProductTemplate.create(vlist)[0]

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

    def _create_auth_net_gateway_for_site(self, method='credit_card'):
        """
        A helper function that creates the authorize.net gateway and assigns
        it to the websites.
        """
        PaymentGateway = POOL.get('payment_gateway.gateway')
        NereidWebsite = POOL.get('nereid.website')
        Journal = POOL.get('account.journal')

        cash_journal, = Journal.search([
            ('name', '=', 'Cash')
        ])
        self.account_cash, = self.Account.search([
            ('kind', '=', 'other'),
            ('name', '=', 'Main Cash'),
            ('company', '=', self.company.id)
        ])
        cash_journal.debit_account = self.account_cash
        cash_journal.credit_account = self.account_cash
        cash_journal.save()

        with Transaction().set_context({'use_dummy': True}):
            gatway = PaymentGateway(
                name='Authorize.net',
                journal=cash_journal,
                provider='dummy',
                method=method,
                authorize_net_login='327deWY74422',
                authorize_net_transaction_key='32jF65cTxja88ZA2',
            )
            gatway.save()

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gatway.id,
        })

    def _create_fiscal_year(self, date=None, company=None):
        """
        Creates a fiscal year and requried sequences
        """
        Sequence = POOL.get('ir.sequence')
        SequenceStrict = POOL.get('ir.sequence.strict')

        if date is None:
            date = datetime.date.today()

        if company is None:
            company, = self.Company.search([], limit=1)

        invoice_sequence, = SequenceStrict.create([{
            'name': '%s' % date.year,
            'code': 'account.invoice',
            'company': company,
        }])
        fiscal_year, = self.FiscalYear.create([{
            'name': '%s' % date.year,
            'start_date': date + relativedelta(month=1, day=1),
            'end_date': date + relativedelta(month=12, day=31),
            'company': company,
            'post_move_sequence': Sequence.create([{
                'name': '%s' % date.year,
                'code': 'account.move',
                'company': company,
            }])[0],
            'out_invoice_sequence': invoice_sequence,
            'in_invoice_sequence': invoice_sequence,
            'out_credit_note_sequence': invoice_sequence,
            'in_credit_note_sequence': invoice_sequence,
        }])
        self.FiscalYear.create_period([fiscal_year])
        return fiscal_year

    def _create_coa_minimal(self, company):
        """Create a minimal chart of accounts
        """
        AccountTemplate = POOL.get('account.account.template')
        account_create_chart = POOL.get(
            'account.create_chart', type="wizard")

        account_template, = AccountTemplate.search(
            [('parent', '=', None)]
        )

        session_id, _, _ = account_create_chart.create()
        create_chart = account_create_chart(session_id)
        create_chart.account.account_template = account_template
        create_chart.account.company = company
        create_chart.transition_create_account()

        receivable, = self.Account.search([
            ('kind', '=', 'receivable'),
            ('company', '=', company),
        ])
        payable, = self.Account.search([
            ('kind', '=', 'payable'),
            ('company', '=', company),
        ])
        create_chart.properties.company = company
        create_chart.properties.account_receivable = receivable
        create_chart.properties.account_payable = payable
        create_chart.transition_create_properties()

    def _create_payment_term(self):
        """Create a simple payment term with all advance
        """

        return self.PaymentTerm.create([{
            'name': 'Direct',
            'lines': [('create', [{'type': 'remainder'}])]
        }])

    def _create_countries(self, count=5):
        """
        Create some sample countries and subdivisions
        """
        for country in list(pycountry.countries)[0:count]:
            countries = self.Country.create([{
                'name': country.name,
                'code': country.alpha2,
            }])
            try:
                divisions = pycountry.subdivisions.get(
                    country_code=country.alpha2
                )
            except KeyError:
                pass
            else:
                for subdivision in list(divisions)[0:count]:
                    self.Subdivision.create([{
                        'country': countries[0].id,
                        'name': subdivision.name,
                        'code': subdivision.code,
                        'type': subdivision.type.lower(),
                    }])

    def _create_pricelists(self):
        """
        Create the pricelists
        """
        # Setup the pricelists
        self.party_pl_margin = Decimal('1.10')
        self.guest_pl_margin = Decimal('1.20')
        user_price_list, = self.PriceList.create([{
            'name': 'PL 1',
            'company': self.company.id,
            'lines': [
                ('create', [{
                    'formula': 'unit_price * %s' % self.party_pl_margin
                }])
            ],
        }])
        guest_price_list, = self.PriceList.create([{
            'name': 'PL 2',
            'company': self.company.id,
            'lines': [
                ('create', [{
                    'formula': 'unit_price * %s' % self.guest_pl_margin
                }])
            ],
        }])
        return guest_price_list.id, user_price_list.id

    def setup_defaults(self):
        """
        Setup the defaults
        """
        with Transaction().set_context(company=None):
            self.usd, = self.Currency.create([{
                'name': 'US Dollar',
                'code': 'USD',
                'symbol': '$',
            }])
            self.party, = self.Party.create([{
                'name': 'Openlabs',
            }])
            self.company, = self.Company.create([{
                'party': self.party.id,
                'currency': self.usd
            }])

        self.User.write(
            [self.User(USER)], {
                'main_company': self.company.id,
                'company': self.company.id,
            }
        )
        CONTEXT.update(self.User.get_preferences(context_only=True))

        # Create Fiscal Year
        self._create_fiscal_year(company=self.company.id)
        # Create Chart of Accounts
        self._create_coa_minimal(company=self.company.id)
        # Create a payment term
        payment_term, = self._create_payment_term()

        channel_price_list, user_price_list = self._create_pricelists()
        party1, = self.Party.create([{
            'name': 'Guest User',
        }])

        party2, = self.Party.create([{
            'name': 'Registered User',
            'sale_price_list': user_price_list,
        }])

        self.party2 = party2

        party3, = self.Party.create([{
            'name': 'Registered User 2',
        }])

        sale_config = self.SaleConfig(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.gift_card_method = 'order'
        sale_config.save()

        # Create users and assign the pricelists to them
        self.guest_user, = self.NereidUser.create([{
            'party': party1.id,
            'display_name': 'Guest User',
            'email': 'guest@openlabs.co.in',
            'password': 'password',
            'company': self.company.id,
        }])
        self.registered_user, = self.NereidUser.create([{
            'party': party2.id,
            'display_name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company.id,
        }])
        self.registered_user2, = self.NereidUser.create([{
            'party': party3.id,
            'display_name': 'Registered User 2',
            'email': 'email2@example.com',
            'password': 'password2',
            'company': self.company.id,
        }])

        self._create_countries()
        self.available_countries = self.Country.search([], limit=5)

        warehouse, = self.Location.search([
            ('type', '=', 'warehouse')
        ], limit=1)
        location, = self.Location.search([
            ('type', '=', 'storage')
        ], limit=1)
        en_us, = self.Language.search([('code', '=', 'en_US')])

        self.locale_en_us, = self.Locale.create([{
            'code': 'en_US',
            'language': en_us.id,
            'currency': self.usd.id,
        }])

        self.sale_tax, = self.Tax.create([{
            'name': 'Sales Tax',
            'description': 'Sales Tax',
            'type': 'percentage',
            'rate': Decimal('0.05'),  # Rate 5%
            'company': self.company.id,
            'invoice_account': self._get_account_by_kind('other').id,
            'credit_note_account': self._get_account_by_kind('other').id,
        }])

        self.channel, = self.SaleChannel.create([{
            'name': 'Default Channel',
            'price_list': channel_price_list,
            'warehouse': warehouse,
            'payment_term': payment_term,
            'company': self.company.id,
            'currency': self.company.currency.id,
            'invoice_method': 'order',
            'shipment_method': 'order',
            'source': 'webshop',
            'create_users': [('add', [USER])],
        }])

        self.User.set_preferences({'current_channel': self.channel})

        self.User.write(
            [self.User(USER)], {
                'main_company': self.company.id,
                'company': self.company.id,
                'current_channel': self.channel,
            }
        )

        self.default_node, = self.Node.create([{
            'name': 'root',
            'slug': 'root',
        }])
        self.default_menuitem, = self.MenuItem.create([{
            'type_': 'view',
            'title': 'Test Title'
        }])
        self.NereidWebsite.create([{
            'name': 'localhost',
            'channel': self.channel,
            'company': self.company.id,
            'application_user': USER,
            'default_locale': self.locale_en_us.id,
            'guest_user': self.guest_user,
            'countries': [('add', self.available_countries)],
            'currencies': [('add', [self.usd.id])],
            'homepage_menu': self.default_menuitem.id,
        }])

        # Create an article category
        article_categ, = self.ArticleCategory.create([{
            'title': 'Test Categ',
            'unique_name': 'test-categ',
        }])

        self.Article.create([{
            'title': 'Test Article',
            'uri': 'test-article',
            'content': 'Test Content',
            'sequence': 10,
            'categories': [('add', [article_categ.id])],
        }])

        # Product categories
        self.category, = self._create_product_category('categ1', [{}])
        self.category2, = self._create_product_category('categ2', [{}])
        self.category3, = self._create_product_category('categ3', [{}])

        self.Account.write(
            self.Account.search([]), {'party_required': True}
        )

    def login(self, client, username, password, assert_=True):
        """
        Login method.

        :param client: Instance of the test client
        :param username: The username, usually email
        :param password: The password to login
        :param assert_: Boolean value to indicate if the login has to be
                        ensured. If the login failed an assertion error would
                        be raised
        """
        rv = client.post(
            '/login', data={
                'email': username,
                'password': password,
            }
        )

        if assert_:
            self.assertEquals(rv.status_code, 302)
        return rv
