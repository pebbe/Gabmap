
library(iL04)

# from "alpha {psychometric}"
# Arguments
#   x   Data.frame or matrix object with rows corresponding individuals and columns to items
cronalphaold <- function(x) 
{
    x <- na.exclude(as.matrix(x))
    Sx <- sum(var(x))
    SumSxi <- sum(apply(x, 2, var))
    k <- ncol(x)
    alpha <- k/(k - 1) * (1 - SumSxi/Sx)
    return(alpha)
}


# dit houdt beter rekening met ontbrekende waardes
cronalpha <- function(x)
{
  m <- ncol(x)
  n <- nrow(x)

  # bereken variances
  varSum <- 0
  varN <- 0
  for (w1 in 1:m) {

    varSum <- varSum + var(x[, w1], use='complete.obs')
    varN <- varN + 1

  }
  if (varN < 1) {
    return(NA)
  }
  varAv <- varSum / varN

  # bereken covariances
  covSum <- 0
  covN <- 0
  for (w1 in 2:m) {
    for (w2 in 1:(w1 - 1)) {

      covSum <- covSum + cov(x[, w1], x[, w2], use='pairwise.complete.obs')
      covN <- covN + 1

    }
  }
  if (covN < 1) {
    return(NA)
  }
  covAv <- covSum / covN
  
  caValue <- m * covAv / (varAv + (m - 1) * covAv)

  return(caValue)
}


con <- file('../data/Method', open='rt')
m <- readLines(con, n=1)
close(con)

if (m == 'numnorm') {
  normalise <- TRUE
} else {
  normalise <- FALSE
}

con = file("../data/table.txt", open="rt", encoding="iso-8859-1")
a <- read.table(con, allowEscapes=TRUE, check.names=FALSE)
close(con)

width <- max(6, min(16, 1 + .2 * length(a[1,])))

postscript(file='../data/boxplot%02d.eps', width=width, height=8, onefile=FALSE, horizontal=FALSE, paper='special')
par(mar=c(20, 3, 1, 1) + 0.1)
boxplot(a, pars=list(boxwex=0.8, staplewex=0.5, outwex=0.5, las=3))

if (normalise) {
  for (i in 1:length(a[1,])) {
    m <- mean(a[, i], na.rm=TRUE)
    s <- sd(a[, i], na.rm=TRUE)
    if (! is.na(s) & s > 0) {
      a[, i] <- (a[, i] - m) / s
    } else {
      if (! is.na(m)) {
         a[, i] <- a[, i] - m
      }
    }
  }
  boxplot(a, pars=list(boxwex=0.8, staplewex=0.5, outwex=0.5, las=3))
}

dev.off()

aa <- apply(a, 2, dist)

options(digits=4)
ca <- format(try(cronalpha(aa)))
cat(ca, '\n', sep='', file='ca.txt')

d <- length(a[,1])
m <- matrix(0, nrow=d, ncol=d)
m[col(m) < row(m)] <- apply(aa, 1, mean, na.rm=TRUE)
m <- as.dist(m)
attr(m, "Labels") <- row.names(a)
write.dif(m, 'diff.txt')
