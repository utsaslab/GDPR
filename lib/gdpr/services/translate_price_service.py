from enum import Enum

# Source: https://cloud.google.com/translate/pricing
class GoogleTranslateModelPrice(Enum):
    PBMT=20.0
    NMT=20.0
    AutoML=80.0

class GoogleTranslatePriceService():
    def price_for_text(self, text, model=GoogleTranslateModelPrice.PBMT):
        if len(text) == 0:
            return 0.0
        return model.value * (len(text) / 10.0**6)
