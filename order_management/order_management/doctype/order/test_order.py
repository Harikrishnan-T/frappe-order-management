# Copyright (c) 2026, Harikrishnan T and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestOrder(FrappeTestCase):
	def setUp(self):
		# Dummy customer + product used by the tests below.
		if not frappe.db.exists("Customer", "Test Co"):
			frappe.get_doc({"doctype": "Customer", "customer_name": "Test Co"}).insert()
		if not frappe.db.exists("Product", "Test Widget"):
			frappe.get_doc(
				{
					"doctype": "Product",
					"product_name": "Test Widget",
					"sku": "TW-1",
					"price": 100,
					"stock_quantity": 50,
				}
			).insert()

	def test_order_total_is_calculated(self):
		order = frappe.get_doc(
			{
				"doctype": "Order",
				"customer": "Test Co",
				"items": [{"product": "Test Widget", "quantity": 3, "price": 100}],
			}
		).insert()
		self.assertEqual(order.items[0].amount, 300)  # 3 x 100
		self.assertEqual(order.total_amount, 300)

	def test_price_is_fetched_from_product(self):
		# No price on the row -> server should pull it from the Product (100).
		order = frappe.get_doc(
			{
				"doctype": "Order",
				"customer": "Test Co",
				"items": [{"product": "Test Widget", "quantity": 2}],
			}
		).insert()
		self.assertEqual(order.total_amount, 200)

	def test_zero_quantity_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Order",
					"customer": "Test Co",
					"items": [{"product": "Test Widget", "quantity": 0, "price": 100}],
				}
			).insert()

	def test_empty_order_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{"doctype": "Order", "customer": "Test Co", "items": []}
			).insert()
