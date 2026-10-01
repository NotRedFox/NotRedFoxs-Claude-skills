# tinyinvoice

Small invoice helper for a freelance business.

## Usage

```python
from invoice import Invoice
inv = Invoice("Acme")
inv.add("Logo design", 450.00)
print(inv.summary())
```
