from enum import Enum

class Category(str, Enum):
    billing = "billing"
    technical = "technical"
    account = "account"
    feature_request = "feature_request"
    other = "other"

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"