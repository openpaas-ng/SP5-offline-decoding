#!/bin/bash

#Need lattice-to-nbest file in param
dataFile=$1

#Init value
declare -a utteranceValue
declare -a acousticScore
declare -a languageScore

countUtterance=1
previousId=1
acousticScore[previousId]=0
languageScore[previousId]=0


#Position of important colonne 
posName=0
posAcoustic=2
posLanguage=3
posUtterance=4



while read -r line
do
	name="$line"
	arrLine=($line)
	currentId="${arrLine[$posName]##*-}"
	if [ "$currentId" -eq "$previousId" ]; then
		#Manage all data value before storage
		countUtterance=$((countUtterance + 1))
		utteranceValue[$currentId]="${utteranceValue[currentId]} ${arrLine[$posUtterance]}"
		acousticScore[$currentId]=`echo ${acousticScore[currentId]} + ${arrLine[$posAcoustic]} | bc`
		languageScore[$currentId]=`echo ${languageScore[currentId]} + ${arrLine[$posLanguage]} | bc`	
	else
		#Do stuff on the previous segment before swap
		acousticScore[$previousId]=$(echo "scale=2; ${acousticScore[$previousId]}/$countUtterance" | bc)
		languageScore[$previousId]=$(echo "scale=2; ${languageScore[$previousId]}/$countUtterance" | bc)
		
		#Init for the next seglment
		previousId=$currentId
		countUtterance=0
		concatUterance=""
		acousticScore[previousId]=0
		languageScore[previousId]=0

		#Init data for the uterance
		countUtterance=$((countUtterance + 1))
		utteranceValue[$currentId]="${utteranceValue[currentId]} ${arrLine[$posUtterance]}"
		acousticScore[$currentId]=`echo ${acousticScore[currentId]} + ${arrLine[$posAcoustic]} | bc`
		languageScore[$currentId]=`echo ${languageScore[currentId]} + ${arrLine[$posLanguage]} | bc`	

	fi
done < "$dataFile"

#Need to manage the last data
acousticScore[$previousId]=$(echo "scale=2; ${acousticScore[$previousId]}/$countUtterance" | bc)
languageScore[$previousId]=$(echo "scale=2; ${languageScore[$previousId]}/$countUtterance" | bc)

#start to 1, no id 0 stored
echo "["
for i in `seq 1 $previousId`; do
		acousticScore[$i]=$(echo "scale=2; 1-${acousticScore[$i]}" | bc)
		languageScore[$i]=$(echo "scale=2; 1-${languageScore[$i]}" | bc)

		echo "{"
		echo "\"utterance\":\"${utteranceValue[$i]}\","
		echo "\"acousticScore\":0${acousticScore[$i]},"
		echo "\"languageScore\":0${languageScore[$i]}"
		if [ "$i" -eq "$previousId" ]; then
			echo "}"
		else
			echo "},"
		fi
done
echo "]"