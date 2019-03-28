
library(iL04)

span <- .1

#---------------------------------------------------------------

dif <- as.matrix(read.dif('../diff/diff.txt'))
geo <- as.matrix(read.dif('../map/map.geo'))[labels(dif)[[1]], labels(dif)[[1]]]

dif <- as.dist(dif)
geo <- as.dist(geo)

grp <- read.dif('grp2.dif')

m  <- loess(dif ~ geo, span=span)
mr <- loess(abs(residuals(m)) ~ geo, span=span)
for (i in unique(grp)) {
  g <- geo[grp == i]
  m1  <- loess(dif[grp == i] ~ g, span=span)
  mr1 <- loess(abs(residuals(m1)) ~ g, span=span)
  dif[grp == i] <- (dif[grp == i] - predict(m1, data.frame(g = g))) /
    predict(mr1, data.frame(g = g)) *
      predict(mr, data.frame(geo = g)) +
        predict(m, data.frame(geo = g))
}

write.dif(dif, 'newdiff2.txt')

#---------------------------------------------------------------

dif <- as.matrix(read.dif('../diff/diff.txt'))
geo <- as.matrix(read.dif('../map/map.geo'))[labels(dif)[[1]], labels(dif)[[1]]]

dif <- as.dist(dif)
geo <- as.dist(geo)

grp <- read.dif('grp3.dif')

m  <- loess(dif ~ geo, span=span)
mr <- loess(abs(residuals(m)) ~ geo, span=span)
for (i in unique(grp)) {
  g <- geo[grp == i]
  m1  <- loess(dif[grp == i] ~ g, span=span)
  mr1 <- loess(abs(residuals(m1)) ~ g, span=span)
  dif[grp == i] <- (dif[grp == i] - predict(m1, data.frame(g = g))) /
    predict(mr1, data.frame(g = g)) *
      predict(mr, data.frame(geo = g)) +
        predict(m, data.frame(geo = g))
}

write.dif(dif, 'newdiff3.txt')


