# E-Commerce Orders — Data Dictionary

## `orders` table

| Column | Type | Description | Quality Rule |
|---|---|---|---|
| order_id | VARCHAR | Unique order identifier (O0001–O9999) | Required · Unique |
| customer_id | VARCHAR | FK → customers.customer_id | Required |
| product | VARCHAR | Name of the purchased product | Required |
| category | VARCHAR | Product category (Electronics, Accessories, Audio, Wearables, Storage) | Informational |
| unit_price | INTEGER | Price per unit (₹) | ≥ 0.01 and ≤ 5,00,000 |
| quantity | INTEGER | Number of units ordered | ≥ 1 |
| order_date | DATE | Date the order was placed | Required |
| city | VARCHAR | City of delivery | Informational |
| payment_mode | VARCHAR | Payment method used | UPI / Credit Card / Debit Card / COD / Net Banking |
| status | VARCHAR | Current order status | Pending / Shipped / Delivered / Cancelled / Returned |

## `customers` table

| Column | Type | Description | Quality Rule |
|---|---|---|---|
| customer_id | VARCHAR | Unique customer identifier (C001–C999) | Required · Unique |
| name | VARCHAR | Customer's full name | Required |
| email | VARCHAR | Contact email address | Required |
| city | VARCHAR | City of residence | Informational |
| signup_date | DATE | Account creation date | Informational |

## `order_details` view (derived)

A LEFT JOIN of `orders` and `customers` on `customer_id`, with a computed `total_amount = unit_price × quantity`.
