# Order Management System (Frappe)

A small **Order Management System** built from scratch on the **Frappe Framework** —
created purely as a **hands-on learning project** to understand how Frappe works in
practice (DocTypes, workflows, permissions, APIs, background jobs, reports and more).

> ⚠️ Learning project only — no real customers, payments, or courier integrations.
> All data is dummy.

---

## Why this project

To learn the Frappe Framework by *building* something rather than just reading docs.
Each feature was added one phase at a time, so the git history reads like a tutorial.

## Tech stack

- **Frappe Framework v15** (the app framework — **not** ERPNext)
- **Python** (server-side logic)
- **JavaScript** (client-side form logic)
- **MariaDB** (database)
- **Redis** (cache + background job queue)

## Frappe concepts demonstrated

| Concept | Where |
|---|---|
| **DocTypes** (data models) | Customer, Product, Order, Order Item, Shipment |
| **Fields & field types** | Data, Currency, Int, Date, Select, Link |
| **Link fields** | Order → Customer, Order Item → Product, Shipment → Order |
| **Child Tables** | Order Item (line items inside an Order) |
| **Controllers (Python)** | `order.py` — validation + total calculation |
| **Client Scripts (JS)** | `order.js` — live price fetch + totals |
| **Naming** | Orders auto-named `ORD-#####`, customers by name |
| **Workflow** | Draft → Confirmed → Processing → Shipped → Completed |
| **Roles & Permissions** | Sales User, Warehouse User, Manager |
| **REST API** | auto `/api/resource/Order` + custom `api.py` methods |
| **Background Jobs** | `tasks.py` daily order summary |
| **Notifications** | "Order X has been shipped" |
| **Reports** | Orders by Status (query report) |
| **Dashboard** | number cards (counts + total value) + bar chart |
| **Hooks** | `hooks.py` — scheduler events |
| **Testing** | `test_order.py` — unit tests for the calculations |

## Application flow

```
Customer  ─┐
Product   ─┤→  Order (with Order Items)  →  Workflow  →  Shipment
           │        └ auto-calculates total    (Draft → … → Completed)
```

1. Create **Customers** and **Products**
2. Create an **Order**, add multiple products (Order Items) — item amount & order total
   calculate automatically
3. Move the order through its **Workflow** (Confirm → Process → Ship → Complete)
4. Create a **Shipment** for the order (dummy tracking number)
5. View **Reports** and the **Dashboard**

## Data model

- **Customer** — `customer_name`, `email`, `phone`
- **Product** — `product_name`, `sku` (unique), `price`, `stock_quantity`
- **Order** — `customer` (Link), `order_date`, `status`, `items` (Child Table), `total_amount`
- **Order Item** (child) — `product` (Link), `quantity`, `price`, `amount`
- **Shipment** — `order` (Link), `customer`, `shipment_date`, `tracking_number`, `shipment_status`

## Setup / installation

Assumes a working [Frappe bench](https://frappeframework.com/docs) with MariaDB + Redis.

```bash
# 1. Get the app into your bench
cd frappe-bench
bench get-app https://github.com/Harikrishnan-T/frappe-order-management.git order_management

# 2. Install it on a site
bench --site your-site install-app order_management

# 3. Create the roles, workflow, notification, report and dashboard
bench --site your-site execute order_management.setup.create_roles
bench --site your-site execute order_management.setup.setup_permissions
bench --site your-site execute order_management.setup.create_workflow
bench --site your-site execute order_management.setup.create_notification
bench --site your-site execute order_management.setup.create_report
bench --site your-site execute order_management.setup.create_dashboard

# 4. Start
bench start
```

### Run the tests
```bash
bench --site your-site set-config allow_tests true
bench --site your-site run-tests --module order_management.order_management.doctype.order.test_order
```

## Screenshots

_(Add screenshots here: Order form, Workflow buttons, Dashboard, Report.)_

## Future improvements

- Auto-create a Shipment when an Order is marked Shipped
- Reduce product stock when an order is confirmed
- Customer-facing order portal page
- More reports (sales over time, top products)
- Export as Frappe fixtures so setup installs automatically

## License

MIT
