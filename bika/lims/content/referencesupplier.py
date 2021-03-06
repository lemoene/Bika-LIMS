"""ReferenceSupplier.

$Id: ReferenceSupplier.py 639 2007-03-20 09:35:32Z anneline $
"""

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.Archetypes.utils import DisplayList
from Products.CMFCore import permissions
from Products.CMFCore.permissions import ListFolderContents, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims.config import I18N_DOMAIN, PROJECTNAME, ManageReferenceSuppliers
from bika.lims.content.organisation import Organisation
from bika.lims.utils import generateUniqueId
from bika.lims.interfaces import IReferenceSupplier
from zope.interface import implements
from bika.lims import bikaMessageFactory as _

schema = Organisation.schema.copy()

schema['AccountNumber'].write_permission = ManageReferenceSuppliers

class ReferenceSupplier(Organisation):
    implements(IReferenceSupplier)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declarePublic('generateUniqueId')
    def generateUniqueId (self, type_name, batch_size = None):
        return generateUniqueId(self, type_name, batch_size)

##    security.declarePublic('getContactsDisplayList')
##    def getContactsDisplayList(self):
##        pairs = []
##        for contact in self.objectValues('SupplierContact'):
##            pairs.append((contact.UID(), contact.Title()))
##        return DisplayList(pairs)
##
##    security.declarePublic('getReferenceDefinitionDisplayList')
##    def getReferenceDefinitionDisplayList(self):
##        """ return all Reference Definitions """
##        defs = []
##        for st in self.portal_catalog(portal_type = 'ReferenceDefinition',
##                                      sort_on = 'sortable_title'):
##            defs.append((st.UID, st.Title))
##        return DisplayList(defs)

registerType(ReferenceSupplier, PROJECTNAME)
