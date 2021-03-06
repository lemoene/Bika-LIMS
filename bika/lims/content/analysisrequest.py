"""The request for analysis by a client. It contains analysis instances.

$Id: AnalysisRequest.py 2567 2010-09-27 14:51:15Z anneline $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import delete_objects
from DateTime import DateTime
from Products.ATContentTypes.content import schemata
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.ATExtensions.widget.records import RecordsWidget
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import shasattr
from Products.CMFCore import permissions
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from bika.lims.browser.fields import ARAnalysesField
from bika.lims.config import I18N_DOMAIN, PROJECTNAME, \
    ManageInvoices
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.utils import sortable_title, generateUniqueId
from decimal import Decimal
from email.Utils import formataddr
from types import ListType, TupleType
from zope.app.component.hooks import getSite
from zope.interface import implements
import sys
import time
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('RequestID',
        required = 1,
        searchable = True,
        widget = StringWidget(
            label = 'Request ID',
            label_msgid = 'label_requestid',
            description = 'The ID assigned to the client''s request by the lab',
            description_msgid = 'help_requestid',
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden'},
        ),
    ),
    ReferenceField('Contact',
        required = 1,
        vocabulary = 'getContactsDisplayList',
        default_method = 'getContactUIDForUser',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Contact',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestContact',
    ),
    ReferenceField('CCContact',
        multiValued = 1,
        vocabulary = 'getContactsDisplayList',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Contact',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestCCContact',
    ),
    ReferenceField('Attachment',
        multiValued = 1,
        allowed_types = ('Attachment',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestAttachment',
    ),
    StringField('CCEmails',
        widget = StringWidget(
            label = 'CC Emails',
            label_msgid = 'label_ccemails',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Sample',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Sample',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestSample',
    ),
    ARAnalysesField('Analyses',
        required = 1,
    ),
    StringField('ClientOrderNumber',
        searchable = True,
        widget = StringWidget(
            label = 'Client Order ID',
            label_msgid = 'label_client_order_id',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Invoice',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Invoice',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestInvoice',
    ),
    ReferenceField('Profile',
        allowed_types = ('ARProfile',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisRequestProfile',
    ),
    BooleanField('InvoiceExclude',
        default = False,
        widget = BooleanWidget(
            label = "Invoice Exclude",
            label_msgid = "label_invoice_exclude",
            description = "Select if analyses to be excluded from invoice",
            description_msgid = 'help_invoiceexclude',
        ),
    ),
    BooleanField('ReportDryMatter',
        default = False,
        widget = BooleanWidget(
            label = "Report as dry matter",
            label_msgid = "label_report_dry_matter",
            description = "Select if result is to be reported as dry matter",
            description_msgid = 'help_report_dry_matter',
        ),
    ),
    DateTimeField('DateRequested',
        required = 1,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = 'Date requested',
            label_msgid = 'label_daterequested',
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateReceived',
        widget = DateTimeWidget(
            label = 'Date received',
            label_msgid = 'label_datereceived',
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DatePublished',
        widget = DateTimeWidget(
            label = 'Date published',
            label_msgid = 'label_datepublished',
            visible = {'edit':'hidden'},
        ),
    ),
    TextField('Notes',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = 'Notes'
        ),
    ),
    FixedPointField('MemberDiscount',
        default_method = 'getDefaultMemberDiscount',
        widget = DecimalWidget(
            label = 'Member discount %',
            label_msgid = 'label_memberdiscount_percentage',
            description = 'Enter percentage value eg. 33.0',
            description_msgid = 'help_memberdiscount_percentage',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ComputedField('ClientUID',
        expression = 'here.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ClientReference',
        expression = 'here.getSample() and here.getSample().getClientReference()' ,
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ClientSampleID',
        expression = 'here.getSample() and here.getSample().getClientSampleID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SampleTypeTitle',
        expression = "here.getSample() and here.getSample().getSampleType() and here.getSample().getSampleType().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SamplePointTitle',
        expression = "here.getSample() and here.getSample().getSamplePoint() and here.getSample().getSamplePoint().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('SampleUID',
        expression = 'here.getSample() and here.getSample().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ContactUID',
        expression = 'here.getContact() and here.getContact().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ProfileUID',
        expression = 'here.getProfile( and here.getProfile().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

schema['title'].required = False

class AnalysisRequest(BaseFolder):
    implements(IAnalysisRequest)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _has_dependant_calcs = False

    def hasBeenInvoiced(self):
        if self.getInvoice():
            return True
        else:
            return False

    def Title(self):
        """ Return the Request ID as title """
        return self.getRequestID()

    security.declarePublic('generateUniqueId')
    def generateUniqueId (self, type_name, batch_size = None):
        return generateUniqueId(self, type_name, batch_size)

    def getDefaultMemberDiscount(self):
        """ compute default member discount if it applies """
        if hasattr(self, 'getMemberDiscountApplies'):
            if self.getMemberDiscountApplies():
                plone = getSite()
                settings = plone.bika_setup
                return settings.getMemberDiscount()
            else:
                return "0.00"

    security.declareProtected(View, 'getResponsible')
    def getResponsible(self):
        """ Return all manager info of responsible departments """
        managers = {}
        departments = []
        for analysis in self.objectValues('Analysis'):
            department = analysis.getService().getDepartment()
            if department is None:
                continue
            department_id = department.getId()
            if department_id in departments:
                continue
            departments.append(department_id)
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if not managers.has_key(manager_id):
                managers[manager_id] = {}
                managers[manager_id]['name'] = manager.getFullname()
                managers[manager_id]['email'] = manager.getEmailAddress()
                managers[manager_id]['phone'] = manager.getBusinessPhone()
                managers[manager_id]['signature'] = '%s/Signature' % manager.absolute_url()
                managers[manager_id]['dept'] = ''
            mngr_dept = managers[manager_id]['dept']
            if mngr_dept:
                mngr_dept += ', '
            mngr_dept += department.Title()
            managers[manager_id]['dept'] = mngr_dept
        mngr_keys = managers.keys()
        mngr_info = {}
        mngr_info['ids'] = mngr_keys
        mngr_info['dict'] = managers

        return mngr_info

    security.declareProtected(View, 'getResponsible')
    def getManagers(self):
        """ Return all managers of responsible departments """
        manager_ids = []
        manager_list = []
        departments = []
        for analysis in self.objectValues('Analysis'):
            department = analysis.getService().getDepartment()
            if department is None:
                continue
            department_id = department.getId()
            if department_id in departments:
                continue
            departments.append(department_id)
            manager = department.getManager()
            if manager is None:
                continue
            manager_id = manager.getId()
            if not manager_id in manager_ids:
                manager_ids.append(manager_id)
                manager_list.append(manager)

        return manager_list

    security.declareProtected(View, 'getLate')
    def getLate(self):
        """ return True if any analyses are late """
        wf_tool = getToolByName(self, 'portal_workflow')
        review_state = wf_tool.getInfoFor(self, 'review_state', '')
        if review_state in ['sample_due', 'published']:
            return False

        now = DateTime()
        for analysis in self.objectValues('Analysis'):
            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            if review_state == 'published':
                continue
            if analysis.getDueDate() < now:
                return True
        return False

    security.declareProtected(View, 'getBillableItems')
    def getBillableItems(self):
        """ Return all items except those in 'not_requested' state """
        wf_tool = getToolByName(self, 'portal_workflow')
        items = []
        for analysis in self.objectValues('Analysis'):
            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            if review_state != 'not_requested':
                items.append(analysis)
        return items

    security.declareProtected(View, 'getSubtotal')
    def getSubtotal(self):
        """ Compute Subtotal
            XXX invoked MANY times during a single AR's creation
        """
        return sum(
            [Decimal(obj.getService() and obj.getService().getPrice() or 0) \
            for obj in self.getBillableItems()])

    security.declareProtected(View, 'getVAT')
    def getVAT(self):
        """ Compute VAT """
        return Decimal(self.getTotalPrice()) - Decimal(self.getSubtotal())

    security.declareProtected(View, 'getTotalPrice')
    def getTotalPrice(self):
        """ Compute TotalPrice """
        billable = self.getBillableItems()
        TotalPrice = Decimal(0, 2)
        for item in billable:
            service = item.getService()
            if not service:
                # XXX invokeFactory can cause us to be catalogued before we're ready.
                return Decimal(0, 2)
            itemPrice = Decimal(service.getPrice() or 0)
            VAT = Decimal(service.getVAT() or 0)
            TotalPrice += Decimal(itemPrice) * (Decimal(1, 2) + VAT)
        return TotalPrice
    getTotal = getTotalPrice

    def setDryMatterResults(self):
        """ get results of analysis requiring DryMatter reporting """
        analyses = []
        DryMatter = None
        settings = getToolByName(self, 'bika_setup')
        dry_service = settings.getDryMatterService()
        for analysis in self.getAnalyses(full_objects = True):
            if analysis.getReportDryMatter():
                analyses.append(analysis)
            try:
                if analysis.getServiceUID() == dry_service.UID():
                    DryMatter = Decimal(analysis.getResult())
            except:
                DryMatter = None

        for analysis in analyses:
            if DryMatter:
                try:
                    wet_result = Decimal(analysis.getResult())
                except:
                    wet_result = None
            if DryMatter and wet_result:
                dry_result = '%.2f' % ((wet_result / DryMatter) * 100)
            else:
                dry_result = None
            analysis.setResultDM(dry_result)

        return

    security.declareProtected(ManageInvoices, 'issueInvoice')
    def issueInvoice(self, REQUEST = None, RESPONSE = None):
        """ issue invoice
        """
        # check for an adhoc invoice batch for this month
        now = DateTime()
        batch_month = now.strftime('%b %Y')
        batch_title = '%s - %s' % (batch_month, 'ad hoc')
        invoice_batch = None
        for b_proxy in  self.portal_catalog(portal_type = 'InvoiceBatch',
                                    Title = batch_title):
            invoice_batch = b_proxy.getObject()
        if not invoice_batch:
            first_day = DateTime(now.year(), now.month(), 1)
            start_of_month = first_day.earliestTime()
            last_day = first_day + 31
            while last_day.month() != now.month():
                last_day = last_day - 1
            end_of_month = last_day.latestTime()

            invoices = self.invoices
            batch_id = invoices.generateUniqueId('InvoiceBatch')
            invoices.invokeFactory(id = batch_id, type_name = 'InvoiceBatch')
            invoice_batch = invoices._getOb(batch_id)
            invoice_batch.edit(
                title = batch_title,
                BatchStartDate = start_of_month,
                BatchEndDate = end_of_month,
            )
            invoice_batch.processForm()

        client_uid = self.getClientUID()
        invoice_batch.createInvoice(client_uid, [self, ])

        RESPONSE.redirect(
                '%s/analysisrequest_invoice' % self.absolute_url())

    security.declarePublic('printInvoice')
    def printInvoice(self, REQUEST = None, RESPONSE = None):
        """ print invoice
        """
        invoice = self.getInvoice()
        invoice_url = invoice.absolute_url()
        RESPONSE.redirect('%s/invoice_print' % invoice_url)

    def addARAttachment(self, REQUEST = None, RESPONSE = None):
        """ Add the file as an attachment
        """
        workflow = getToolByName(self, 'portal_workflow')

        this_file = self.REQUEST.form['AttachmentFile_file']
        if self.REQUEST.form.has_key('Analysis'):
            analysis_uid = self.REQUEST.form['Analysis']
        else:
            analysis_uid = None

        attachmentid = self.generateUniqueId('Attachment')
        self.aq_parent.invokeFactory(id = attachmentid, type_name = "Attachment")
        attachment = self.aq_parent._getOb(attachmentid)
        attachment.edit(
            AttachmentFile = this_file,
            AttachmentType = self.REQUEST.form['AttachmentType'],
            AttachmentKeys = self.REQUEST.form['AttachmentKeys'])
        attachment.processForm()
        attachment.reindexObject()

        if analysis_uid:
            tool = getToolByName(self, REFERENCE_CATALOG)
            analysis = tool.lookupObject(analysis_uid)
            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)
            if workflow.getInfoFor(analysis, 'review_state') == 'attachment_due':
                workflow.doActionFor(analysis, 'attach')
        else:
            others = self.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())

            self.setAttachment(attachments)

        RESPONSE.redirect(
                '%s/manage_results' % self.absolute_url())

    def delARAttachment(self, REQUEST = None, RESPONSE = None):
        """ delete the attachment """
        tool = getToolByName(self, REFERENCE_CATALOG)
        if self.REQUEST.form.has_key('ARAttachment'):
            attachment_uid = self.REQUEST.form['ARAttachment']
            attachment = tool.lookupObject(attachment_uid)
            parent = attachment.getRequest()
        elif self.REQUEST.form.has_key('AnalysisAttachment'):
            attachment_uid = self.REQUEST.form['AnalysisAttachment']
            attachment = tool.lookupObject(attachment_uid)
            parent = attachment.getAnalysis()

        others = parent.getAttachment()
        attachments = []
        for other in others:
            if not other.UID() == attachment_uid:
                attachments.append(other.UID())
        parent.setAttachment(attachments)
        client = attachment.aq_parent
        ids = [attachment.getId(), ]
        BaseFolder.manage_delObjects(client, ids, REQUEST)

        RESPONSE.redirect(
                '%s/manage_results' % self.absolute_url())

    security.declarePublic('getContactUIDForUser')
    def get_verifier(self):
        wtool = getToolByName(self, 'portal_workflow')
        mtool = getToolByName(self, 'portal_membership')

        verifier = None
        try:
            review_history = wtool.getInfoFor(self, 'review_history')
        except:
            return 'access denied'

        if not review_history:
            return 'no history'
        for items in  review_history:
            action = items.get('action')
            if action != 'verify':
                continue
            actor = items.get('actor')
            member = mtool.getMemberById(actor)
            verifier = member.getProperty('fullname')
            if verifier is None or verifier == '':
                verifier = actor
        return verifier

    security.declarePublic('getContactUIDForUser')
    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        r = self.portal_catalog(
            portal_type = 'Contact',
            getUsername = user_id
        )
        if len(r) == 1:
            return r[0].UID

    security.declarePublic('getCCDisplays')
    def getCCDisplays(self):
        """ get a string of titles of the contacts
        """
        cc_uids = ''
        cc_titles = ''
        for cc in self.getCCContact():
            if cc_uids:
                cc_uids = cc_uids + ', ' + cc.UID()
                cc_titles = cc_titles + ', ' + cc.Title()
            else:
                cc_uids = cc.UID()
                cc_titles = cc.Title()
        return [cc_uids, cc_titles]

    security.declareProtected(delete_objects, 'manage_delObjects')
    def manage_delObjects(self, ids = [], REQUEST = None):
        """ recalculate state from remaining analyses """
        BaseFolder.manage_delObjects(self, ids, REQUEST)
        #self._escalateWorkflowAction()

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

atapi.registerType(AnalysisRequest, PROJECTNAME)
