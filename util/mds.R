
library(iL04)

colors <- c(
'1\n1\n0.9979133',
'1\n1\n0.951178',
'1\n1\n0.904911',
'1\n1\n0.8595787',
'0.9936441\n0.9975165\n0.8157186',
'0.9766634\n0.9908928\n0.7751566',
'0.9537174\n0.9819685\n0.7408325',
'0.9261637\n0.971293\n0.7157217',
'0.8940859\n0.9588669\n0.7015761',
'0.853902\n0.9431143\n0.6966288',
'0.8013755\n0.9221774\n0.698484',
'0.7328502\n0.8944876\n0.7048092',
'0.6514241\n0.8618412\n0.7140098',
'0.5645519\n0.8282048\n0.7249673',
'0.4797463\n0.797567\n0.7365706',
'0.4021244\n0.7716024\n0.7476638',
'0.3317804\n0.7471322\n0.7569964',
'0.268176\n0.7203667\n0.7633064',
'0.2111159\n0.6878304\n0.76541',
'0.1631302\n0.6485423\n0.7627474',
'0.1280489\n0.6027108\n0.7550558',
'0.1096479\n0.5505687\n0.7420829',
'0.1079946\n0.4933524\n0.7240725',
'0.1174074\n0.4338541\n0.7020381',
'0.1317104\n0.3750003\n0.6770591',
'0.1449949\n0.3195292\n0.6498102',
'0.1528481\n0.2691288\n0.6187012',
'0.1513770\n0.2251213\n0.5813547',
'0.1368118\n0.1887735\n0.5354694',
'0.1090943\n0.1596755\n0.481082',
'0.07245721\n0.1354784\n0.4209323',
'0.03137255\n0.1137255\n0.3579104')

ncolors <- length(colors)

k <- 10

d <- read.dif('../diff/diff.txt', encoding='iso-8859-1')
d1 <- (d - mean(d)) / sd(d)

if (k >= attributes(d)$Size) {
  k <- attributes(d)$Size - 1
}

#if (any(d == 0.0)) {
  sets <- c(FALSE)
#} else {
#  sets <- c(FALSE, TRUE)
#}

rvals = rep(NA, length.out=k)
rvals1 = rep(NA, length.out=k)
svals = rep(NA, length.out=k+1)
names(rvals) <- 1:k

for (kruskal in sets) {

  if (kruskal) {
    prefix <- 'kruskal'
    mds <- ISOMDS(d, k)
  } else {
    prefix <- 'standard'
    mds <- MDS(d, k)
  }

  for (i in 1:k) {

    if (! any(is.na(mds[,i]))) {
    
      dd <- dist(mds[,1:i])
      stopifnot(all(labels(d) == labels(dd)))
      con <- file(sprintf('%s%02ic.cor', prefix, i), open="wt")
      allcor <- cor(d, dd)
      cat(allcor, '\n', file=con, sep='')
      close(con)

      rvals[i] <- allcor
    
      con <- file(sprintf('%s%02i.stress', prefix, i), open="wt")
      d2 <- (dd - mean(dd)) / sd(dd)
      stress <- sqrt(sum((d1 - d2) ^ 2) / sum(d1^2))
      cat(stress, '\n', file=con, sep='')
      close(con)

      svals[i+1] <- stress

      dd <- dist(mds[,i])
      stopifnot(all(labels(d) == labels(dd)))
      con <- file(sprintf('%s%02i.cor', prefix, i), open="wt")
      allcor <- cor(d, dd)
      cat(allcor, '\n', file=con, sep='')
      close(con)

      rvals1[i] <- allcor
    }
  }
  
  n <- length(mds[,1])

  con <- file(sprintf('%s.tmp', prefix), open='wt', encoding='iso-8859-1')
  write.vec(mds[,1:3], con)
  close(con)

  for (i in 1:k) {
    if (! any(is.na(mds[,i]))) {
      fmin <- min(mds[,i])
      fmax <- max(mds[,i])
      con <- file(sprintf('%s%02i.rgb', prefix, i), open='wt', encoding='iso-8859-1')
      cat('3\n', file=con)
      for (j in 1:n) {
        cat(rownames(mds)[j], '\n', sep='', file=con)
        f <- as.integer((mds[j, i] - fmin) / (fmax - fmin) * ncolors)
        if (f > ncolors - 1) {
          f <- ncolors - 1
        }
        cat(colors[f + 1], '\n', sep='', file=con)
      }
      close(con)
    }
  }
}

con <- file('../description', open='rt', encoding='UTF-8')
desc <- readLines(con, n=1)
close(con)

desc <- gsub('&lt;', '<', desc, fixed=TRUE)
desc <- gsub('&gt;', '>', desc, fixed=TRUE)
desc <- gsub('&quot;', '"', desc, fixed=TRUE)
desc <- gsub('&amp;', '&', desc, fixed=TRUE)

numbers <- 1:length(rvals)

o <- (! is.na(rvals)) & (! is.na(rvals1))
rvals <- rvals[o]
rvals1 <- rvals1[o]
numbers <- numbers[o]

y1 <- min(0, rvals)

m <- matrix(ncol=length(rvals), nrow=2)
m[1,] <- rvals1
m[2,] <- rvals

postscript(file='plot%02d.eps', width=6, height=4.5, onefile=FALSE, horizontal=FALSE, paper='a4')
par(mar=c(4, 4, 1, 2) + 0.1)
barplot(m, beside=TRUE, ylim=c(y1,1), xlab=expression(plain('Dark: dimension ')*italic(n)*plain('  -  Light: first ')*italic(n)*plain(' dimensions')), ylab="Correlation", names.arg=numbers) #,space=.5)

#svals[1] <- 1
numbers <- 0:(length(svals)-1)
o <- (! is.na(svals))
svals <- svals[o]
numbers <- numbers[o]

barplot(svals, space=.5, xlab=expression(plain('First ')*italic(n)*plain(' dimensions')), ylab="Stress", names.arg=numbers)

dev.off()
