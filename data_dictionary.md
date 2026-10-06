# E-Commerce Orders — Data Dictionary

| Column | Meaning | Quality Rule |
|---|---|---|
| order_id | Unique order identifier | Required + unique |
| customer_id | Customer identifier | Required |
| product | Purchased product | Required |
| category | Product category | Informational |
| unit_price | Price per unit | >= 0.01 |
| quantity | Number of units | >= 1 |
| order_date | Order date | Required |
| city | Delivery/customer city | Informational |
| status | Order lifecycle status | Pending/Shipped/Delivered/Cancelled |
