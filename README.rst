=============
Feel Rested
=============

Extends Django REST Framework to create instant full-featured GET APIs with fields, filters, offset,
limit, etc., including the ability to drill down into chained objects (foreignKey, manyToMany, oneToOne fields).

You create just one simple view per API; you do not need to create separate serializers for the
chained objects.


Quickstart
----------
Example adapted from code in tests.py.

1. Install the package:
    ``pip install --index-url https://pypi.kiiroo.com/pypi feel-rested``


2. Create a view that's a subclass of DrillDownAPIView (use your own models; "Invoice" is just an example)::

    from feel_rested.views import BaseApiView

    class InvoiceList(BaseApiView):
        """A GET API for Invoice objects"""
        # Primary model for the API (required)
        model = Invoice

        # Global throttle for the API. Defaults to 1000. If your query hits MAX_RESULTS,
        # this is noted in X-Query_Warning in the response header.
        MAX_RESULTS = 5000

        # The picky flag defaults to False; if True, then any unidentifiable param in the
        # request will result in an error.
        #picky = True

        # Optional list of chained foreignKey, manyToMany, and oneToOne objects
        # your users can drill down into -- note that you do not need to build
        # separate serializers for these; DrilldownAPI builds them dynamically.
        drilldowns = ['client__profile', 'salesperson__profile', 'items']

        # Optional list of fields to ignore if they appear in the request
        ignore = ['fakefield']

        # Optional list of fields that your users are not allowed to
        # see or query
        hide = ['salesperson__commission_pct']


3. In urls.py, create a URL for the view:
    ``url(r'^invoices/$', InvoiceList.as_view(), name='invoices'),``

4. Start running queries! Some of the things you can do:

* Limit and offset:
    ``/invoices/?limit=10&offset=60``

    Does just what you'd expect. The total number of results is returned in a custom header code: ``X-Total-Count: 2034``

* Specify fields to include, including "drilldown" fields:
    ``/invoices/?fields=id,client.profile.first_name,client.profile.last_name``

    Returns invoices showing just the invoice ID and the client's first and last name.

* Filter on fields:
    ``/invoices/?total__gte=100&salesperson.last_name__iexact=smith``

    Lists invoices where total >= $100 and salesperson is "Smith".

* Filter on dates and booleans:
    ``/invoices/?paid=false&bill_date__lt=2014-05-01``


    Dates are formatted YYYY-MM-DD and booleans may be true, True, false, or False.

* Use the 'ALL' keyword to return all fields in an object:
    ``/invoices/?fields=salesperson.ALL``

    Lists the salesperson for each invoice; will display all salesperson fields
    EXCEPT commission_pct which is in the "hide" list in the API above.

* Use order_by, including - sign for reverse:
    ``/invoices/?order_by=client.profile.last_name,-amount``

    Returns invoices ordered by associated client's last name, from highest to lowest amount.

Total number of results for each query (before applying limit and offset) are returned in a custom header code:
    ``X-Total-Count: 2034``


Errors and warnings are also returned in a custom header code. Errors get status 400; warnings are status 200.
    ``X-Query_Error: error text``
    ``X-Query_Warning: warning text``

Also supports format parameter, e.g. ?format=json

POST requests
-------------
DrillDownAPIView overrides the Django REST Framework's get() method. It does not affect post() and other methods
at all, so your DrillDownAPIView class may include a standard Django REST Framework post() method.

Solutions for Common Problems
-----------------------------
* Access Control:
    In your API view, override the get() method and add your access control to it::

        @method_decorator(accounting_permission_required)
        def get(self, request):
            return super(InvoiceList, self).get(request)


* Custom Queries:
    Assume that invoices > $1000 require prior authorization, and you'd like to support that as a simple query:

    ``/invoices/?requires_authorization=True``

    1. Add your field to the ignore list in the API view:
        ``ignore = ['requires_authorizaton']``

    2. Add the logic for handling the new filter to ``get_base_query()`` in the API view::

        def get_base_query(self):
            qs = Invoice.objects.all()
            if self.request.GET.get('requires_authorizaton'):
                requires_authorization = self.request.GET['requires_authorization']
                if requires_authorization == 'True':
                    qs = qs.filter(total__gt=1000)
                elif requires_authorization == 'False':
                    qs = qs.exclude(total__gt=1000)
            return qs

    Now you can query for ``requires_authorization=True`` or ``requires_authorization=False``.
