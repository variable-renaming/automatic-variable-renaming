#REF: https://github.com/SLP-team/SLP-Core

#For training the model, please use the following: https://github.com/SLP-team/SLP-Core/releases/tag/v0.3

jdk-9.0.4/bin/java -jar slp-core.jar vocabulary training-file-methods train.vocab --unk-cutoff 0 -l java 

jdk-9.0.4/bin/java -jar slp-core.jar train --train training-file-methods --counter train.counts --vocabulary train.vocab --order 3 -l java



