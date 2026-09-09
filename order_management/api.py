# Copyright (c) 2026, Harikrishnan T and contributors
# For license information, please see license.txt
"""
Custom REST API endpoints for the Order Management app.

Any function decorated with @frappe.whitelist() is callable over HTTP at:
    /api/method/order_management.api.<function_name>

(Frappe ALSO auto-exposes generic endpoints for every DocType at
 /api/resource/Order — list, GET /api/resource/Order/<name>, POST to create.)
"""

import json

import frappe


@frappe.whitelist()
def get_orders():
	"""GET /api/method/order_management.api.get_orders
	Returns a simple list of all orders.
	"""
	return frappe.get_all(
		"Order",
		fields=["name", "customer", "order_date", "status", "total_amount"],
		order_by="creation desc",
	)


@frappe.whitelist()
def get_order(name):
	"""GET /api/method/order_management.api.get_order?name=ORD-00001
	Returns one order with its line items.
	"""
	doc = frappe.get_doc("Order", name)
	return {
		"name": doc.name,
		"customer": doc.customer,
		"order_date": str(doc.order_date),
		"status": doc.status,
		"total_amount": doc.total_amount,
		"items": [
			{
				"product": i.product,
				"quantity": i.quantity,
				"price": i.price,
				"amount": i.amount,
			}
			for i in doc.items
		],
	}


@frappe.whitelist()
def create_order(customer, items):
	"""POST /api/method/order_management.api.create_order
	Body: customer=<name>, items=[{"product": "...", "quantity": 2}, ...]
	Prices/amounts/total are filled by the Order's own server-side logic.
	"""
	if isinstance(items, str):
		items = json.loads(items)

	doc = frappe.get_doc({"doctype": "Order", "customer": customer, "items": items})
	doc.insert()
	frappe.db.commit()
	return {"name": doc.name, "total_amount": doc.total_amount}
