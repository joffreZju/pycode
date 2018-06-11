#!/bin/bash

sed -i 's/$/,/' "$*"
sed -i '$s/,$//' "$*"
sed -i '1i[' "$*"
sed -i '$a]' "$*"
