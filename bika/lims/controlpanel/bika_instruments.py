from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IInstruments
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from operator import itemgetter

class InstrumentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    def __init__(self, context, request):
        super(InstrumentsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Instrument',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Add'):
                                    "createObject?type_name=Instrument"}
        self.title = _("Instruments")
        self.icon = "++resource++bika.lims.images/instrument_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
                   'Title': {'title': _('Instrument')},
                   'Type': {'title': _('Type')},
                   'Brand': {'title': _('Brand')},
                   'Model': {'title': _('Model')},
                   'ExpiryDate': {'title': _('Expiry Date')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['Title',
                         'Type',
                         'Brand',
                         'Model',
                         'ExpiryDate']},
            {'title': _('Active'), 'id':'active',
             'contentFilter': {'inactive_state': 'active'},
             'transitions': ['deactivate'],
             'columns': ['Title',
                         'Type',
                         'Brand',
                         'Model',
                         'ExpiryDate']},
            {'title': _('Dormant'), 'id':'inactive',
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': ['activate',],
             'columns': ['Title',
                         'Type',
                         'Brand',
                         'Model',
                         'ExpiryDate']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Type'] = obj.Type
            items[x]['Brand'] = obj.Brand
            items[x]['Model'] = obj.Model
            items[x]['ExpiryDate'] = obj.CalibrationExpiryDate and \
                obj.CalibrationExpiryDate.asdatetime().strftime("%d %b %Y") or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

schema = ATFolderSchema.copy()
class Instruments(ATFolder):
    implements(IInstruments)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Instruments, PROJECTNAME)
