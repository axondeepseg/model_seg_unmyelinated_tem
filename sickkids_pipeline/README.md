# unmyelinated_axon_seg
Collaboration with data from Sick Kids (UoT)

## Training details
The model was trained on a 5-fold cross validation scheme with nnunetv2. The model checkpoint is available at https://github.com/axondeepseg/model_seg_unmyelinated_tem/releases/tag/v1.0.0 as a release asset.

## Filename correspondance
This table gives the correspondance between original filenames and the case identifier used by nnUNet. 
| Original filename | BIDS filename | Case identifier |
|:--|:--|:--|
|002|sub-mouse1_sample-data1_TEM|UMA_001|
|26|sub-mouse2_sample-data2_TEM|UMA_002|
|2079-OT-R-EM22-677-03_wl_8-bit|sub-mouse3_sample-data3_TEM|UMA_003|
|2080-CC-R-EM22-685-18_wl_8-bit|sub-mouse4_sample-data4_TEM|UMA_004|
|EM22-846-2055-AC-L_001|sub-mouse5_sample-data5_TEM|UMA_005|
|EM23-195_01.png|sub-mouse6_sample-data6_TEM|UMA_006|