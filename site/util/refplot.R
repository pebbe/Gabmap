
postscript(file='plot%02d.eps', width=6, height=5, onefile=FALSE, horizontal=FALSE, paper='a4')
par(mar=c(5, 4, 1, 2) + 0.1)

con <- file('../description', open='rt', encoding='UTF-8')
desc <- readLines(con, n=1)
close(con)

desc <- gsub('&lt;', '<', desc, fixed=TRUE)
desc <- gsub('&gt;', '>', desc, fixed=TRUE)
desc <- gsub('&quot;', '"', desc, fixed=TRUE)
desc <- gsub('&amp;', '&', desc, fixed=TRUE)


con <- file('curplace.txt', open='rt', encoding='UTF-8')
place <- readLines(con, n=1)
close(con)

t <- read.table('curplot.data')

#plot(t, ylim=c(0, max(t[,2])), main=desc, xlab=paste('geographic distance in km from', place), ylab='dialect difference')
plot(t, xlab=paste('geographic distance in km from', place), ylab='dialect difference', col='#A0A0A0')
lines(lowess(t, f=.3),col='blue',lwd=2)

dev.off()
