
library(iL04)

dif <- as.vector(read.dif('../diff/diff.txt'))
geo <- as.vector(read.dif('tmp.dst'))

o <- order(geo)
dif <- dif[o]
geo <- geo[o]

xrange <- range(geo)

x <- seq(xrange[1], xrange[2], length.out = 200)

step <- max(geo) / 50.0
g1 <- rep(NA, 50)
d1 <- rep(NA, 50)
n <- 0
for (i in 1:50) {
  idx = geo > step * (i - 1) & geo <= step * i
  if (length(idx[idx]) > 0) {
    n <- n + 1
    g1[n] <- mean(geo[idx])
    d1[n] <- mean(dif[idx])
  }
}


con <- file('../description', open='rt', encoding='UTF-8')
desc <- readLines(con, n=1)
close(con)

desc <- gsub('&lt;', '<', desc, fixed=TRUE)
desc <- gsub('&gt;', '>', desc, fixed=TRUE)
desc <- gsub('&quot;', '"', desc, fixed=TRUE)
desc <- gsub('&amp;', '&', desc, fixed=TRUE)

postscript(file='plot%02d.eps', width=6, height=5, onefile=FALSE, horizontal=FALSE, paper='a4')
par(mar=c(5, 4, 1, 2) + 0.1)

assign("needplot", TRUE, envir=.GlobalEnv)

plot01 <- function() {

  a <- min(dif)
  b <- max(dif) - a
  c <- geo[length(dif[dif < mean(dif)])]

  m <- nls(dif ~ a + b * geo / (c + geo), start=list(a=a, b=b, c=c), trace=TRUE)

  a <- as.numeric(m$m$getPars()[1])
  b <- as.numeric(m$m$getPars()[2])
  c <- as.numeric(m$m$getPars()[3])

  abc <- sprintf('a = %.3g   b = %.3g   c = %g km', a, b, round(c))


  yrange <- c(a - b, max(max(dif), a + b))
  plot(xrange, yrange, xlab='Geograpic distance (km)', ylab='Linguistic difference', type='n', sub=abc)
  assign("needplot", FALSE, envir=.GlobalEnv)
  points(geo, dif, col='#A0A0A0', pch='.')

  lines(g1, d1, col='red', lwd=2)

  lines(x, a + b * x / (c + x),  col='blue',  lwd=2)

  lines(xrange, c(a, a), col='blue', lwd=.5)
  lines(xrange, c(a + b, a + b), col='blue', lwd=.5)
  lines(xrange, c(a + b/2, a + b/2), col='blue', lwd=.5)
  lines(c(c, c), c(0, a + b/2), col='blue', lwd=.5)

  legend(xrange[2], yrange[1],
         c(expression(a + b ~~ frac(x, c + x)), 'local'),
         xjust=1, yjust=0,
         col=c('blue', 'red'), lwd=2, bty="n")

  text(xrange[2], a, expression(a), adj=c(1,1.5), col='blue')
  text(xrange[2], a + b/2, expression(a + b / 2), adj=c(1,1.5), col='blue')
  text(0, a + b, expression(a + b), adj=c(0,1.5), col='blue')
  text(c, 0, expression(c),adj=c(-.5,0), col='blue')

  sink('plot01.log')
  print(summary(m))
  cat('Asymptotic/Actual  R-squared:', cor(dif, predict(m, data.frame(geo = geo)))^2, '\n')
  cat('Asymptotic/Local   R-squared:', cor(d1[1:n], predict(m, data.frame(geo = g1[1:n])))^2, '\n')
  sink()

  return(yrange)
 
}

result <- try(plot01())

if (class(result) == "try-error") {
  cat(result, file='plot01.log')
  if (needplot) {
    plot.new()
  }
  del01 <- TRUE
  yrange <- c(0, max(dif))
} else {
  del01 <- FALSE
  yrange <- result
}

o <- is.finite(log(geo))
dif <- dif[o]
geo <- geo[o]
mlog <- lm(dif ~ I(log(geo)))
plot(xrange, yrange, xlab='Geograpic distance (km)', ylab='Linguistic difference', type='n')
points(geo, dif, col='#A0A0A0', pch='.')
lines(g1, d1, col='red', lwd=2)
lines(x, predict(mlog, data.frame(geo = x)), col='blue',  lwd=2)
legend(xrange[2], yrange[1],
       c('log', 'local'),
       xjust=1, yjust=0,
       col=c('blue', 'red'), lwd=2, bty="n")

sink('plot02.log')
print(summary(mlog))
cat('Logarithmic/Actual  R-squared:', cor(dif, predict(mlog, data.frame(geo = geo)))^2, '\n')
cat('Logarithmic/Local   R-squared:', cor(d1[1:n], predict(mlog, data.frame(geo = g1[1:n])))^2, '\n')
sink()

dif <- as.matrix(read.dif('../diff/diff.txt'))
geo <- as.matrix(read.dif('tmp.dst'))

n <- length(geo[,1])

g1 <- rep(0, n)
g2 <- rep(0, n)
g3 <- rep(0, n)
l1 <- rep(0, n)
l2 <- rep(0, n)
l3 <- rep(0, n)

for (i in 1:n) {
    l <- order(dif[,i])
    l1[i] <- geo[l[2], i]
    l2[i] <- geo[l[3], i]
    l3[i] <- geo[l[4], i]
    g <- sort(geo[,i])
    g1[i] <- g[2]
    g2[i] <- g[3]
    g3[i] <- g[4]
}

dens <- function(x, bw,col) {
  #d <- density(x, bw=bw)
  d <- density(x)
  lines(d, lwd=2, col=col)
  m <- median(x)
  p <- d$y[d$x < m]
  lines(c(m,m),c(0,d$y[length(p)]),col=col)
}


col=c("#000000", "#808080", "#C0C0C0", "#0000FF", "#8080FF", "#C0C0FF")

d1 <- density(g1)
bw <- d1$bw
ym <- 1.1 * max(d1$y)
xm <- 1.4 * median(l3)

sub <- sprintf("bandwidth = %.3g km", bw)
sub <- ''

plot(c(0, xm), c(0, ym), type="n", main="", sub = sub, xlab="Distances to nearest neighbour in km", ylab="Density")

dens(l3, bw, col[6])
dens(g3, bw, col[3])
dens(l2, bw, col[5])
dens(g2, bw, col[2])
dens(l1, bw, col[4])
dens(g1, bw, col[1])

legend(xm, ym,
       xjust = 1,
       yjust = 1,
       cex = .8,
       pt.cex = 1,
       legend=c(
         "geographic, 1st",
         "geographic, 2nd",
         "geographic, 3rd",
         "linguistic, 1st",
         "linguistic, 2nd",
         "linguistic, 3rd"),
       lwd = 2,
       col = col
       )

dev.off()

if (del01) {
  unlink('plot01.eps')
}
