from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, I18N_DOMAIN, ManagePricelists, ManageBika, PRICELIST_TYPES, CLIENT_TYPES, PROJECTNAME
import sys
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('Type',
        required = 1,
        vocabulary = PRICELIST_TYPES,
        widget = SelectionWidget(
            label = _("Pricelist for"),
        ),
    ),
    StringField('ClientType',
        required = 1,
        vocabulary = CLIENT_TYPES,
        widget = SelectionWidget(
            label = _("Pricing model"),
        ),
    ),
    FixedPointField('Discount',
        widget = DecimalWidget(
            label = _("Discount %"),
            description = _("Enter discount percentage value"),
        ),
    ),
    BooleanField('Descriptions',
        default = False,
        widget = BooleanWidget(
            label = _("Include descriptions"),
            description = _("Select if the descriptions should be included"),
        ),
    ),
    DateTimeField('StartDate',
        required = 1,
        with_time = False,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = _("Valid from"),
            show_hm = False,
        ),
    ),
    DateTimeField('EndDate',
        required = 1,
        with_time = False,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = _("Valid until"),
            show_hm = False,
        ),
    ),
    TextField('Notes',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = _("Notes")
        ),
    ),
),
)

class Pricelist(BaseFolder):
    security = ClassSecurityInfo()
    archetype_name = 'Pricelist'
    schema = schema
    content_icon = 'pricelist.png'
    allowed_content_types = ('PricelistLineItem',)
    immediate_view = 'base_view'
    use_folder_tabs = 0
    global_allow = 0
    filter_content_types = 1

    actions = (

        {'id': 'printpricelist',
         'name': 'Print pricelist',
         'action': 'string:${object_url}/pricelist_print',
         'permissions': (permissions.View,),
        },
        {'id': 'emailpricelist',
         'name': 'Email pricelist',
         'action': 'string:${object_url}/pricelist_email',
         'permissions': (permissions.View,),
        },
    )

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    security.declareProtected(ManagePricelists, 'create_price_list')
    def create_price_list(self):
        """ Create price list
        """
        for p in self.portal_catalog(portal_type = self.getType()):
            obj = p.getObject()
            item_id = self.generateUniqueId('PricelistLineItem')
            self.invokeFactory(id = item_id, type_name = 'PricelistLineItem')
            item = self._getOb(item_id)
            itemDescription = None
            itemAccredited = False
            if not cmp(self.getType(), 'LabProduct'):
                if str(obj.getVolume()) or obj.getUnit():
                    print_detail = ' ('
                if str(obj.getVolume()):
                    print_detail = print_detail + str(obj.getVolume())
                if str(obj.getUnit()):
                    print_detail = print_detail + str(obj.getUnit())
                if print_detail:
                    print_detail = print_detail + ')'
                    itemTitle = obj.Title() + print_detail
                else:
                    itemTitle = obj.Title()
                if self.getDescriptions():
                    itemDescription = obj.Description()
            else:
                if str(obj.getUnit()):
                    print_detail = ' (' + str(obj.getUnit()) + ')'
                    itemTitle = obj.Title() + print_detail
                else:
                    itemTitle = obj.Title()
                if self.getDescriptions():
                    itemDescription = obj.Description()
                itemAccredited = obj.getAccredited()
            if self.getType() == 'AnalysisService':
                cat = obj.getCategoryName()
                if self.getClientType() == 'corporate':
                    if obj.getCorporatePrice():
                        price = obj.getCorporatePrice()
                        totalprice = obj.getTotalCorporatePrice()
                        vat = totalprice - price
                    else:
                        price = None
                        totalprice = None
                        vat = None
                else:
                    if obj.getPrice():
                        price = obj.getPrice()
                        totalprice = obj.getTotalPrice()
                        vat = totalprice - price
                    else:
                        totalprice = None
                        price = None
                        vat = None
            else:
                cat = None
                if obj.getPrice():
                    price = obj.getPrice()
                    totalprice = obj.getTotalPrice()
                    vat = totalprice - price
                else:
                    price = None
                    totalprice = None
                    vat = None

            if self.getDiscount():
                price = price * (100.0 - self.getDiscount()) / 100.0
                totalprice = totalprice * (100 - self.getDiscount()) / 100.0
                vat = totalprice - price

            item.edit(
                title = itemTitle,
                ItemDescription = itemDescription,
                Accredited = itemAccredited,
                Subtotal = price,
                VAT = vat,
                Total = totalprice,
                CategoryName = cat,
            )
            item.processForm()
        self.REQUEST.RESPONSE.redirect('base_view')

    security.declareProtected(permissions.ModifyPortalContent,
                              'processForm')
    def processForm(self, data = 1, metadata = 0, REQUEST = None, values = None):
        """ Override BaseObject.processForm so that we can create
            invoice lineitems once the form is filled in
        """
        BaseFolder.processForm(self, data = data, metadata = metadata,
            REQUEST = REQUEST, values = values)
        self.create_price_list()


registerType(Pricelist, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('edit', 'syndication', 'references',
                       'metadata', 'localroles'):
            a['visible'] = 0
    return fti
