

library(iL04)

differences <- as.vector(read.dif('diff.txt'))

con <- file('../description', open='rt', encoding='UTF-8')
desc <- readLines(con, n=1)
close(con)

desc <- gsub('&lt;', '<', desc, fixed=TRUE)
desc <- gsub('&gt;', '>', desc, fixed=TRUE)
desc <- gsub('&quot;', '"', desc, fixed=TRUE)
desc <- gsub('&amp;', '&', desc, fixed=TRUE)

postscript(file='diff%02d.eps', width=6, height=5, onefile=FALSE, horizontal=FALSE, paper='a4')
par(mar=c(5, 4, 1, 2) + 0.1)

# histogram met normaalcurve
histnorm <- function(x,
                     freq = NULL, probability = !freq,
                     main = paste("Histogram and normal curve of" , xname),
                     xlab = xname,
                     clwd = 2, ccol = "black",
                     ...) {
    xname <- deparse(substitute(x))
    if (is.null(freq) && !missing(probability)) {
        freq <- !as.logical(probability)
    }
    h <- hist(x, plot = FALSE, freq = freq, ...)
    i <- h$breaks[1]
    j <- h$breaks[length(h$breaks)]
    xx <- seq(i, j, length = 100)
    yy <- dnorm(xx, mean(x), sd(x))
    if (is.null(freq)) {
        freq <- h$equidist
    }
    if (freq) {
        yy = yy * (j - i) / (length(h$breaks) - 1) * length(x)
        ymax = max(yy, h$count)
    } else {
        ymax = max(yy, h$density)
    }
    hist(x, freq = freq, ylim = c(0, ymax), main = main, xlab = xlab, ...)
    lines(xx, yy, lwd = clwd, col = ccol)
}

histnorm(differences^2, ccol='blue', col='grey', breaks=40, xlab=expression(Differences^2), main=NULL)

dev.off()
