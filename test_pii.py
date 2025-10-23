from app.utils.pii_utils import mask_pii

result = mask_pii("Call me at 090-123-4567 or email john@example.com")
print(result)
