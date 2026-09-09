// Copyright (c) 2026, Harikrishnan T and contributors
// For license information, please see license.txt

// Client-side (browser) logic — gives instant feedback in the form.
// The Python side re-checks everything on save, so this is just for UX.

frappe.ui.form.on("Order", {
	validate(frm) {
		calculate_total(frm);
	},
});

frappe.ui.form.on("Order Item", {
	product(frm, cdt, cdn) {
		// When a product is picked, auto-fill its price.
		const row = locals[cdt][cdn];
		if (row.product) {
			frappe.db.get_value("Product", row.product, "price").then((r) => {
				if (r && r.message) {
					frappe.model.set_value(cdt, cdn, "price", r.message.price);
				}
			});
		}
	},
	quantity(frm, cdt, cdn) {
		calculate_row_amount(frm, cdt, cdn);
	},
	price(frm, cdt, cdn) {
		calculate_row_amount(frm, cdt, cdn);
	},
	items_remove(frm) {
		calculate_total(frm);
	},
});

function calculate_row_amount(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", (row.quantity || 0) * (row.price || 0));
	calculate_total(frm);
}

function calculate_total(frm) {
	let total = 0;
	(frm.doc.items || []).forEach((row) => {
		total += row.amount || 0;
	});
	frm.set_value("total_amount", total);
}
