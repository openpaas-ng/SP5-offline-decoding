#!/bin/bash

. cmd.sh
. path.sh

# call sh ./decoding.sh ../systems/sys1

wavdir=$lvcsrRootDir/wavs
nj=1
decode_nj=1
num_threads=1
sysdir=$(readlink -f $1)
echo $sysdir
doScoring=0
stage=1

sysRootName=$(echo $(basename $sysdir)|cut -f1 -d"=")
echo $sysRootName

for file in $(find $wavdir -name "*.wav");do
    echo $file
    fileRootName=$(basename $file .wav)
    echo $fileRootName
    datadir=$sysdir/kaldi_input_data/$fileRootName
    [ -d $datadir ] || mkdir -p $datadir
    if [ $stage -le 0 ]; then
        if [ -e $wavdir/$fileRootName.stm ]; then
            cp $wavdir/$dileRootName.stm $datadir/stm
            doScoring=1
        fi
    fi
    if [ $stage -le 1 ]; then
        echo "doing Speaker diaritization : segment extraction"
        java -Xmx2024m -jar $lvcsrRootDir/tools/lium_spkdiarization-8.4.1.jar  \
            --fInputMask=$file --sOutputMask=$datadir/$fileRootName.seg --doCEClustering $fileRootName
    fi
    if [ $stage -le 2 ]; then
        # Generate kaldi input for offline decoding
        # file gen: segments, utt2spk, spk2utt, wav.scp
        # Gen segments file
        awk '$1 !~ /^;;/ {print $1"-"$8"-"$3/100.0"-"($3+$4)/100.0" "$1" "$3/100.0" "($3+$4)/100.0}' \
		   	$datadir/$fileRootName.seg | sort -nk3 > $datadir/segments
        # Gen utt2spk file
        awk '{split($1,a,"-"); print $1" "a[2]  }'  $datadir/segments > $datadir/utt2spk
		echo here before utt2spk_to_spk2utt.pl
		# Gen spk2utt file
		cat $datadir/utt2spk | $lvcsrRootDir/scripts/utils/utt2spk_to_spk2utt.pl > $datadir/spk2utt
		# Gen wav.scp
		(for tag in $(cut -f1 -d"-" $datadir/spk2utt | cut -f2 -d" "); do
		    echo "$tag sox $file -t wav -r 16000 -c 1 - |"
		done) > $datadir/wav.scp
		cat $datadir/wav.scp | awk '{ print $1, $1, "A"; }' > $datadir/reco2file_and_channel
		echo validate_data_dir.sh
		$lvcsrRootDir/scripts/utils/validate_data_dir.sh --no-text --no-feats $datadir
		$lvcsrRootDir/scripts/utils/fix_data_dir.sh $datadir
	fi
	if [ $stage -le 3 ]; then
	    # Generate Feature for each segments
	    mfccdir=$datadir/mfcc
	    mkdir -p $mfccdir
	    $lvcsrRootDir/scripts/steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" $datadir $datadir/log $mfccdir || exit 1
	    $lvcsrRootDir/scripts/steps/compute_cmvn_stats.sh $datadir $datadir/log $mfccdir || exit 1
	fi
	# Link tri3 model
	gmmdir=$1
	transdir=$gmmdir/decode_$fileRootName

	if [ $stage -le 4 ]; then
        if [ ! -f $transdir/trans.1 ]; then
            echo "run fmllr decoding"
            $lvcsrRootDir/scripts/steps/decode_fmllr.sh --nj $decode_nj --cmd "$decode_cmd" --num-threads $num_threads --skip-scoring "true" \
            $gmmdir/Graph $datadir $transdir || exit 1
        fi
	fi
	### for next sprint add
	### fmllr Feature Extraction ####
	### DNN Acoustic Models applied on top of the fmllr features ###
	### Rescoring with LM
	### Get CTM and STM files
done

echo "End...."

