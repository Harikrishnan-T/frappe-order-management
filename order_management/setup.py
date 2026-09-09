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


# ---------------------------------------------------------------------------
# Phase 11 — Notification ("Order X has been shipped")
# ---------------------------------------------------------------------------
def create_notification():
	if frappe.db.exists("Notification", "Order Shipped"):
		return "notification exists"
	frappe.get_doc(
		{
			"doctype": "Notification",
			"name": "Order Shipped",
			"subject": "Order {{ doc.name }} has been shipped",
			"document_type": "Order",
			"channel": "System Notification",
			"event": "Value Change",
			"value_changed": "status",
			"condition": "doc.status == 'Shipped'",
			"message": "Order {{ doc.name }} for {{ doc.customer }} has been marked as Shipped.",
			"enabled": 1,
			"is_standard": 0,
			"recipients": [{"receiver_by_role": "Manager"}],
		}
	).insert(ignore_permissions=True)
	frappe.db.commit()
	return "notification created"


# ---------------------------------------------------------------------------
# Phase 12 — Report (Orders by Status)
# ---------------------------------------------------------------------------
def create_report():
	if frappe.db.exists("Report", "Orders by Status"):
		return "report exists"
	frappe.get_doc(
		{
			"doctype": "Report",
			"report_name": "Orders by Status",
			"ref_doctype": "Order",
			"report_type": "Query Report",
			"is_standard": "No",
			"query": (
				"SELECT status AS `Status:Data:150`, "
				"COUNT(name) AS `Total Orders:Int:130`, "
				"SUM(total_amount) AS `Order Value:Currency:160` "
				"FROM `tabOrder` GROUP BY status"
			),
			"roles": [{"role": "Manager"}, {"role": "Sales User"}],
		}
	).insert(ignore_permissions=True)
	frappe.db.commit()
	return "report created"


# ---------------------------------------------------------------------------
# Phase 13 — Dashboard (number cards)
# ---------------------------------------------------------------------------
def create_dashboard():
	def card(label, function, based_on=None, status=None):
		if frappe.db.exists("Number Card", label):
			return
		filters = [["Order", "status", "=", status, False]] if status else []
		doc = {
			"doctype": "Number Card",
			"name": label,
			"label": label,
			"type": "Document Type",
			"document_type": "Order",
			"function": function,
			"filters_json": frappe.as_json(filters),
			"is_standard": 0,
		}
		if based_on:
			doc["aggregate_function_based_on"] = based_on
		frappe.get_doc(doc).insert(ignore_permissions=True)

	card("Total Orders", "Count")
	card("Draft Orders", "Count", status="Draft")
	card("Processing Orders", "Count", status="Processing")
	card("Shipped Orders", "Count", status="Shipped")
	card("Completed Orders", "Count", status="Completed")
	card("Total Order Value", "Sum", based_on="total_amount")

	# A Dashboard needs at least one chart, so add a "by status" bar chart.
	if not frappe.db.exists("Dashboard Chart", "Orders by Status Chart"):
		frappe.get_doc(
			{
				"doctype": "Dashboard Chart",
				"chart_name": "Orders by Status Chart",
				"chart_type": "Group By",
				"document_type": "Order",
				"group_by_type": "Count",
				"group_by_based_on": "status",
				"type": "Bar",
				"filters_json": "[]",
				"is_standard": 0,
			}
		).insert(ignore_permissions=True)

	if not frappe.db.exists("Dashboard", "Order Management"):
		frappe.get_doc(
			{
				"doctype": "Dashboard",
				"dashboard_name": "Order Management",
				"is_standard": 0,
				"charts": [{"chart": "Orders by Status Chart", "width": "Full"}],
				"cards": [
					{"card": c}
					for c in [
						"Total Orders",
						"Draft Orders",
						"Processing Orders",
						"Shipped Orders",
						"Completed Orders",
						"Total Order Value",
					]
				],
			}
		).insert(ignore_permissions=True)
	frappe.db.commit()
	return "dashboard created"

