var DH = 0;
var an = 0;
var al = 0;
var ai = 0;

var DS = null;
var DSvisibleID = null;
var DSvisible = false;
var OI = '';
var timerRunning = false;
var timerID = null;
var timer2Running = false;
var timer2ID = null;
var poppedUp = false;
var mapIdx = -1;

if (document.getElementById) {
    ai = 1;
    DH = 1;
} else {
    if (document.all) {
	al = 1;
	DH = 1;
    } else {
	browserVersion = parseInt(navigator.appVersion);
	if ((navigator.appName.indexOf('Netscape') != -1) && (browserVersion == 4)) {
	    an = 1;
	    DH = 1;
	}
    }
}
function fd(oi, wS) {
    if (ai)
	return wS ? document.getElementById(oi).style : document.getElementById(oi);
    if (al)
	return wS ? document.all[oi].style : document.all[oi];
    if (an)
	return document.layers[oi];
}
function pw() {
    return window.innerWidth != null ? window.innerWidth : document.body.clientWidth != null ? document.body.clientWidth : null;
}
function mouseX(evt) {
    if (evt.pageX)
	return evt.pageX;
    else if (evt.clientX)
	return evt.clientX + (document.documentElement.scrollLeft ?  document.documentElement.scrollLeft : document.body.scrollLeft);
    else
	return null;
}
function mouseY(evt) {
    if (evt.pageY)
	return evt.pageY;
    else if (evt.clientY)
	return evt.clientY + (document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop);
    else
	return null;
}

function stopTimer() {
    if (timerRunning) {
	clearTimeout(timerID);
	timerRunning = false;
    }
}

function stopTimer2() {
    if (timer2Running) {
	clearTimeout(timer2ID);
	timer2Running = false;
    }
}

function doPopUp() {
    if (DSvisible) {
	DSvisibleID.visibility = "hidden"
    }
    DS.visibility = "visible";
    DSvisibleID = DS;
    DSvisible = true;
    stopTimer2();
    poppedUp = true;
}

function popUp(evt,oi) {
    if (DH) {
	var wp = pw();

	//if (DSvisible) {
	//    return null;
	//}

	//if (oi == OI && timerRunning) {
	//    return null;
	//}
	//OI = oi

	if (timerRunning) {
          clearTimeout(timerID);
          timerRunning = false;
        }

	if (DSvisible) {
	    DSvisibleID.visibility = "hidden";
	    DSvisible = false;
	}

	DS = fd(oi,1);
	dm = fd(oi,0);
	st = DS.visibility;
	if (dm.offsetWidth)
	    ew = dm.offsetWidth;
	else if (dm.clip.width)
	    ew = dm.clip.width;
	if (st == "visible" || st == "show") {
	    // DS.visibility = "hidden";
	} else {
	    tv = mouseY(evt) - 15;
	    // lv = mouseX(evt) - (ew/3);
	    lv = mouseX(evt) - 10;
	    if (lv < 2)
		lv = 2;
	    else if (lv + ew > wp)
		lv -= ew/2;
	    if (!an) {
		lv += 'px';
		tv += 'px';
	    }
	    DS.left = lv;
	    DS.top = tv;
	    setTimeout('stopTimer2()', 100);
	    timerID = setTimeout('doPopUp()', 600);
	    timerRunning = true;
	}
    }
}

function popDown(evt,oi) {
    if (DH) {
	ds = fd(oi,1);
	st = ds.visibility;
	if (st == "visible" || st == "show") {
	    ds.visibility = "hidden";
	    DSvisible = false;
	}
    }
    stopTimer2();
    // setTimeout('stopTimer2()', 100);
    poppedUp = false;
}

function restoreImg(e, src) {
    timer2Running = false;
    if (! poppedUp) {
	e.src = src;
    }
}
function restore(e, src) {
    if (! poppedUp) {
	stopTimer2();
	timer2ID = setTimeout(function(){restoreImg(e, src)}, 300);
	timer2Running = true;
    }
}
function setPoints(e, src, idx) {
    if (idx != mapIdx) {
	timerRunning = false;
	timerID = null;
	timer2Running = false;
	timer2ID = null;
	poppedUp = false;
	mapIdx = idx;
    } else {
	stopTimer2();
    }
    e.src = src;
}
