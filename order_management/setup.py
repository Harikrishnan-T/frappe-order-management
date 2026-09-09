# Copyright (c) 2026, Harikrishnan T and contributors
# For license information, please see license.txt
"""
One-time setup helpers for the Order Management learning app.

Run a function with:
    bench --site oms.localhost execute order_management.setup.<function_name>

These create records (Roles, Workflow, Notification, Report, Dashboard cards)
that live in the database. Keeping them here means the setup is reproducible and
version-controlled.
"""

import frappe

ROLES = ["Sales User", "Warehouse User", "Manager"]


# ---------------------------------------------------------------------------
# Phase 7 — Roles & Permissions
# ---------------------------------------------------------------------------
def create_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(
				ignore_permissions=True
			)
	frappe.db.commit()
	return "roles created: " + ", ".join(ROLES)


def setup_permissions():
	from frappe.permissions import add_permission, update_permission_property

	# which roles can access which doctype
	access = {
		"Customer": ["Sales User", "Manager"],
		"Product": ["Sales User", "Warehouse User", "Manager"],
		"Order": ["Sales User", "Warehouse User", "Manager"],
		"Shipment": ["Warehouse User", "Manager"],
	}
	for doctype, roles in access.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		for role in roles:
			add_permission(doctype, role, 0)
			for perm in ("read", "write", "create"):
				update_permission_property(doctype, role, 0, perm, 1)
			if role == "Manager":  # managers can also delete
				update_permission_property(doctype, role, 0, "delete", 1)
	frappe.db.commit()
	return "permissions set"


# ---------------------------------------------------------------------------
# Phase 6 — Workflow (Draft -> Confirmed -> Processing -> Shipped -> Completed)
# ---------------------------------------------------------------------------
def create_workflow():
	states = [
		("Draft", "Sales User"),
		("Confirmed", "Sales User"),
		("Processing", "Warehouse User"),
		("Shipped", "Warehouse User"),
		("Completed", "Manager"),
	]
	transitions = [
		("Draft", "Confirm", "Confirmed", "Sales User"),
		("Confirmed", "Start Processing", "Processing", "Warehouse User"),
		("Processing", "Ship", "Shipped", "Warehouse User"),
		("Shipped", "Complete", "Completed", "Manager"),
	]

	# Frappe needs a Workflow State + Workflow Action Master record for each name.
	for state, _role in states:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": state}).insert(
				ignore_permissions=True
			)
	for _from, action, _to, _role in transitions:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc(
				{"doctype": "Workflow Action Master", "workflow_action_name": action}
			).insert(ignore_permissions=True)

	if not frappe.db.exists("Workflow", "Order Workflow"):
		frappe.get_doc(
			{
				"doctype": "Workflow",
				"workflow_name": "Order Workflow",
				"document_type": "Order",
				"workflow_state_field": "status",
				"is_active": 1,
				"states": [
					{"state": s, "doc_status": "0", "allow_edit": r} for s, r in states
				],
				"transitions": [
					{"state": f, "action": a, "next_state": n, "allowed": r}
					for f, a, n, r in transitions
				],
			}
		).insert(ignore_permissions=True)
	frappe.db.commit()
	return "workflow created"
