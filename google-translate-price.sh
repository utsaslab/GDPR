pricingSource="https://cloud.google.com/translate/pricing"

fileSum=0
charSum=0
freeTierCharLimit=500000
contactTierCharLimit=1000000000 # a billion

for filename in ./data/09-25-2019/*/*/*.txt; do
  charCount=($(wc -m < $filename))
  charSum=$(($charSum + $charCount))
  fileSum=$(($fileSum + 1))
done

echo "Data summary:"
echo "\tTotal number of unique files:\t$fileSum"
echo "\tTotal number of characters:\t$charSum"

if [ "$charSum" -ge "$contactTierCharLimit" ]; then
  echo "Too many characters to translate. (Exceeding a billion character limit - $charSum).\bPlease contact Google developer team for resolution: $pricingSource"
else
  charPerMillion=`scale=2; echo $charSum/1000000|bc -l`

  price=`scale=2; echo 20*$charPerMillion|bc -l`
  pbmtPrice=`scale=2; echo 20*$charPerMillion|bc -l`
  nmtPrice=`scale=2; echo 20*$charPerMillion|bc -l`
  autoMLPrice=`scale=2; echo 80*$charPerMillion|bc -l`

  if [ "$charSum" -le "$freeTierCharLimit" ]; then
    nmtPrice=0.0
    autoMLPrice=0.0
  fi

  echo "\b"
  echo "Price of feature (Text Translation):"

  printf "\t(API v2):\t\t\t\$%.2f\n" $price
  printf "\t(PBMT general models) (API v3):\t\$%.2f\n" $pbmtPrice
  printf "\t(NMT general models) (API v3):\t\$%.2f\n" $nmtPrice
  printf "\t(AutoML models) (API v3):\t\$%.2f\n" $autoMLPrice

  echo "\b\b"
  echo "\tPricing equation: Price per million * Number of chars (per million)"
  echo "\tPricing example: \$20 * (75.000 chars/10^6 chars)) = \$20*0.075 = \$1.5"
  echo "\tSource: $pricingSource"
fi
