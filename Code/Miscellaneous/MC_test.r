library(exact2x2)
library(effsize)
library(xtable)


res=list(Dataset=c(),McNemar.p=c(),McNemar.OR=c())
d<-"/Users/antonio/icse2022-variable-renaming/Results/Statistical-Analysis/MC_Test/Developers/final.csv"
t<-read.csv(d)

m=mcnemar.exact(t$IS_PERFECT_T5,t$IS_C_MATCH_NGRAM)
res$Dataset=c(res$Dataset,as.character(d))
res$McNemar.p=c(res$McNemar.p, m$p.value)
res$McNemar.OR=c(res$McNemar.OR,m$estimate)

m=mcnemar.exact(t$IS_PERFECT_T5,t$IS_P_MATCH_NGRAM)
res$Dataset=c(res$Dataset,as.character(d))
res$McNemar.p=c(res$McNemar.p, m$p.value)
res$McNemar.OR=c(res$McNemar.OR,m$estimate)

m=mcnemar.exact(t$IS_PERFECT_T5,t$IS_C_MATCH_CUGLM)
res$Dataset=c(res$Dataset,as.character(d))
res$McNemar.p=c(res$McNemar.p, m$p.value)
res$McNemar.OR=c(res$McNemar.OR,m$estimate)

m=mcnemar.exact(t$IS_PERFECT_T5,t$IS_P_MATCH_CUGLM)
res$Dataset=c(res$Dataset,as.character(d))
res$McNemar.p=c(res$McNemar.p, m$p.value)
res$McNemar.OR=c(res$McNemar.OR,m$estimate)


res=data.frame(res)
#p-value adjustment
res$McNemar.p=p.adjust(res$McNemar.p,method="holm")
print(res)



# print(xtable(res),include.rownames=FALSE)
