
library(iL04)

#---------------------------------------------------------------

dif <- as.matrix(read.dif('../diff/diff.txt'))
geo <- as.matrix(read.dif('../map/map.geo'))[labels(dif)[[1]], labels(dif)[[1]]]

dif <- as.dist(dif)
geo <- as.dist(geo)

grp <- read.dif('grp2.dif')


step <- 20
n <- as.integer(max(geo) / step)
if (n * step < max(geo)) n <- n + 1

y.m <- 1:n
y.sd <- 1:n
y.n <- 1:n
x <- 1:n * step - step * .5
for (i in 1:n) {
  p <- geo >= (i - 1) * step & geo <= i * step
  y.n[i] <- length(geo[p])
  if (y.n[i] > 1) {
    x[i] <- mean(geo[p])
    y.m[i]  <- mean(dif[p])
    y.sd[i] <- sd(dif[p])
  }
}
u <- y.n > 1
x <- x[u]
ALLmean <- lm(y.m[u]  ~ x + I(x^2) + I(x^3) + I(x^4))
ALLsd   <- lm(y.sd[u] ~ x + I(x^2) + I(x^3) + I(x^4))

for (idx in unique(grp)) {

  g <- geo[grp == idx]
  d <- dif[grp == idx]

  y.m <- 1:n
  y.sd <- 1:n
  y.n <- 1:n
  x <- 1:n * step - step * .5
  for (i in 1:n) {
    p <- g >= (i - 1) * step & g <= i * step
    y.n[i] <- length(g[p])
    if (y.n[i] > 1) {
      x[i] <- mean(g[p])
      y.m[i]  <- mean(d[p])
      y.sd[i] <- sd(d[p])
    }
  }
  u <- y.n > 1
  x <- x[u]
  SUBmean <- lm(y.m[u]  ~ x + I(x^2) + I(x^3) + I(x^4))
  SUBsd   <- lm(y.sd[u] ~ x + I(x^2) + I(x^3) + I(x^4))

  SUB.norm <- (d - predict(SUBmean, data.frame(x=g))) /
    predict(SUBsd, data.frame(x=g)) *
      predict(ALLsd, data.frame(x=g)) +
        predict(ALLmean, data.frame(x=g))

  dif[grp == idx] <- SUB.norm

}

write.dif(dif, 'newdiff22.txt')

#---------------------------------------------------------------
