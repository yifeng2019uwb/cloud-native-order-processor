class PaymentStatus:
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    
    @classmethod
    def all_statuses(cls):
        return [cls.PENDING, cls.PROCESSING, cls.COMPLETED, 
                cls.FAILED, cls.CANCELLED, cls.REFUNDED]