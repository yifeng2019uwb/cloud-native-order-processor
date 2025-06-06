class PaymentMethod:
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"

    @classmethod
    def all_methods(cls):
        return [
            cls.CREDIT_CARD,
            cls.DEBIT_CARD,
            cls.PAYPAL,
            cls.STRIPE,
            cls.BANK_TRANSFER,
            cls.CASH_ON_DELIVERY,
        ]
