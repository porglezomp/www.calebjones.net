---
title: Debugging in the Deep End
date: 2018-04-17
tags: code
slug: debugging-in-the-deep-end
author: C Jones
summary: I discuss the approach I used to fix a bug in VCV Rack despite having never looked at the codebase before.
status: published
---

# The Problem

Last week I was working with [Aaron][] on a series of [VCV Rack plugin modules][VCVMicroTools], and we were trying to add our own custom graphics for them.
VCV Rack uses SVG for its plugins, so Aaron had built a front face for one of our modules, but it wasn't properly aligned.
I imported it into Affinity Designer and tried to fix it up, but when I exported my new version and loaded it, suddenly all of our modules had vanished.
Since our module wasn't *supposed* to vanish, and I hadn't done anything *obviously* wrong, I decided that this must be a bug in VCV Rack.
Over the next few hours, I diagnosed and managed to fix this bug, and by the magic of open source and some luck, the PRs got merged the next day.
In particular, I managed to make this fix without having ever looked at any of this code before, and I'd like to share the process I followed to manage to do this.

[Aaron]: http://twitter.com/a2aarontothe2
[VCVMicroTools]: https://github.com/a2aaron/VCVMicroTools
<!-- Use these links? -->
[VCV Issue]: https://github.com/VCVRack/Rack/issues/917
[nanosvg PR]: https://github.com/memononen/nanosvg/pull/116

# Debugging the SVG

The first phase when fixing a bug is to reproduce the bug.
Here, because the rendering worked fine with Aaron's SVG until I re-exported it, I suspected that some feature being used in Affinity's SVG export wasn't supported by the VCV Rack SVG renderer.
To figure out which, I used the first technique: minimize your failing case.

First, I tried changing export settings, removing groups to flatten the SVG, doing everything I could to remove different features.
As I went, I inspected the working and not working SVG side-by-side to see what the differences were.
I didn't make much progress this way, so I started from the other direction, building up instead of tearing down.
I saved a simple blank grey square, just a single element.
When that didn't work, I figured it must have something to do with one of the attributes on the `<svg>` container element.
For reference, a minimal SVG exported from Affinity might look something like:

```svg
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
          "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%" height="100%" viewBox="0 0 240 380" version="1.1"
     xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     xml:space="preserve" xmlns:serif="http://www.serif.com/"
     style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round;
            stroke-miterlimit:1.41421;">
     <rect x="0" y="0" width="240" height="380" style="fill:rgb(235,235,235);"/>
</svg>
```

So I looked through all the settings on that, I noticed that it was setting the width and height to `100%`, whereas the working one was setting it to explicit pixel numbers.
I copied the width and height out of the working one into the not-working one… and that fixed it.
That suggested a possible problem: If you used percentage dimensions on the `<svg>` element, it wouldn't correctly calculate the size of the object, and would simply make it 0 by 0.
This was a good enough guess for me, so I set about trying to figure out how to fix that.

# Spelunking the Code

This brings us to the second phase of solving the bug: find a piece of code that's related to the bug, so you have a place to start.
I suspected that I could find where the SVGs were loaded in VCV Rack and fix it to handle those percentages correctly.
I didn't know exactly how I would handle them yet, I had to see what it was doing first.
To find this, I took a simple approach: search the source code for the word "SVG" and see what I could find!
I used [ripgrep][], a very good search tool, but you can use whatever tool you have available as long as it can search all the code at once.
If your editor can jump to definitions in a project, searching for related words and then jumping from definition to definition can help you find the part of the code you're interested in very quickly; having good code navigation tools helps *a lot*.

[ripgrep]: https://github.com/BurntSushi/ripgrep

Using this, I found SVG widgets, followed their class hierarchy up to rendering components, and then eventually I found my way to a class calling functions from "nanosvg."
Curious, I looked it up, and saw that it was a small SVG parser library, and that it produces a bunch of shape paths.
In order to not have to resize all those paths (I assumed), I decided to try fixing the bug from inside nanosvg instead of inside VCV Rack.
Knowing that it was a problem with dimensions, I searched the nanosvg code for the string `"width"`.
The second result was a very promising looking function:

```c hl_lines="6 7 8 9"
static void nsvg__parseSVG(NSVGparser* p, const char** attr)
{
	int i;
	for (i = 0; attr[i]; i += 2) {
		if (!nsvg__parseAttr(p, attr[i], attr[i + 1])) {
			if (strcmp(attr[i], "width") == 0) {
				p->image->width = nsvg__parseCoordinate(p, attr[i + 1], 0.0f, 0.0f);
			} else if (strcmp(attr[i], "height") == 0) {
				p->image->height = nsvg__parseCoordinate(p, attr[i + 1], 0.0f, 0.0f);
// …
```

# Writing a Fix

I'd located a likely location for the bug, so now I changed mode from code spelunking to trying to understand what the code did.
Since this function looked so relevant, I first tried to figure out what `nsvg__parseSVG` was doing.
A good tool for this was finding where it was used: it was getting called in one place, from `nsvg__startElement`, and seemed to be being called when an `<svg>` tag was found, to compute the context from the attributes… perfect.
The parameter `const char** attr` suggested a list of attribute strings, and the usage `attr[i]` and `attr[i + 1]` suggested the SVG key/value pairs.
Therefore, it seemed like

```c
if (strcmp(attr[i], "width") == 0)
    p->image->width = nsvg__parseCoordinate(p, attr[i + 1], 0.0f, 1.0f);
```

would parse the width coordinate value.
In order to figure this out, we want to go look at `nsvg__parseCoordinate`.

```c
static float nsvg__parseCoordinate(NSVGparser* p, const char* str,
                                   float orig, float length)
{
    NSVGcoordinate coord = nsvg__parseCoordinateRaw(str);
    return nsvg__convertToPixels(p, coord, orig, length);
}
```

Following those definitions, `nsvg__parseCoordinateRaw` follows a few steps to get to unit parsing, but it seems largely straightforward parsing of the data, no fancy processing.
The fact that we've got an issue in % suggests that `nsvg__convertToPixels` is doing something interesting.
And indeed, looking at the code for that function, it made clear what the `length` argument did:

```c hl_lines="7"
static float nsvg__convertToPixels(NSVGparser* p, NSVGcoordinate c,
                                   float orig, float length)
{
    NSVGattrib* attr = nsvg__getAttr(p);
    switch (c.units) {
        // …
        case NSVG_UNITS_PERCENT:    return orig + c.value / 100.0f * length;
        default:                    return c.value;
    }
    return c.value;
}
```

It was used as the base value that the percentage should be relative to.
Then, it becomes clear: `nsvg__parseCoordinate(p, attr[i + 1], 0.0f, 1.0f);` makes `100%` into `1px`
So, now we know what exactly has gone wrong, how do we solve it?
Since I didn't know what the percentages should be relative to, I started researching, looking at Mozilla references for how the percent should behave.

I didn't find an answer, but while I was researching, I ran into lots of examples that didn't specify dimensions at all.
This made me suspicious: nanosvg handles most SVGs correctly, so it must have some code to handle this case.
When you're fixing a bug, often the edge case that you're running into is similar to another edge case that's already handled, and you just need to make it cover your case as well.
Since this must be related to the dimensions, and the dimension handling sets the `width` field while parsing the `<svg>` element, I went out searching for `->width` and `.width` in the code.
I immediately found `nsvg__scaleToViewbox` which contains a promising looking block of code:

```c hl_lines="1"
if (p->viewWidth == 0) {
    if (p->image->width > 0) {
        p->viewWidth = p->image->width;
    } else {
        p->viewMinx = bounds[0];
        p->viewWidth = bounds[2] - bounds[0];
    }
}
```

This looks like what we want!
It will recalculate the width and height if they're set to 0, so we just need to make sure that our 100% sets it to 0 instead of 1.
And to fix that, we can simply change:

```diff
 if (strcmp(attr[i], "width") == 0) {
-    p->image->width = nsvg__parseCoordinate(p, attr[i + 1], 0.0f, 1.0f);
+    p->image->width = nsvg__parseCoordinate(p, attr[i + 1], 0.0f, 0.0f);
 } else if (strcmp(attr[i], "height") == 0) {
-    p->image->height = nsvg__parseCoordinate(p, attr[i + 1], 0.0f, 1.0f);
+    p->image->height = nsvg__parseCoordinate(p, attr[i + 1], 0.0f, 0.0f);
 } else if (strcmp(attr[i], "viewBox") == 0) {
```

And that's the whole fix!

# Conclusions

You can use these techniques the next time you have to jump into a large codebase that's unfamiliar.
Finding a simple case that fails, making a hypothesis about why it fails, and then searching for terms related to that gives you a big head-start navigating the code.
Being able to jump to definitions helps you build a mental map of a thin slice of the code.
Even though Rack is about 11K lines of code, and nanosvg is almost 3K, in the process of fixing this bug I only *glanced at* a few hundred lines of code, and only tried to understand a few dozen of them.
The next time you want to try to examine a new codebase, keep these tricks in mind.
