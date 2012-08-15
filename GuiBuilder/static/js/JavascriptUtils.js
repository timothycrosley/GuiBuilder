//$Revision: 67389 $
/* Javascript Utils
 *
 * Contains general functions which ease the usage of multi-browser Javascript coding
 * and are unrelated to Prototype, or other javascript libraries.
 *
 * JUGetElement(element) -- returns an element where the given element can be represented by
 *                          an id, name, or actual element
 *
 * JUGetElementByClassName(classname, parentNode) -- returns the first element within
 *                                                parentNode that has a certain classname
 *
 * JUGetElementsByClassName(className, parentNode) -- returns all elements with a certain
 *                                                 class name contained within parentNode
 *
 * JUPeer(element, className) -- returns a an element with the same parent as element where
 *                                       the class == className
 *
 * JUFirstChildElement(element) -- returns the first(non-empty) child element of element
 *
 * JULastChildElement(element) -- returns the last(none-empty) child element of element
 *
 * JUNextElement(element) -- returns the next(non-empty) sibling of element.
 *
 * JUPrevElement(element) -- returns the previous(non-empty) sibling of element.
 *
 * JUParentElement(element, className) -- returns the parent(non-empty) of the current element.
 *                                      with classname
 *
 * hideElement(element) -- hides an element by setting its display property to none
 *
 * showElement(element) -- shows an element by setting its display property to block
 *
 * JUElementShown(element) -- return true if the elements display property is set to block
 *
 * JURemoveElement(element) -- safely removes an element from the page
 *
 * JUContains(text, subtext, caseSensitive) -- checks if text JUContains subtext
 *
 * JUDoInPageJavascript() -- performs javascript contained in elements with the class
 *                         'onLoadJavascript' - meant to enable javascript to be
 *                          called from within a page after an AJAX update
 *
 * JUPixelsAbove(element) -- returns the number of pixels above an element
 *
 * JUPixelsBelow(element) -- returns the number of pixels below an element
 *
 * JUSetAbsoluteRelativeToParent(element, pixelsDown, pixelsToRight) -- sets the absolute
 *          position of an element to that of its parent + pixelsDown & pixelsToRight
 *
 * JUDisplayDropDown(dropDown) -- displays dropDown right below its parent element
 *
 * JUSelectedOptions(selectBox) -- returns the items in the select box that are selected
 *
 * JUSelectedOption(selectBox) -- returns the first selected  item from a list
 *
 * JUMove(element, to) -- moves element out of its current location and places at the end
 * JUCopy(element, to) -- makes a copy of an element appending it at the end of to
 *
 * JUSetPrefix(element, prefix) -- sets the prefix for element (and all children) to
 *                                   prefix
 *
 * JURedraw(element) -- forces the browser to redraw the element (works only for shown elements)
 *
 * JUChildElements(element) - returns all non-empty child elements of an element
 */


var TAB = 9;
var ENTER = 13;
var DOWN_ARROW = 40;

var currentDropDown = null;
var currentButton = null;

//returns the element given (if it is a page element) or the result of getElementId
function JUGetElement(element)
{
    //If an actual element is given (or nothing is given) just return it
    if(!element || element.innerHTML != null || element == document)
    {
        return element;
    }

    //If a element id is given -- return the element associated with the id
    var idElement = document.getElementById(element);
    if(idElement != null && idElement.innerHTML != null)
    {
        return idElement;
    }

    //If a element name is given -- return the first element associated with the name
    var nameElement = document.getElementsByName(element);
    if(nameElement.length != 0 && nameElement[0].innerHTML != null)
    {
        return nameElement[0]
    }

    return null;
}

function JUGetValue(element)
{
    var element = JUGetElement(element)
    if (element)
    {
        return element.value;
    }

    return ""
}

//Hides Elements with a particular class name
function JUHideClass(className, parentNode)
{
    var elements = JUGetElementsByClassName(className, parentNode);
    for(var currentElement=0; currentElement < elements.length; currentElement++)
    {
        var element = elements[currentElement];
        JUHideElement(element)
    }
}

//Shows Elements with a particular class name
function JUShowClass(className, parentNode)
{
    var elements = JUGetElementsByClassName(className, parentNode);
    for(var currentElement=0; currentElement < elements.length; currentElement++)
    {
        var element = elements[currentElement];
        JUShowElement(element);
    }
}


//Creates a throbber on the fly
function JUBuildThrobber()
{
    var throbber = document.createElement('img');
    throbber.src = 'images/loop-grey.gif';
    return throbber;
}

//Gets elements by there css class that are childern of a certain node
function JUGetElementsByClassName(classname, parentNode)
{
    parentNode = JUGetElement(parentNode);
    if(document.getElementByClassName){
        if(parentNode)
        {
            parentNode.getElementByClassName(className);
        }
        else
        {
            document.getElementByClassName(className);
        }
    }

    if(!parentNode)
    {
        if(document.getElementsByClassName)
        {
            return document.getElementsByClassName(classname);
        }
        else
        {
            parentNode = document.getElementsByTagName("body")[0];
        }
    }
    else
    {
        parentNode = JUGetElement(parentNode);
    }

    var elements_to_return = [];
    var regexp = new RegExp('\\b' + classname + '\\b');
    var elements = parentNode.getElementsByTagName("*");

    for(var currentElement=0; currentElement < elements.length; currentElement++)
    {
        element = elements[currentElement];
        if(regexp.test(element.className))
        {
            elements_to_return.push(element);
        }
    }

    return elements_to_return;
}

//populates a form using an id/name:value dictionary -- such as a request dictionary.
function JUPopulate(fieldDict)
{
    for(fieldId in fieldDict)
    {
        field = JUGetElement(fieldId);
        value = fieldDict[fieldId];
        if(field && value)
        {
            field.value = value;
        }
    }
}

//updates a countdown label slowly deincrementing till reaches 0 than calls action
function JUCountDown(label, seconds, action)
{
    var label = JUGetElement(label);
    label.innerHTML = seconds;
    label.timeoutList = []

    for(var currentCount = 1; currentCount < seconds; currentCount++)
    {
        timeout = setTimeout('JUGetElement(\'' + label.id + '\').innerHTML = ' +
                  (seconds - currentCount) + ';', (currentCount * 1000));
        label.timeoutList.push(timeout);
    }

    timeout = setTimeout('JUGetElement(\'' + label.id + '\').innerHTML = 0;' +
                         action, seconds * 1000);
    label.timeoutList.push(timeout);
}

//updates a countdown label slowly deincrementing till reaches 0 than calls action
function JUAbortCountDown(label)
{
    var label = JUGetElement(label);
    var timeoutList = label.timeoutList

    for(var currentTimeout = 0; currentTimeout < timeoutList.length; currentTimeout++)
    {
        var timeout = timeoutList[currentTimeout];
        clearTimeout(timeout);
    }
}

//Returns the number of pixels left of element
function JUPixelsToLeft(element)
{
    var aTag = JUGetElement(element);

    var pixelsToLeft = 0;
    do
    {
        pixelsToLeft += aTag.offsetLeft;
        aTag = aTag.offsetParent;
    } while(aTag && aTag.tagName!="BODY");

    return pixelsToLeft;
}

//Returns the number of pixels above an element
function JUPixelsAbove(element)
{
    var aTag = JUGetElement(element);

    var pixelsAbove = 0;
    do
    {
        pixelsAbove += aTag.offsetTop;
        if(aTag.scrollTop){
            pixelsAbove -= aTag.scrollTop;
        }
        aTag = aTag.offsetParent;
    } while(aTag && aTag.tagName!="BODY");
    var aTag = element.parentNode;
    do
    {
        if(aTag.scrollTop)
        {
            pixelsAbove -= aTag.scrollTop;
        }
        aTag = aTag.parentNode;
    } while(aTag && aTag.tagName!="BODY");

    var aTag = element.parentNode;
    do
    {
        if(aTag.scrollTop)
        {
            pixelsAbove -= aTag.scrollTop;
        }
        aTag = aTag.parentNode;
    } while(aTag && aTag.tagName!="BODY");

    return pixelsAbove;
}

//Sets an element position to that of its parents + pixelsDown & pixelsToRight
function JUSetAbsoluteRelativeToParent(element, pixelsDown, pixelsToRight, parentElement)
{
    var element = JUGetElement(element);
    if(parentElement == null)
    {
        parentElement = element.parentNode;
    }
    else
    {
        parentElement = JUGetElement(parentElement);
    }
    if(pixelsDown == null)
    {
        pixelsDown = 0;
    }
    if(pixelsToRight == null)
    {
        pixelsToRight = 0;
    }

    element.style.left = JUPixelsToLeft(parentElement) + pixelsToRight;
    element.style.top = JUPixelsAbove(parentElement) + pixelsDown;
}

//Sets an element position to that of its parents + pixelsDown & pixelsToRight
function JUDisplayDropDown(dropDown, parentElement)
{
    var dropDownElement = JUGetElement(dropDown);
    if(parentElement == null)
    {
        parentElement = dropDownElement.parentNode;
    }
    else
    {
        parentElement = JUGetElement(parentElement);
    }

    JUSetAbsoluteRelativeToParent(dropDownElement, parentElement.offsetHeight -1,
                                  0, parentElement);
    JUShowElement(dropDownElement);
}

function JUToggleDropDown(dropDown, parentElement)
{
    if(JUElementShown(dropDown))
    {
        JUHideElement(dropDown);
        return false;
    }
    else
    {
        JUDisplayDropDown(dropDown, parentElement);
        return true;
    }
}

//Gets the first element in parent node with a certain class name
function JUGetElementByClassName(classname, parentNode)
{
    var elements = JUGetElementsByClassName(classname, parentNode);
    if(elements.length > 0)
    {
        return elements[0];
    }
    else
    {
        return null;
    }
}


function JUFellowChild(element, parentClass, childClass)
{
    return JUGetElementByClassName(childClass, JUParentElement(element, parentClass));
}

//Get first child element (exluding empty elements)
function JUFirstChildElement(element)
{
    var element = JUGetElement(element);
    if(element.firstChild)
    {
        element = element.firstChild
    }
    while ((!element || element.innerHTML == null) && element.nextSibling)
    {
        element = element.nextSibling;
    }
    return element;
}

//Get first child element (exluding empty elements)
function JULastChildElement(element)
{
    var element = JUGetElement(element);
    if(element.lastChild)
    {
        element = element.lastChild
    }
    while ((!element || element.innerHTML == null) && element.prevSibling)
    {
        element = element.prevSibling;
    }
    return element;
}


//Same as element.nextSibling except it is called
//as JUNextElement(object) and ignores blank elements
function JUNextElement(element)
{
    if(element.nextSibling)
    {
        element = element.nextSibling;
    }
    while ((!element || element.innerHTML == null) && element.nextSibling)
    {
        element = element.nextSibling;
    }
    return element;
}

//increments the value of a hiddenField
function JUIncrement(element, max)
{
    var element = JUGetElement(element);
    var number = parseInt(element.value)
    if(!number){
        number = 0;
    }
    number += 1;
    if(max != undefined && number > max){
        number = max;
    }
    element.value = number;
    if(element.onchange)
    {
        element.onchange();
    }
}

//deincrements the value of a hiddenField
function JUDeincrement(element, min)
{
    var element = JUGetElement(element);
    var number = parseInt(element.value)
    if(!number){
        number = 0;
    }
    number -= 1;
    if(min != undefined && number < min){
        number = min;
    }
    element.value = number;
    element.onchange();
}

//Sets the prefix for the container and all childElements
function JUSetPrefix(container, prefix)
{
    var container = JUGetElement(container);
    container.id = prefix + container.id;
    container.name = prefix + container.name;

    var children = JUChildElements(container);
    for(currentChild = 0; currentChild != children.length; currentChild++)
    {
        var child = children[currentChild];
        child.id = prefix + child.id;
        child.name = prefix + child.name;
    }

}

//Same as element.previousSibling except it is called
//as JUPrevElement(object) and ignores blank elements
function JUPrevElement(element)
{
    if(element.previousSibling)
    {
        element = element.previousSibling;
    }
    while ((!element || element.innerHTML == null) && element.previousSibling)
    {
        element = element.previousSibling;
    }
    return element;
}

//Same as element.parentNode except it is called as
//JUParentElement(object) and ignores blank elements
function JUParentElement(element, className, giveUpAtClass)
{
    var element = JUGetElement(element);
    var regexp = new RegExp('\\b' + className + '\\b');
    var regexpCancel = false;
    if(giveUpAtClass)
    {
        regexpCancel = new RegExp('\\b' + giveUpAtClass + '\\b');
    }

    if(element.parentNode)
    {
        element = element.parentNode;
    }
    while ((!element || element.innerHTML == null || !regexp.test(element.className))
           && element.parentNode)
    {
        element = element.parentNode;
        if(regexpCancel && regexpCancel.test(element.className)){
            return false;
        }
    }
    return element;
}


//Removes all children
function JUClearChildren(element, replacement)
{
    var childElements = JUChildElements(element);
    if(childElements)
    {
        for(var currentChild = 0; currentChild < childElements.length; currentChild++)
        {
            JURemoveElement(childElements[currentChild]);
        }
    }
    if(replacement)
    {
        element.appendChild(replacement)
    }
}

//Allows you to get a childElement by class name
function JUChildElement(element, className)
{
    var element = JUGetElement(element);
    return JUGetElementByClassName(className, element);
}

//Allows you to get childElements by class name if provided or simply returns all child elements
function JUChildElements(parentElement, className)
{
    var parentElement = JUGetElement(parentElement);
    if(className != null)
    {
        return JUGetElementsByClassName(className, parentElement);
    }

    var childElements = parentElement.getElementsByTagName('*');
    var returnedChildren = Array();
    for(var currentChild = 0; currentChild != childElements.length; currentChild++)
    {
        var child = childElements[currentChild];
        if(child && child.innerHTML != null)
        {
            returnedChildren.push(child);
        }
    }

    return returnedChildren;
}



//Allows you to get an element in the same location on the tree based on a classname
function JUPeer(element, className)
{
    var parentElement = JUGetElement(element).parentNode
    return JUChildElement(parentElement, className);
}

//Forces this to be the only peer with class
function JUStealClassFromPeer(element, className)
{
    var peer = JUPeer(element, className);
    if(peer)
    {
        JURemoveClass(peer, className);
    }
    JUAddClass(element, className);
}

//Forces this to be the only peer with class
function JUStealClassFromFellowChild(element, parentClassName, className)
{
    var fellowChild = JUFellowChild(element, parentClassName, className);
    if(fellowChild)
    {
        JURemoveClass(fellowChild, className);
    }
    JUAddClass(element, className);
}

//hides an element by setting its display property to none
function JUHideElement(element)
{
    var element = JUGetElement(element);
    if(element != null)
    {
        element.style.display = "none";
        return true;
    }
    return false;
}

//shows an element by setting its display property to block
function JUShowElement(element)
{
    var element = JUGetElement(element);
    if(element != null)
    {
        var tagName = element.tagName.toLowerCase();
        if(tagName == "span")
        {
            element.style.display = "inline";
        }
        else if(tagName == "tr")
        {
            element.style.display = "";
        }
        else
        {
            element.style.display = "block";
        }
        return true;
    }
    return false;
}

//shows the element if it is hidden - hides it if it is visable
function JUToggleElement(element)
{
    if(JUElementShown(element))
    {
        JUHideElement(element);
        return true;
    }
    JUShowElement(element);
    return false;
}

//return if the element is visable or not
function JUElementShown(element)
{
    var element = JUGetElement(element);
    if(element.style.display == "none")
    {
        return false;
    }
    return true;
}

//replaces 'element' with 'newElement' (element must contain a parent element)
function JUReplaceElement(element, newElement)
{
   var element = JUGetElement(element);
   var elementParent = element.parentNode;
   if(!elementParent)
   {
       return false;
   }

   var newElement = JUGetElement(newElement);
   elementParent.replaceChild(newElement, element);
   return true;
}

//removes 'element' from the page (element must contain a parent element)
function JURemoveElement(element)
{
    var element = JUGetElement(element);
    var elementParent = element.parentNode;
    if(!elementParent)
    {
        return false;
    }

    elementParent.removeChild(element);
    return true;
}

//clears the innerHTML of an element
function JUClear(element)
{
    var element = JUGetElement(element);
    element.innerHTML = "";
}

//adds an option to a selectbox with a specified name and value
function JUAddOption(selectElement, optionName, optionValue)
{
    var selectElement = JUGetElement(selectElement);
    if(optionValue == undefined){
        optionValue = optionName;
    }
    newOption = document.createElement('option');
    newOption.innerHTML = optionName;
    newOption.value = optionValue;
    selectElement.appendChild(newOption);
}

//adds html to element
function JUAddHtml(element, html)
{
    var element = JUGetElement(element);
    var newDiv = document.createElement('div');
    newDiv.innerHTML = html;
    element.appendChild(newDiv);
    return newDiv
}

//moves a div
function JUMove(element, to)
{
    var element = JUGetElement(element);
    var to = JUGetElement(to);
    to.appendChild(element);
}

//makes a copy of an element into 'to' incrementing its id and returns the copy
function JUCopy(element, to, incrementId)
{
    if(incrementId == null){incrementId = true;}

    var element = JUGetElement(element);
    var to = JUGetElement(to);

    var elementCopy = element.cloneNode(true);
    var toReplace = elementCopy.id
    if(toReplace && incrementId)
    {
        for(currentChar = toReplace.length - 1; currentChar >= 0; currentChar--)
        {
            var character = toReplace[currentChar];
            if(isNaN(character))
            {
                break;
            }
        }
        var splitAt = currentChar + 1
        var increment = (toReplace.substring(splitAt, toReplace.length) * 1) + 1
        var replacement = toReplace.substring(0, splitAt) + increment
        elementCopy.id = replacement

        var html = elementCopy.innerHTML

    }
    to.appendChild(elementCopy);

    if(incrementId)
    {
        elementCopy.innerHTML = JUReplaceAll(html, toReplace, replacement);
    }

    return elementCopy
}

//returns true if text JUContains subtext false if not
function JUContains(text, subtext, caseSensitive)
{
    if(!caseSensitive)
    {
        var text = text.toLowerCase();
        var subtext = subtext.toLowerCase();
    }

    if(text.indexOf(subtext) == -1)
    {
        return false;
    }
    return true;
}

//returns true if any words within text start with subtext
function JUStartsWith(text, subtext, caseSensitive)
{
    if(!caseSensitive)
    {
        var text = text.toLowerCase();
        var subtext = subtext.toLowerCase();
    }

    var text = JUReplaceAll(text, ">", " ");
    text = JUReplaceAll(text, "<", " ");
    text = JUReplaceAll(text, ",", " ");
    text = JUReplaceAll(text, "|", " ");
    text = text.split(" ")

    for(currentWord = 0; currentWord < text.length; currentWord++)
    {
        var word = text[currentWord]
        if(word.indexOf(subtext) == 0)
        {
            return true;
        }
    }

    return false;
}

//Adds a prefix to all child elements
function JUAddPrefix(container, prefix)
{
    if(!caseSensitive)
    {
        var text = text.toLowerCase();
        var subtext = subtext.toLowerCase();
    }

    if(text.indexOf(subtext) == -1)
    {
        return false;
    }
    return true;
}


//perform the javascript contained on the page --
//contained in elements innerHTML where the
//class is set to 'onLoadJavascript'
//made for use on AJAX pages -- inflicts a noticable performance penalty over <script>
function JUDoInPageJavascript(container)
{
    var container = JUGetElement(container);
    var elements = JUGetElementsByClassName("onLoadJavascript", container);
    for(currentElement = 0; currentElement < elements.length; currentElement++)
    {
        var element = elements[currentElement]
        if(element.innerHTML != null && element.innerHTML != "")
        {
            scriptTag = document.createElement('script');
            scriptTag.type = "text/javascript"
            container.appendChild(scriptTag)

            scriptText = element.innerHTML;
            scriptText = JUReplaceAll(scriptText, "&lt;", "<");
            scriptText = JUReplaceAll(scriptText, "&gt;", ">");
            scriptText = JUReplaceAll(scriptText, "&amp;", "&");

            scriptTag.text = scriptText
        }
    }
}

//sorts a list alphabetically
function JUSortSelect(selectElement)
{
    var selectElement = JUGetElement(selectElement);
    var selectOptions = selectElement.options;
    var sorted = new Array();
    var selectElementSorted = new Array();

    for(var currentOption = 0; currentOption < selectOptions.length; currentOption++)
    {
        var option = selectOptions[currentOption];
        sorted[currentOption] = new Array();
        sorted[currentOption][0] = option.innerHTML;
        sorted[currentOption][1] = option.value;
        sorted[currentOption][2] = option.id;
    }

    sorted.sort();

    for(var currentOption=0; currentOption < sorted.length; currentOption++)
    {
        selectElement.options[currentOption].innerHTML=sorted[currentOption][0];
        selectElement.options[currentOption].value=sorted[currentOption][1];
        selectElement.options[currentOption].id = sorted[currentOption][2];

    }


}

//returns a list without duplicate elements
function JURemoveDuplicates(inArray)
{
    var result = {};

    for(var i = 0; i < inArray.length; i++)
    {
      result[inArray[i]] = true;
    }

    var outArray = new Array();
    for(var dictKey in result)
    {
        outArray.push(dictKey)
    }

    return outArray;
}

//returns the selected options within a select box
function JUSelectedOptions(selectBox)
{
    var selectBox = JUGetElement(selectBox);
    var options = selectBox.options;

    var selectedOptions = Array();
    for(currentOption = 0; currentOption < options.length; currentOption++)
    {
        var option = options[currentOption];
        if (option.selected)
        {
            selectedOptions.push(option)
        }
    }
    return selectedOptions
}

//returns the selected options within a select box
function JUSelectAllOptions(selectBox)
{
    var selectBox = JUGetElement(selectBox);
    var options = selectBox.options;

    var selectedOptions = Array();
    for(currentOption = 0; currentOption < options.length; currentOption++)
    {
        var option = options[currentOption];
        option.selected = true;
    }
}

//returns the selected checkboxes withing a container
function JUSelectedCheckboxes(container)
{
    var container = JUGetElement(container);
    var elements = JUChildElements(container);

    var selectedCheckboxes = Array();
    for(currentElement = 0; currentElement < elements.length; currentElement++)
    {
        var element = elements[currentElement];
        if (element.checked)
        {
            selectedCheckboxes.push(element.name)
        }
    }
    return selectedCheckboxes
}

function JUSelectAllCheckboxes(container, check)
{
    if(check == null){var check = true;}

    var children = JUChildElements(container);
    for(current = 0; current < children.length; current++)
    {
        var child = children[current];
        if(child.type == 'checkbox')
        {
            child.checked = check;
        }
    }
}

//returns all nested values within a contianer
function JUGetValues(container, checkSelected)
{
    if(checkSelected == null){var checkSelected = false;}

    var container = JUGetElement(container);
    var optionElements = container.getElementsByTagName("option");

    var values = Array();
    for(currentOption = 0; currentOption < optionElements.length; currentOption++)
    {
        option = optionElements[currentOption];
        if (!checkSelected || option.selected)
        {
            values.push(option.value)
        }
    }
    return values
}

//Get a child element of element based on value
function JUGetElementByValue(element, value)
{
    var element = JUGetElement(element);

    var children = JUChildElements(element);
    for(current = 0; current < children.length; current++)
    {
        var child = children[current];
        if(child.value == value)
        {
            return child;
        }
    }

    return false;
}

//returns the first selected option within a select box
function JUSelectedOption(selectBox)
{
    var selectBox = JUGetElement(selectBox);
    var options = selectBox.options;

    for(currentOption = 0; currentOption < options.length; currentOption++)
    {
        var option = options[currentOption];
        if (option.selected)
        {
            return option;
        }
    }

    return null
}

//selects an element based on its value
function JUSelectOption(selectBox, option)
{
    JUSelectedOption(selectBox).selected = false;
    JUGetElementByValue(selectBox, option).selected = true;
}

//replaces all instances of a string with another string
function JUReplaceAll(string, toReplace, replacement)
{
    return string.split(toReplace).join(replacement);
}

//returns all css classes attached to an element as a list
function JUClasses(element)
{
    var element = JUGetElement(element);
    var classes = element.className;
    return classes.split(" ");
}

//returns true if element contains class
function JUHasClass(element, className)
{
    var element = JUGetElement(element)
    var regexp = new RegExp('\\b' + className + '\\b');
    if(regexp.test(element.className))
    {
        return true;
    }
    return false;
}

//sets an elements classes based on the passed in list
function JUSetClasses(element, classList)
{
    var element = JUGetElement(element);
    element.className = classList.join(" ");
}

//removes a css class
function JURemoveClass(element, classToRemove)
{
    JUSetClasses(element, JUClasses(element).without(classToRemove))
}

//adds a css class
function JUAddClass(element, classToAdd)
{
    var element = JUGetElement(element);
    var styleClasses = JUClasses(element);

    for(currentClass = 0; currentClass < styleClasses.length; currentClass++)
    {
        var styleClass = styleClasses[currentClass];
        if(styleClass == classToAdd)
        {
            return;
        }
    }

    element.className += " " + classToAdd;
}

//lets you choose one class out of a list of class choices
function JUChooseClass(element, classes, choice)
{
    var element = JUGetElement(element);
    var styleClasses = JUClasses(element);
    for(currentClass = 0; currentClass < classes.length; currentClass++){
        styleClasses = styleClasses.without(classes[currentClass]);
    }
    styleClasses.push(choice);
    JUSetClasses(element, styleClasses);
}

//forces the browser to redraw the element (Needs to exist becuase IE is Evil)
function JURedraw(element)
{
    var element = JUGetElement(element);
    var parentElement = element.parentNode;
    var html = parentElement.innerHTML;

    parentElement.innerHTML = "";
    parentElement.innerHTML = html;
}

//Simple way to access data within div section
function JUAttribute(element, attribute)
{
    element = JUGetElementByClassName(attribute + "Value", element)
    if(element == null)
    {
        return "";
    }

    if(element.nodeName.toLowerCase() == "input")
    {
        return element.value;
    }
    else
    {
        return JUStrip(element.innerHTML);
    }
}

//Simple way to set an attribute in a div section
function JUSetAttribute(element, attribute, value)
{
    element = JUChildElement(element, attribute + "Value")
    if(element == null)
    {
        return false;
    }

    if(element.nodeName.toLowerCase() == "input")
    {
        element.value = value;
        if(element.onchange)
        {
            element.onchange()
        }
    }
    else
    {
        element.innerHTML = value;
    }
    return true;
}


//Simple way to export variables within a div
function JUExport(element, delimiter, max)
{
    if(delimiter == null)
    {
        delimiter = ","
    }

    var exportedValue = [];
    var values = JUGetElementsByClassName("Value", element);
    for(currentValue = 0; currentValue < values.length; currentValue++)
    {
        element = values[currentValue];
        if(max == currentValue)
        {
            break;
        }
        if(element.nodeName.toLowerCase() == "input")
        {
            exportedValue.push(JUStrip(element.value));
        }
        else
        {
            exportedValue.push(JUStrip(element.innerHTML));
        }
    }
    return exportedValue.join(delimiter);
}

//Strip spaces before and after string
function JUStrip(string)
{
    return string.replace(/^\s+|\s+$/g,"");
}

//Easy way to see if a value is contained in a list
function JUInList(list, value)
{
    for(var current = 0; current < list.length; current++)
    {
        if(list[current] == value)
        {
            return true;
        }
    }
    return false;
}

//Appens to a list only if the value is not already contained in the list
function JUAppendOnce(list, listItem)
{
    if(!JUInList(list, listItem))
    {
        list.push(listItem)
    }
}

//Combines two lists into one ignoring duplicate values
function JUCombine(list, list2)
{
    for(var currentListItem = 0; currentListItem < list2.length; currentListItem++)
    {
        listItem = list2[currentListItem];
        JUAppendOnce(list, listItem);
    }
}

//suppress a single nodes onclick event
function JUSuppress(element, attribute)
{
    var element = JUGetElement(element);

    element['suppressed_' + attribute] = element[attribute];
    element[attribute] = null;
}

//unsuppress the supressed javascript event
function JUUnsuppress(element, attribute)
{
    var element = JUGetElement(element);

    element[attribute] = element['suppressed_' + attribute];
    element['suppressed_' + attribute] = element[attribute];
}

function JUToggleMenu(button)
{
    var menu = JUPeer(button, 'WEMenu');
    try{ x = currentDropDown; }
    catch(e){ window.currentDropDown = null; }
    if(currentDropDown != menu){
    JUHideElement(currentDropDown);
    }
    currentDropDown = menu;
    JUToggleDropDown(currentDropDown);
}

function JUCloseMenu()
{
    try{ x = closeCurrentDropDown; }
    catch(e){ window.currentDropDown = null; }
    JUHideElement(currentDropDown);
}

function JUSelectText(element, start, end)
{
    var element = JUGetElement(element);
    if(element.setSelectionRange){
        element.setSelectionRange(parseInt(start), parseInt(end));
    }
    else if (element.createTextRange){
        var range = element.createTextRange();
        range.collapse(true);
        range.moveStart('character', parseInt(start));
        range.moveEnd('character', parseInt(end - start));
        range.select();
    }
}

