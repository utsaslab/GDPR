echo "Calculating price, please wait.."
pricingSource="https://cloud.google.com/translate/pricing"

fileSum=0
charSum=0

for filename in ./data/09-25-2019/*/*/*.txt; do
  charCount=($(wc -m < $filename))
  charSum=$(($charSum + $charCount))
  fileSum=$(($fileSum + 1))
done

echo "\b"
echo "Data summary:"
echo "\tTotal number of unique files:\t$fileSum"
echo "\tTotal number of characters:\t$charSum"

freeTierCharLimit=500000
contactTierCharLimit=1000000000 # a billion

if [ "$charSum" -ge "$contactTierCharLimit" ]; then
  echo "Too many characters to translate. (Exceeding a billion character limit - $charSum).\bPlease contact Google developer team for resolution: $pricingSource"
else
  charPerMillion=$(python3 -c "from math import ceil; print(ceil($charSum/1000000.0))")

  echo "\b"
  echo "Estimated pricing:"
  echo "\tFeature detection (API v2, v3):\t\$$((20 * $charPerMillion))"
  echo "\tText translation (API v2):\t\$$((20 * $charPerMillion))"
  echo "\tText translation (PBMT general models) (API v3):\t\$$((20 * $charPerMillion))"

  if [ "$charSum" -le "$freeTierCharLimit" ]; then
    echo "\tText translation (NMT general models) (API v3):\tFree"
  else
    echo "\tText translation (NMT general models) (API v3):\t\$$((20 * $charPerMillion))"
  fi

  if [ "$charSum" -le "$freeTierCharLimit" ]; then
    echo "\tText translation (AutoML models) (API v3):\tFree"
  else
    echo "\tText translation (AutoML models) (API v3):\t\$$((80 * $charPerMillion))"
  fi
  echo "\b\b"
  echo "\tPricing equation: Price per million * Number of million chars"
  echo "\tSource: $pricingSource"
fi
