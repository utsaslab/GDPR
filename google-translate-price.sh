pricingSource="https://cloud.google.com/translate/pricing"

uniqueFileSum=0
translatedFileSum=0
charSum=0
freeTierCharLimit=500000
contactTierCharLimit=1000000000 # a billion

for filename in ./data/09-25-2019/*/*/*.txt; do
  if [[ $filename != */en.txt ]]; then
    charCount=($(wc -m < $filename))
    charSum=$(($charSum + $charCount))
    translatedFileSum=$(($translatedFileSum + 1))
  fi
  uniqueFileSum=$(($uniqueFileSum + 1))
done

translatedFilesPct=`echo $translatedFileSum/$uniqueFileSum|bc -l`
translatedFilesPct=`echo 1.0-$translatedFilesPct|bc -l`
translatedFilesPct=`echo $translatedFilesPct*100.0|bc -l`

echo "Data summary:"
echo "\tTotal number of characters:\t$charSum"
echo "\tTotal number of files:\t\t$translatedFileSum"
printf "\tFiles translated:\t\t%.2f%%" $translatedFilesPct

if [ "$charSum" -ge "$contactTierCharLimit" ]; then
  echo "Too many characters to translate. (Exceeding a billion character limit - $charSum).\bPlease contact Google developer team for resolution: $pricingSource"
else
  charPerMillion=`echo $charSum/1000000|bc -l`

  price=`echo 20*$charPerMillion|bc -l`
  pbmtPrice=`echo 20*$charPerMillion|bc -l`
  nmtPrice=`echo 20*$charPerMillion|bc -l`
  autoMLPrice=`echo 80*$charPerMillion|bc -l`

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
