# Copyright (c) 2026, Harikrishnan T and contributors
# For license information, please see license.txt
"""
Background jobs for the Order Management app.

A "background job" runs OUTSIDE the normal web request — either on a schedule
(via Frappe's scheduler) or pushed onto a queue (frappe.enqueue). This keeps
slow or periodic work off the user's screen.
"""

import frappe


def daily_order_summary():
	"""Runs automatically once a DAY (registered in hooks.py -> scheduler_events).
	Simulated task: logs how many orders sit in each status.
	"""
	counts = {}
	for row in frappe.get_all(
		"Order", fields=["status", "count(name) as c"], group_by="status"
	):
		counts[row.status] = row.c

	frappe.logger("order_management").info(f"Daily order summary: {counts}")
	return counts


@frappe.whitelist()
def run_summary_now():
	"""On-demand demo: pushes the summary onto the background queue immediately.
	Call it from the web (/api/method/order_management.tasks.run_summary_now) or:
	    bench --site oms.localhost execute order_management.tasks.run_summary_now
	"""
	frappe.enqueue("order_management.tasks.daily_order_summary", queue="short")
	return "Summary job queued (runs in the background)."
