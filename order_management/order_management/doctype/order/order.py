# Copyright (c) 2026, Harikrishnan T and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Order(Document):
	def validate(self):
		"""Runs on the SERVER every time an Order is saved.
		Server-side logic is the source of truth — even if someone calls the API
		directly (bypassing the browser), these rules still apply.
		"""
		self.calculate_amounts()

	def calculate_amounts(self):
		# An order must have at least one item.
		if not self.items:
			frappe.throw(_("Please add at least one item to the order."))

		total = 0
		for item in self.items:
			# Quantity must be positive.
			if not item.quantity or item.quantity <= 0:
				frappe.throw(_("Quantity must be greater than 0 for product {0}.").format(item.product))

			# If no price was entered on the row, pull it from the Product.
			if not item.price:
				item.price = frappe.db.get_value("Product", item.product, "price") or 0

			# amount = quantity x price (per row)
			item.amount = item.quantity * item.price
			total += item.amount

		# order total = sum of all row amounts
		self.total_amount = total
