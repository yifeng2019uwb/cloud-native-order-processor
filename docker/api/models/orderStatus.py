class OrderStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    @classmethod
    def all_statuses(cls):
        return [
            cls.PENDING,
            cls.CONFIRMED,
            cls.PROCESSING,
            cls.PAID,
            cls.SHIPPED,
            cls.DELIVERED,
            cls.CANCELLED,
            cls.REFUNDED,
        ]

    @classmethod
    def active_statuses(cls):
        return [cls.PENDING, cls.CONFIRMED, cls.PROCESSING, cls.PAID, cls.SHIPPED]

    @classmethod
    def final_statuses(cls):
        return [cls.DELIVERED, cls.CANCELLED, cls.REFUNDED]
