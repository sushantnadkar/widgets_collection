from __future__ import unicode_literals
import frappe
import frappe.utils
from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys, login_via_oauth2, login_oauth_user as _login_oauth_user, redirect_post_login
import json
from frappe import _
from frappe.auth import LoginManager
from frappe.integrations.doctype.ldap_settings.ldap_settings import get_ldap_settings

def apply_context(context):

	# get settings from site config
	context["disable_signup"] = frappe.utils.cint(frappe.db.get_value("Website Settings", "Website Settings", "disable_signup"))

	for provider in ("google", "github", "facebook", "frappe"):
		if get_oauth_keys(provider):
			context["{provider}_login".format(provider=provider)] = get_oauth2_authorize_url(provider)
			context["social_login"] = True

	ldap_settings = get_ldap_settings()
	context["ldap_settings"] = ldap_settings

	return context

@frappe.whitelist(allow_guest=True)
def login_via_google(code, state):
	login_via_oauth2("google", code, state, decoder=json.loads)

@frappe.whitelist(allow_guest=True)
def login_via_github(code, state):
	login_via_oauth2("github", code, state)

@frappe.whitelist(allow_guest=True)
def login_via_facebook(code, state):
	login_via_oauth2("facebook", code, state)

@frappe.whitelist(allow_guest=True)
def login_via_frappe(code, state):
	login_via_oauth2("frappe", code, state, decoder=json.loads)

@frappe.whitelist(allow_guest=True)
def login_oauth_user(data=None, provider=None, state=None, email_id=None, key=None, generate_login_token=False):
	if not ((data and provider and state) or (email_id and key)):
		frappe.respond_as_web_page(_("Invalid Request"), _("Missing parameters for login"), http_status_code=417)
		return

	_login_oauth_user(data, provider, state, email_id, key, generate_login_token)

@frappe.whitelist(allow_guest=True)
def login_via_token(login_token):
	sid = frappe.cache().get_value("login_token:{0}".format(login_token), expires=True)
	if not sid:
		frappe.respond_as_web_page(_("Invalid Request"), _("Invalid Login Token"), http_status_code=417)
		return

	frappe.local.form_dict.sid = sid
	frappe.local.login_manager = LoginManager()

	redirect_post_login(desk_user = frappe.db.get_value("User", frappe.session.user, "user_type")=="System User")
