//$Revision: 66253 $
//  originally written	by Tan Ling	Wee	on 2 Dec 2001
//	last updated 23 June 2002
//	email :	fuushikaden@yahoo.com
//	Significantly modified by Arinc Direct

PopCal = function() {
    return {

	fixedX : -1,			// x position (-1 if to appear below control)
	fixedY : -1,			// y position (-1 if to appear below control)
	startAt : 0,			// 0 - sunday ; 1 - monday
	showWeekNumber : 0,	// 0 - don't show; 1 - show
	showToday : 1,		// 0 - don't show; 1 - show
	imgDir : "images/popupcal/",			// directory for images ... e.g. var imgDir="/img/"

	gotoString : "Go To Current Month",
	todayString : "Today is",
	weekString : "Wk",
	scrollLeftMessage : "Click to scroll to previous month. Hold mouse button to scroll automatically.",
	scrollRightMessage : "Click to scroll to next month. Hold mouse button to scroll automatically.",
	selectMonthMessage : "Click to select a month.",
	selectYearMessage : "Click to select a year.",
	selectDateMessage : "Select [date] as date.", // do not replace [date], it will be replaced by date.

    calendarID : 0,
    zuluClock : false,

    crossobj : null,
    crossMonthObj : null,
    crossYearObj : null,
    monthSelected : null,
    yearSelected : null,
    dateSelected : null,
    omonthSelected : null,
    oyearSelected : null,
    odateSelected : null,
    monthConstructed : null,
    yearConstructed : null,
    intervalID1 : null,
    intervalID2 : null,
    timeoutID1 : null,
    timeoutID2 : null,
    ctlToPlaceValue : null,
    ctlNow : null,
    dateFormat : null,
    nStartingYear : null,

	bPageLoaded : false,
	ie : (document.all && !(navigator.appVersion.indexOf('Trident/5') != -1) ),
	dom : document.getElementById,

	ns4 : document.layers,
    today :	new	Date(),
	dateNow	 : new Date().getDate(),
	monthNow : new Date().getMonth(),
	yearNow	 : new Date().getYear(),
	imgsrc : new Array("drop1.gif","drop2.gif","left1.gif","left2.gif","right1.gif","right2.gif"),
	img	: new Array(),

	bShow : false,

    firstUpdate : true,

    updateToday : function (data)
    {
        results = data.responseText.split('|');
        curTime = parseInt(results[0]);
        popIdx = parseInt(results[1]);
        if(popIdx == -1)
            return;
        cal = document.popCalendars[popIdx];
        cal.today = new Date(curTime + cal.today.getTimezoneOffset() * 60000);
        cal.dateNow = cal.today.getDate();
        cal.monthNow = cal.today.getMonth();
        cal.yearNow = cal.today.getYear();
        if(!cal.ie)
        {
             cal.yearNow += 1900;
        }

        if(cal.firstUpdate)
        {
            cal.odateSelected = cal.dateSelected = cal.dateNow;
            cal.omonthSelected = cal.monthSelected = cal.monthNow;
            cal.oyearSelected = cal.yearSelected = cal.yearNow;
			if (cal.showToday==1)
			{
				document.getElementById("lblToday" + cal.calendarID).innerHTML =	cal.todayString + " <a onmousemove='window.status=\""+cal.gotoString+"\"' onmouseout='window.status=\"\"' title='"+cal.gotoString+"' style='"+cal.styleAnchor+"' href='javascript:document.popCalendars[" + cal.calendarID + "].monthSelected=document.popCalendars[" + cal.calendarID + "].monthNow;document.popCalendars[" + cal.calendarID + "].yearSelected=document.popCalendars[" + cal.calendarID + "].yearNow;document.popCalendars[" + cal.calendarID + "].constructCalendar();'>"+cal.dayName[(cal.today.getDay()-cal.startAt==-1)?6:(cal.today.getDay()-cal.startAt)]+", " + cal.dateNow + " " + cal.monthName[cal.monthNow].substring(0,3)	+ "	" +	cal.yearNow	+ "</a>"
			}
            cal.firstUpdate = false;
       }

    },

    doUpdate : function()
    {
      try
      {
          var req = new Ajax.Request("GetTime",
            {
              onSuccess : this.updateToday,
              method : "get"
            });
      }
      catch(e) { return false; }
      return true;
    },

    /* hides <select> and <applet> objects (for IE only) */
    hideElement : function( elmID, overDiv )
    {
      if( this.ie )
      {
        for( i = 0; i < document.all.tags( elmID ).length; i++ )
        {
          obj = document.all.tags( elmID )[i];
          if( !obj || !obj.offsetParent )
          {
            continue;
          }
      
          // Find the element's offsetTop and offsetLeft relative to the BODY tag.
          objLeft   = obj.offsetLeft;
          objTop    = obj.offsetTop;
          objParent = obj.offsetParent;
          while(objParent &&  objParent.tagName.toUpperCase() != "BODY" )
          {
            objLeft  += objParent.offsetLeft;
            objTop   += objParent.offsetTop;
            objParent = objParent.offsetParent;
          }
      
          objHeight = obj.offsetHeight;
          objWidth = obj.offsetWidth;
      
          if(( overDiv.offsetLeft + overDiv.offsetWidth ) <= objLeft );
          else if(( overDiv.offsetTop + overDiv.offsetHeight ) <= objTop );
          else if( overDiv.offsetTop >= ( objTop + objHeight ));
          else if( overDiv.offsetLeft >= ( objLeft + objWidth ));
          else
          {
            obj.style.visibility = "hidden";
          }
        }
      }
    },
     
    /*
    * unhides <select> and <applet> objects (for IE only)
    */
    showElement : function( elmID )
    {
      if( this.ie )
      {
        for( i = 0; i < document.all.tags( elmID ).length; i++ )
        {
          obj = document.all.tags( elmID )[i];
          
          if( !obj || !obj.offsetParent )
          {
            continue;
          }
        
          obj.style.visibility = "";
        }
      }
    },

	HolidayRec : function(d, m, y, desc)
	{
		this.d = d
		this.m = m
		this.y = y
		this.desc = desc
	},

	HolidaysCounter : 0,
	Holidays : new Array(),

	addHoliday : function (d, m, y, desc)
	{
		this.Holidays[this.HolidaysCounter++] = new this.HolidayRec ( d, m, y, desc )
	},


	monthName :	new	Array("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"),
    dayName : new Array	("Sun","Mon","Tue","Wed","Thu","Fri","Sat"),
	styleAnchor : "text-decoration:none;color:black;",
	styleLightBorder : "border-style:solid;border-width:1px;border-color:#a0a0a0;",

	swapImage : function(srcImg, destImg){
		if (this.ie)	
        { 
            img = document.getElementById(srcImg); 
            if(img)
            {
                img.setAttribute("src",this.imgDir + destImg)
            }
        }
        
	},

	init : function(zclock)	{
        this.zuluClock = zclock;


        if(document.popCalendars == null)
        {
            document.popCalendars = new Array();
        }

        document.popCalendars[document.popCalendars.length] = this;
        this.calendarID = document.popCalendars.length - 1;
        

	    if (this.startAt==0)
    	{
            this.dayName = new Array	("Sun","Mon","Tue","Wed","Thu","Fri","Sat")
    	}
    	else
    	{
    		this.dayName = new Array	("Mon","Tue","Wed","Thu","Fri","Sat","Sun")
    	}
	    document.onclick = function hidecal2 () {
            var i;
            for(i=0;i<document.popCalendars.length;i++)
            {
                var cal = document.popCalendars[i];
		        if (!cal.bShow)
		        {
			        cal.hideCalendar()
		        }
		        cal.bShow = false
            }
	    }

    	if (this.dom)
    	{
    		for	(i=0;i<this.imgsrc.length;i++)
    		{
    			this.img[i] = new Image
    			this.img[i].src = this.imgDir + this.imgsrc[i]
    		}
    		document.write ("<div onclick='document.popCalendars[" + this.calendarID + "].bShow=true' id='calendar" + this.calendarID + "'	style='z-index:+999;position:absolute;visibility:hidden;'><table	width="+((this.showWeekNumber==1)?250:220)+ " style='font-family:arial;font-size:11px;border-width:1;border-style:solid;border-color:#a0a0a0;font-family:arial; font-size:11px}' bgcolor='#ffffff'><tr bgcolor='#889dba'><td><table width='"+ ((this.showWeekNumber==1)?248:218)+"'><tr><td style='padding:2px;font-family:arial; font-size:11px;'><font color='#ffffff'><B><span id='caption" + this.calendarID + "'></span></B></font></td><td align=right><a href='javascript:document.popCalendars[" + this.calendarID + "].hideCalendar()'><IMG SRC='"+this.imgDir+"close.gif' WIDTH='15' HEIGHT='13' BORDER='0' ALT='Close the Calendar'></a></td></tr></table></td></tr><tr><td style='padding:5px' bgcolor=#ffffff><span id='content" + this.calendarID + "'></span></td></tr>")
			
    		if (this.showToday==1)
    		{
    			document.write ("<tr bgcolor=#f0f0f0><td style='padding:5px' align=center><span id='lblToday" + this.calendarID + "'></span></td></tr>")
    		}
    			
    		document.write ("</table></div><div id='selectMonth" + this.calendarID + "' style='z-index:+999;position:absolute;visibility:hidden;'></div><div id='selectYear" + this.calendarID + "' style='z-index:+999;position:absolute;visibility:hidden;'></div>");
    	}
		if (!this.ns4)
		{
			if (!this.ie) { this.yearNow += 1900	}

			this.crossobj=document.getElementById("calendar" + this.calendarID).style;
			this.hideCalendar()

			this.crossMonthObj=document.getElementById("selectMonth" + this.calendarID).style;

			this.crossYearObj=document.getElementById("selectYear" + this.calendarID).style;

			this.monthConstructed=false;
			this.yearConstructed=false;

			if (this.showToday==1)
			{
				document.getElementById("lblToday" + this.calendarID).innerHTML =	this.todayString + " <a onmousemove='window.status=\""+this.gotoString+"\"' onmouseout='window.status=\"\"' title='"+this.gotoString+"' style='"+this.styleAnchor+"' href='javascript:document.popCalendars[" + this.calendarID + "].monthSelected=document.popCalendars[" + this.calendarID + "].monthNow;document.popCalendars[" + this.calendarID + "].yearSelected=document.popCalendars[" + this.calendarID + "].yearNow; document.popCalendars[" + this.calendarID + "].constructCalendar();'>"+this.dayName[(this.today.getDay()-this.startAt==-1)?6:(this.today.getDay()-this.startAt)]+", " + this.dateNow + " " + this.monthName[this.monthNow].substring(0,3)	+ "	" +	this.yearNow	+ "</a>"
			}

			sHTML1="<span id='spanLeft'	style='border-style:solid;border-width:1;border-color:#f0f0f0;cursor:pointer' onmouseover='document.popCalendars[" + this.calendarID + "].swapImage(\"changeLeft" + this.calendarID + "\",\"left2.gif\");this.style.borderColor=\"#ffffff\";window.status=\""+this.scrollLeftMessage+"\"' onclick='javascript:document.popCalendars[" + this.calendarID + "].decMonth()' onmouseout='clearInterval(document.popCalendars[" + this.calendarID + "].intervalID1);document.popCalendars[" + this.calendarID + "].swapImage(\"changeLeft" + this.calendarID + "\",\"left1.gif\");this.style.borderColor=\"#f0f0f0\";window.status=\"\"' onmousedown='clearTimeout(document.popCalendars[" + this.calendarID + "].timeoutID1);document.popCalendars[" + this.calendarID + "].timeoutID1=setTimeout(\"document.popCalendars[" + this.calendarID + "].StartDecMonth()\",500)'	onmouseup='clearTimeout(document.popCalendars[" + this.calendarID + "].timeoutID1);clearInterval(document.popCalendars[" + this.calendarID + "].intervalID1)'>&nbsp<IMG id='changeLeft" + this.calendarID + "' SRC='"+this.imgDir+"left1.gif' width=10 height=11 BORDER=0>&nbsp</span>&nbsp;"
			sHTML1+="<span id='spanRight' style='border-style:solid;border-width:1;border-color:#f0f0f0;cursor:pointer'	onmouseover='document.popCalendars[" + this.calendarID + "].swapImage(\"changeRight\",\"right2.gif\");this.style.borderColor=\"#ffffff\";window.status=\""+this.scrollRightMessage+"\"' onmouseout='clearInterval(document.popCalendars[" + this.calendarID + "].intervalID1);document.popCalendars[" + this.calendarID + "].swapImage(\"changeRight\",\"right1.gif\");this.style.borderColor=\"#f0f0f0\";window.status=\"\"' onclick='document.popCalendars[" + this.calendarID + "].incMonth()' onmousedown='clearTimeout(document.popCalendars[" + this.calendarID + "].timeoutID1);document.popCalendars[" + this.calendarID + "].timeoutID1=setTimeout(\"document.popCalendars[" + this.calendarID + "].StartIncMonth()\",500)'	onmouseup='clearTimeout(document.popCalendars[" + this.calendarID + "].timeoutID1);clearInterval(document.popCalendars[" + this.calendarID + "].intervalID1)'>&nbsp<IMG id='changeRight' SRC='"+this.imgDir+"right1.gif'	width=10 height=11 BORDER=0>&nbsp</span>&nbsp"
			sHTML1+="<span id='spanMonth" + this.calendarID + "' style='border-style:solid;border-width:1;border-color:#f0f0f0;cursor:pointer'	onmouseover='document.popCalendars[" + this.calendarID + "].swapImage(\"changeMonth\",\"drop2.gif\");this.style.borderColor=\"#ffffff\";window.status=\""+this.selectMonthMessage+"\"' onmouseout='document.popCalendars[" + this.calendarID + "].swapImage(\"changeMonth\",\"drop1.gif\");this.style.borderColor=\"#f0f0f0\";window.status=\"\"' onclick='document.popCalendars[" + this.calendarID + "].popUpMonth()'></span>&nbsp;"
			sHTML1+="<span id='spanYear" + this.calendarID + "' style='border-style:solid;border-width:1;border-color:#f0f0f0;cursor:pointer' onmouseover='document.popCalendars[" + this.calendarID + "].swapImage(\"changeYear\",\"drop2.gif\");this.style.borderColor=\"#ffffff\";window.status=\""+this.selectYearMessage+"\"'	onmouseout='document.popCalendars[" + this.calendarID + "].swapImage(\"changeYear\",\"drop1.gif\");this.style.borderColor=\"#f0f0f0\";window.status=\"\"'	onclick='document.popCalendars[" + this.calendarID + "].popUpYear()'></span>&nbsp;"
			
			document.getElementById("caption" + this.calendarID).innerHTML  =	sHTML1

			this.bPageLoaded=true
		}
	},

	hideCalendar : function()	{
        if (!this.crossobj) { return; }
		this.crossobj.visibility="hidden"
		if (this.crossMonthObj != null){this.crossMonthObj.visibility="hidden"}
		if (this.crossYearObj !=	null){this.crossYearObj.visibility="hidden"}

	    this.showElement( 'SELECT' );
		this.showElement( 'APPLET' );
	},

	padZero : function(num) {
		return (num	< 10)? '0' + num : num ;
	},

	constructDate : function(d,m,y)
	{
		sTmp = this.dateFormat
		sTmp = sTmp.replace	("dd","<e>");
		sTmp = sTmp.replace	("d","<d>");
		sTmp = sTmp.replace	("<e>",this.padZero(d));
		sTmp = sTmp.replace	("<d>",d);
		sTmp = sTmp.replace	("mmm","<o>");
		sTmp = sTmp.replace	("mm","<n>");
		sTmp = sTmp.replace	("m","<m>");
		sTmp = sTmp.replace	("<m>",m+1);
		sTmp = sTmp.replace	("<n>",this.padZero(m+1));
		sTmp = sTmp.replace	("<o>",this.monthName[m]);
		sTmp = sTmp.replace     ("yyyy",y);
		sTmp = sTmp.replace     ("yy",(""+y).substr(2,2));
		return sTmp
	},

	closeCalendar : function() 
    {
		var	sTmp;

		this.hideCalendar();
		this.ctlToPlaceValue.value =	this.constructDate(this.dateSelected,this.monthSelected,this.yearSelected)
		    //if (ctlToPlaceValue.onchange){ctlToPlaceValue.onchange();}
		// fire onchange the proper way
 		//var evt = document.createEvent("HTMLEvents");
		//evt.initEvent( 'change', true, true );
		//ctlToPlaceValue.dispatchEvent(evt);
		if (document.createEventObject){
		    // dispatch for IE
		    var evt = document.createEventObject();
		    this.ctlToPlaceValue.fireEvent('onchange',evt)
		}
		else{
		    // disptach for firefox + others
		    var evt = document.createEvent("HTMLEvents");
		    evt.initEvent('change', true, true ); // event type,bubbling,cancelable
		    this.ctlToPlaceValue.dispatchEvent(evt);
		}
	},

	/*** Month Pulldown	***/

	StartDecMonth : function()
	{
        window.currentOpenCalendar = this;
		this.intervalID1=setInterval("window.currentOpenCalendar.decMonth()",80)
	},

	StartIncMonth : function()
	{
        window.currentOpenCalendar = this;
		this.intervalID1=setInterval("window.currentOpenCalendar.incMonth()",80)
	},

	incMonth : function () 
    {
		this.monthSelected++
		if (this.monthSelected>11) {
			this.monthSelected=0
			this.yearSelected++
		}
		this.constructCalendar()
	},

	decMonth : function () 
    {
		this.monthSelected--
		if (this.monthSelected<0) {
			this.monthSelected=11
			this.yearSelected--
		}
		this.constructCalendar()
	},

	constructMonth : function() {
		this.popDownYear()
		if (!this.monthConstructed) {
			sHTML =	""
			for	(i=0; i<12;	i++) {
				sName =	this.monthName[i];
				if (i==this.monthSelected){
					sName =	"<B>" +	sName +	"</B>"
				}
				sHTML += "<tr><td id='m" + i + "' onmouseover='this.style.backgroundColor=\"#FFFFcc\"' onmouseout='this.style.backgroundColor=\"\"' style='cursor:pointer' onclick='document.popCalendars[" + this.calendarID + "].monthConstructed=false;document.popCalendars[" + this.calendarID + "].monthSelected=" + i + ";document.popCalendars[" + this.calendarID + "].constructCalendar();document.popCalendars[" + this.calendarID + "].popDownMonth();event.cancelBubble=true'>&nbsp;" + sName + "&nbsp;</td></tr>"
			}

			document.getElementById("selectMonth" + this.calendarID).innerHTML = "<table width=70	style='font-family:arial; font-size:11px; border-width:1; border-style:solid; border-color:#f0f0f0;' bgcolor='#FFFFF5' cellspacing=0 onmouseover='clearTimeout(document.popCalendars[" + this.calendarID + "].timeoutID1)'	onmouseout='clearTimeout(document.popCalendars[" + this.calendarID + "].timeoutID1);document.popCalendars[" + this.calendarID + "].timeoutID1=setTimeout(\"document.popCalendars[" + this.calendarID + "].popDownMonth()\",100);event.cancelBubble=true'>" +	sHTML +	"</table>"

			this.monthConstructed=true
		}
	},

	popUpMonth : function() {
		this.constructMonth()
		this.crossMonthObj.visibility = (this.dom||this.ie)? "visible"	: "show"
		this.crossMonthObj.left = parseInt(this.crossobj.left) + 50
		this.crossMonthObj.top =	parseInt(this.crossobj.top) + 26

		this.hideElement( 'SELECT', document.getElementById("selectMonth" + this.calendarID) );
		this.hideElement( 'APPLET', document.getElementById("selectMonth" + this.calendarID) );			
	},

	popDownMonth : function()	{
		this.crossMonthObj.visibility= "hidden"
	},

	/*** Year Pulldown ***/

	incYear : function() 
    {
		for	(i=0; i<7; i++){
			newYear	= (i+this.nStartingYear)+1
			if (newYear==this.yearSelected)
			{ txtYear =	"&nbsp;<B>"	+ newYear +	"</B>&nbsp;" }
			else
			{ txtYear =	"&nbsp;" + newYear + "&nbsp;" }
			document.getElementById("y"+i).innerHTML = txtYear
		}
		this.nStartingYear ++;
		this.bShow=true
	},

	decYear : function() 
    {
		for	(i=0; i<7; i++){
			newYear	= (i+this.nStartingYear)-1
			if (newYear==this.yearSelected)
			{ txtYear =	"&nbsp;<B>"	+ newYear +	"</B>&nbsp;" }
			else
			{ txtYear =	"&nbsp;" + newYear + "&nbsp;" }
			document.getElementById("y"+i).innerHTML = txtYear
		}
		this.nStartingYear --;
		this.bShow=true
	},

	selectYear : function(nYear) 
    {
		this.yearSelected=parseInt(nYear+this.nStartingYear);
		this.yearConstructed=false;
		this.constructCalendar();
		this.popDownYear();
	},

	constructYear : function() 
    {
		this.popDownMonth()
		sHTML =	""
		if (!this.yearConstructed) {

			sHTML =	"<tr><td align='center'	onmouseover='this.style.backgroundColor=\"#FFFFcc\"' onmouseout='clearInterval(document.popCalendars[" + this.calendarID + "].intervalID1);this.style.backgroundColor=\"\"' style='cursor:pointer'	onmousedown='clearInterval(document.popCalendars[" + this.calendarID + "].intervalID1);document.popCalendars[" + this.calendarID + "].intervalID1=setInterval(\"document.popCalendars[" + this.calendarID + "].decYear()\",30)' onmouseup='clearInterval(document.popCalendars[" + this.calendarID + "].intervalID1)'>-</td></tr>"

			j =	0
			this.nStartingYear =	this.yearSelected-3
			for	(i=(this.yearSelected-3); i<=(this.yearSelected+3); i++) {
				sName =	i;
				if (i==this.yearSelected){
					sName =	"<B>" +	sName +	"</B>"
				}

				sHTML += "<tr><td id='y" + j + "' onmouseover='this.style.backgroundColor=\"#FFFFDD\"' onmouseout='this.style.backgroundColor=\"\"' style='cursor:pointer' onclick='document.popCalendars[" + this.calendarID + "].selectYear("+j+");event.cancelBubble=true'>&nbsp;" + sName + "&nbsp;</td></tr>"
				j ++;
			}

			sHTML += "<tr><td align='center' onmouseover='this.style.backgroundColor=\"#FFFFDD\"' onmouseout='clearInterval(document.popCalendars[" + this.calendarID + "].intervalID2);this.style.backgroundColor=\"\"' style='cursor:pointer' onmousedown='clearInterval(document.popCalendars[" + this.calendarID + "].intervalID2);document.popCalendars[" + this.calendarID + "].intervalID2=setInterval(\"document.popCalendars[" + this.calendarID + "].incYear()\",30)'	onmouseup='clearInterval(document.popCalendars[" + this.calendarID + "].intervalID2)'>+</td></tr>"

			document.getElementById("selectYear" + this.calendarID).innerHTML	= "<table width=44 style='font-family:arial; font-size:11px; border-width:1; border-style:solid; border-color:#666666;'	bgcolor='#FFFFf5' onmouseover='clearTimeout(document.popCalendars[" + this.calendarID + "].timeoutID2)' onmouseout='clearTimeout(document.popCalendars[" + this.calendarID + "].timeoutID2);document.popCalendars[" + this.calendarID + "].timeoutID2=setTimeout(\"document.popCalendars[" + this.calendarID + "].popDownYear()\",100)' cellspacing=0>"	+ sHTML	+ "</table>"

			this.yearConstructed	= true
		}
	},

	popDownYear : function() 
    {
		clearInterval(this.intervalID1)
		clearTimeout(this.timeoutID1)
		clearInterval(this.intervalID2)
		clearTimeout(this.timeoutID2)
		this.crossYearObj.visibility= "hidden"
	},

	popUpYear : function() 
    {
		var	leftOffset;

		this.constructYear()
		this.crossYearObj.visibility	= (this.dom||this.ie)? "visible" : "show"
		leftOffset = parseInt(this.crossobj.left) + document.getElementById("spanYear" + this.calendarID).offsetLeft
		if (this.ie)
		{
			leftOffset += 6
		}
		this.crossYearObj.left =	leftOffset
		this.crossYearObj.top = parseInt(this.crossobj.top) +	26
	},

	/*** calendar ***/
   WeekNbr : function(n) {
      // Algorithm used:
      // From Klaus Tondering's Calendar document (The Authority/Guru)
      // hhtp://www.tondering.dk/claus/calendar.html
      // a = (14-month) / 12
      // y = year + 4800 - a
      // m = month + 12a - 3
      // J = day + (153m + 2) / 5 + 365y + y / 4 - y / 100 + y / 400 - 32045
      // d4 = (J + 31741 - (J mod 7)) mod 146097 mod 36524 mod 1461
      // L = d4 / 1460
      // d1 = ((d4 - L) mod 365) + L
      // WeekNumber = d1 / 7 + 1
 
      year = n.getFullYear();
      month = n.getMonth() + 1;
      if (this.startAt == 0) {
         day = n.getDate() + 1;
      }
      else {
         day = n.getDate();
      }
 
      a = Math.floor((14-month) / 12);
      y = year + 4800 - a;
      m = month + 12 * a - 3;
      b = Math.floor(y/4) - Math.floor(y/100) + Math.floor(y/400);
      J = day + Math.floor((153 * m + 2) / 5) + 365 * y + b - 32045;
      d4 = (((J + 31741 - (J % 7)) % 146097) % 36524) % 1461;
      L = Math.floor(d4 / 1460);
      d1 = ((d4 - L) % 365) + L;
      week = Math.floor(d1/7) + 1;
 
      return week;
   },





	__constructCalendar : function (data) 
    {

        var cal = null;
        if(data != null)
        {
            var response = data.responseText.split('|');

            var calIdx = response[1];
            cal = document.popCalendars[calIdx];
            cal.updateToday(data);
        }
        else
        {
            cal = this;
        }
        
		var aNumDays = Array (31,0,31,30,31,30,31,31,30,31,30,31);

		var dateMessage;
		var	startDate =	new	Date (cal.yearSelected,cal.monthSelected,1);
		var endDate;

		if (cal.monthSelected==1)
		{
			endDate	= new Date (cal.yearSelected,cal.monthSelected+1,1);
			endDate	= new Date (endDate	- (24*60*60*1000));
			numDaysInMonth = endDate.getDate()
		}
		else
		{
			numDaysInMonth = aNumDays[cal.monthSelected];
		}

		datePointer	= 0
		dayPointer = startDate.getDay() - cal.startAt
		
		if (dayPointer<0)
		{
			dayPointer = 6
		}

		sHTML =	"<table	 border=0 style='font-family:verdana;font-size:10px;'><tr>"

		if (cal.showWeekNumber==1)
		{
			sHTML += "<td width=27><b>" + cal.weekString + "</b></td><td width=1 rowspan=7 bgcolor='#d0d0d0' style='padding:0px'><img src='"+cal.imgDir+"divider.gif' width=1></td>"
		}

		for	(i=0; i<7; i++)	{
			sHTML += "<td width='27' align='right'><B>"+ cal.dayName[i]+"</B></td>"
		}
		sHTML +="</tr><tr>"
		
		if (cal.showWeekNumber==1)
		{
			sHTML += "<td align=right>" + cal.WeekNbr(startDate) + "&nbsp;</td>"
		}

		for	( var i=1; i<=dayPointer;i++ )
		{
			sHTML += "<td>&nbsp;</td>"
		}
	
		for	( datePointer=1; datePointer<=numDaysInMonth; datePointer++ )
		{
			dayPointer++;
			sHTML += "<td align=right>"
			sStyle=cal.styleAnchor
			if ((datePointer==cal.odateSelected) &&	(cal.monthSelected==cal.omonthSelected)	&& (cal.yearSelected==cal.oyearSelected))
			{ sStyle+=cal.styleLightBorder }

			sHint = ""
			for (k=0;k<cal.HolidaysCounter;k++)
			{
				if ((parseInt(cal.Holidays[k].d)==datePointer)&&(parseInt(cal.Holidays[k].m)==(cal.monthSelected+1)))
				{
					if ((parseInt(cal.Holidays[k].y)==0)||((parseInt(cal.Holidays[k].y)==cal.yearSelected)&&(parseInt(cal.Holidays[k].y)!=0)))
					{
						sStyle+="background-color:#FFDDDD;"
						sHint+=sHint==""?cal.Holidays[k].desc:"\n"+cal.Holidays[k].desc
					}
				}
			}

			var regexp= /\"/g
			sHint=sHint.replace(regexp,"&quot;")

			dateMessage = "onmousemove='window.status=\""+cal.selectDateMessage.replace("[date]",cal.constructDate(datePointer,cal.monthSelected,cal.yearSelected))+"\"' onmouseout='window.status=\"\"' "

			if ((datePointer==cal.dateNow)&&(cal.monthSelected==cal.monthNow)&&(cal.yearSelected==cal.yearNow))
			{ sHTML += "<b><a "+dateMessage+" title=\"" + sHint + "\" style='"+sStyle+"' href='javascript:document.popCalendars[" + cal.calendarID + "].dateSelected="+datePointer+";document.popCalendars[" + cal.calendarID + "].closeCalendar();'><font color=#ff0000>&nbsp;" + datePointer + "</font>&nbsp;</a></b>";
            }
			else if	(dayPointer % 7 == (cal.startAt * -1)+1)
			{ sHTML += "<a "+dateMessage+" title=\"" + sHint + "\" style='"+sStyle+"' href='javascript:document.popCalendars[" + cal.calendarID + "].dateSelected="+datePointer + ";document.popCalendars[" + cal.calendarID + "].closeCalendar();'>&nbsp;" + datePointer + "&nbsp;</a>" }
			else
			{ sHTML += "<a "+dateMessage+" title=\"" + sHint + "\" style='"+sStyle+"' href='javascript:document.popCalendars[" + cal.calendarID + "].dateSelected="+datePointer + ";document.popCalendars[" + cal.calendarID + "].closeCalendar();'>&nbsp;" + datePointer + "&nbsp;</a>" }

			sHTML += ""
			if ((dayPointer+cal.startAt) % 7 == cal.startAt) { 
				sHTML += "</tr><tr>" 
				if ((cal.showWeekNumber==1)&&(datePointer<numDaysInMonth))
				{
					sHTML += "<td align=right>" + (cal.WeekNbr(new Date(cal.yearSelected,cal.monthSelected,datePointer+1))) + "&nbsp;</td>"
				}
			}
		}

		document.getElementById("content" + cal.calendarID).innerHTML   = sHTML
		document.getElementById("spanMonth" + cal.calendarID).innerHTML = "&nbsp;" +	cal.monthName[cal.monthSelected] + "&nbsp;<IMG id='changeMonth' SRC='"+cal.imgDir+"drop1.gif' WIDTH='12' HEIGHT='10' BORDER=0>"
		document.getElementById("spanYear" + cal.calendarID).innerHTML =	"&nbsp;" + cal.yearSelected	+ "&nbsp;<IMG id='changeYear' SRC='"+cal.imgDir+"drop1.gif' WIDTH='12' HEIGHT='10' BORDER=0>"
	},

     popUpCalendar : function(ctl,	ctl2, format) 
     {
		var	leftpos=0
		var	toppos=0

        this.ctl2 = ctl2;

		if (this.bPageLoaded)
		{
			if ( this.crossobj.visibility ==	"hidden" ) {
				this.ctlToPlaceValue	= ctl2
				this.dateFormat=format;

				formatChar = " "
				aFormat	= this.dateFormat.split(formatChar)
				if (aFormat.length<3)
				{
					formatChar = "/"
					aFormat	= this.dateFormat.split(formatChar)
					if (aFormat.length<3)
					{
						formatChar = "."
						aFormat	= this.dateFormat.split(formatChar)
						if (aFormat.length<3)
						{
							formatChar = "-"
							aFormat	= this.dateFormat.split(formatChar)
							if (aFormat.length<3)
							{
								// invalid date	format
								formatChar=""
							}
						}
					}
				}

				tokensChanged =	0
				if ( formatChar	!= "" )
				{
					// use user's date
					aData =	ctl2.value.split(formatChar)
					for	(i=0;i<3;i++)
					{
						if ((aFormat[i]=="d") || (aFormat[i]=="dd"))
						{
							this.odateSelected=this.dateSelected = parseInt(aData[i], 10);
							tokensChanged ++;
						}
						else if	((aFormat[i]=="m") || (aFormat[i]=="mm"))
						{
							this.odateSelected=this.monthSelected =	parseInt(aData[i], 10) - 1;
							tokensChanged ++;
						}
						else if	(aFormat[i]=="yyyy")
						{
							this.oyearSelected = this.yearSelected = parseInt(aData[i], 10);
							tokensChanged ++
						}
						else if	(aFormat[i]=="mmm")
						{
							for	(j=0; j<12;	j++)
							{
								if (aData[i]==this.monthName[j])
								{
									this.monthSelected=j
									tokensChanged ++
								}
							}
						}
					}
				}

				if ((tokensChanged!=3)||isNaN(this.dateSelected)||isNaN(this.monthSelected)||isNaN(this.yearSelected))
				{
					this.dateSelected = this.dateNow
					this.monthSelected =	this.monthNow
					this.yearSelected = this.yearNow
				}

				this.odateSelected=this.dateSelected
				this.omonthSelected=this.monthSelected
				this.oyearSelected=this.yearSelected

				aTag = ctl
				do {
					aTag = aTag.offsetParent;
					if(aTag){
                                            leftpos += aTag.offsetLeft;
					    toppos += aTag.offsetTop;
					}
				} while(aTag && aTag.tagName!="BODY");

				this.crossobj.left =	this.fixedX==-1 ? ctl.offsetLeft	+ leftpos :	this.fixedX
				this.crossobj.top = this.fixedY==-1 ?	ctl.offsetTop +	toppos + ctl.offsetHeight +	2 :	this.fixedY
				this.constructCalendar();
				this.crossobj.visibility=(this.dom||this.ie)? "visible" : "show"

				this.hideElement( 'SELECT', document.getElementById("calendar" + this.calendarID) );
				this.hideElement( 'APPLET', document.getElementById("calendar" + this.calendarID) );			

				this.bShow = true;
			}
			else
			{
				this.hideCalendar()
				if (this.ctlNow!=ctl) {this.popUpCalendar(ctl, ctl2, format)}
			}
			this.ctlNow = ctl
		}
	},

    dummyConstructCalendar : function() 
    {
        this.__constructCalendar(null);
    },

    constructCalendar : function() 
    {
        if(!this.zuluClock)
        {
            this.__constructCalendar(null);
        }
        else
        { 
            if(getDateFromText(this.ctl2.value) == false)
            {
                var req = new Ajax.Request("GetTime",
                {
                    parameters : "calID=" + this.calendarID,
                    onSuccess : document.popCalendars[this.calendarID].__constructCalendar,
                    onFailure : document.popCalendars[this.calendarID].dummyConstructCalendar,
                    method : "post"
                });
            }
            else
            {
                this.__constructCalendar(null);
            }
         }   
     }
/*
	document.onkeypress = function hidecal1 () { 
		if (event.keyCode==27) 
		{
			this.hideCalendar()
		}
	}
*/
}
}

zuluCalendar = PopCal();
zuluCalendar.init(true);
lclCalendar = PopCal();
lclCalendar.init(false);
