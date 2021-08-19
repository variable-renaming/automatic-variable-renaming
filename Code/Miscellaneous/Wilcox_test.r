library(effsize)


setwd(paste("statistical-Analysis/Box_Plot/NGRAM/","Large-Scale",sep=""))

data<-read.csv("data_reduced.csv",header=TRUE)
perfect <- data[which(data["IS_PERFECT"] == TRUE),]
wrong <- data[which(data["IS_PERFECT"] == FALSE),]


#p-value < 0.05 to be significant

#Tokens
wilcox.test(perfect$Tokens,wrong$Tokens,alternative="two.side",paired=FALSE)$p.value
cliff.delta(perfect$Tokens,wrong$Tokens)$magnitude


#CharPerVar
wilcox.test(perfect$CharPerVar,wrong$CharPerVar,alternative="two.side",paired=FALSE)$p.value
cliff.delta(perfect$CharPerVar,wrong$CharPerVar)$magnitude

#TokenPerVar
wilcox.test(perfect$TokenPerVar,wrong$TokenPerVar,alternative="two.side",paired=FALSE)$p.value
cliff.delta(perfect$TokenPerVar,wrong$TokenPerVar)$magnitude


#Occurences_Within_Training
wilcox.test(perfect$Occurences_Within_Training,wrong$Occurences_Within_Training,alternative="two.side",paired=FALSE)$p.value
cliff.delta(perfect$Occurences_Within_Training,wrong$Occurences_Within_Training)$magnitude

#OccurencesVarPerMethod
wilcox.test(perfect$OccurencesVarPerMethod,wrong$OccurencesVarPerMethod,alternative="two.side",paired=FALSE)$p.value
cliff.delta(perfect$OccurencesVarPerMethod,wrong$OccurencesVarPerMethod)$magnitude

