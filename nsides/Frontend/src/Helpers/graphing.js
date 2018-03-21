import * as d3 from 'd3';
// let data1;
// let dateformat = "%Y";
// let blank;
// Initialize plot
// drawTimeSeriesGraph([], [], "Select a drug and effect", "", dateformat, blank = true);
/* 
Tooltip from: http://bl.ocks.org/d3noob/6eb506b129f585ce5c8a
*/
//function drawTimeSeriesGraph(data,title,dateformat) {
const drawTimeSeriesGraph = (data, data2, title, title2, dateformat, blank = false, modelType = 'DNN') => {
  console.log(
    'data', data, '\ndata2', data2, '\ntitle', title, 
    '\ntitle2', title2, '\ndateformat', dateformat, 
    '\nblank', blank, '\nmodelType', modelType);
  document.getElementById("viz_container").innerHTML = "";
  //Set bounds for red dots
  // var lbound = 0.045,
  //   ubound = 0.075;\
  // Set the dimensions of the canvas / graph
  var margin = { top: 50, right: 150, bottom: 50, left: 50 },
    width = 800 - margin.left - margin.right,
    height = 270 - margin.top - margin.bottom;
  // Parse the date / time
  var parseDate = d3.timeParse(dateformat), // converts year to date    Tue Jan 01 2013 00:00:00 GMT-0500 (EST)
      formatDate = d3.timeFormat(dateformat), // 
      bisectDate = d3.bisector(function (d) { return d.year; }).left;
  // Set the ranges
  var x = d3.scaleTime().range([0, width]); // scale from 0 - 600. How does this scale work? each x unit is 50 margin apart
  var y = d3.scaleLinear().range([height, 0]); // scale from 140 - 0. 170 low, 0 high.
  // y2 is used for nreports y axis
  var y2 = d3.scaleLinear().range([height, 0]);
  var xAxis = d3.axisBottom()
    .scale(x)
    .ticks(d3.timeYear.every(1)) // display 1 year intervals
    .tickSizeInner(-height)
    .tickSizeOuter(0)
    .tickPadding(10);
  var yAxis = d3.axisLeft()
    .scale(y)
    .tickSizeInner(-width)
    .tickSizeOuter(0)
    .tickPadding(5);
  var yAxis2 = d3.axisLeft()
    .scale(y2)
    .tickSizeInner(-width)
    .tickSizeOuter(0)
    .tickPadding(5);
  // Define the line
  var prrline = d3.line()
    .x(function (d) { 
      // console.log('x', x(d.year)); 
      return x(d.year); 
    }) //increments by margin on the x axis
    .y(function (d) { 
      // console.log('y', y(d.prr)); 
      return y(d.prr); 
    }); //increments by margin on y axis 140 is low 40 is high on the graph
  var nreportsline = d3.line()
    .x(function (d) {
      // console.log('x', x(d.year)); 
      return x(d.year); 
    })
    .y(function (d) { 
      // console.log('y', y(d.prr));
      return y2(d.nreports); 
    });

  // Adds the svg canvas
  var svg = d3.select("#viz_container") // graph number 1
    .append("div")
    .classed("svg-container", true) //container class to make it responsive
    .append("svg")
    //responsive SVG needs these 2 attributes and no width and height attr
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", "0 0 700 270")
    .classed("svg-content-responsive", true)
    .append("g")
    .attr("transform",
    "translate(" + margin.left + "," + margin.top + ")");
      
  // Adds the second svg canvas
  var svg2 = d3.select("#viz_container") // graph number 2
    .append("div")
    .classed("svg-container", true)
    .append("svg")
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", "0 0 700 270")
    .classed("svg-content-responsive", true)
    .append("g")
    .attr("transform",
    "translate(" + margin.left + "," + margin.top + ")");

    // console.log(svg._groups[0][0], svg2._groups[0][0]);

  if (!blank) {
      // Get the data
    data.forEach(function (d) {
        d.year = parseDate(d.year);
        // console.log('after parseDate', d.year);
        d.prr = +d.prr;
        d.ci = +d.ci;
    });
    data2.forEach(function (d2) {
        d2.year = parseDate(d2.year);
        // console.log('after parseDate for d2', d2.year);
        d2.nreports = +d2.nreports;
    });
    // Scale the range of the data
    x.domain(d3.extent(data, function (d) { return d.year; }));
    y.domain([0, d3.max(data, function (d) { return d.prr; }) > 2 ? 0.5 + d3.max(data, function (d) { return d.prr; }) : 2.5]);
    y2.domain([0, d3.max(data2, function (d) { return d.nreports; }) > 5 ? 1.0 + d3.max(data2, function (d) { return d.nreports; }) : 5.5]);

    // Threshold line
    var prrThreshold = 2;
    svg.append("line")
        .attr("class", "divider")
        .attr("x1", x.range()[0])
        .attr("x2", x.range()[1])
        .attr("y1", y(prrThreshold))
        .attr("y2", y(prrThreshold));
    // Add the prrline path.
    var lineSvg = svg.append("g");
    var lineSvg2 = svg2.append("g");
    lineSvg.append("path")
        .attr("class", "line")
        .attr("d", prrline(data));
    lineSvg2.append("path")
        .attr("class", "line")
        .attr("d", nreportsline(data2));
    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);
    svg2.append("g")
        .attr("class", "y axis")
        .call(yAxis2);
    // Only show every other y-axis tick
    // From https://stackoverflow.com/a/38921326
    var ticks = d3.selectAll(".tick text");
    ticks.attr("class", function (d, i) {
        if (i % 2 != 0) d3.select(this).remove();
    });
    // Add the X Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
    svg2.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Y axis title
    var padding = 80;
    svg.append("text")
        .attr("class", "ylabel")
        .attr("text-anchor", "middle")  // this makes it easy to center the text as the transform is applied to the anchor
        .attr("transform", "translate(-" + (padding / 2) + "," + (height / 2) + ")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
        .attr("font-size", "13px")
        .text("PRR");
    svg2.append("text")
        .attr("class", "ylabel")
        .attr("text-anchor", "middle")  // this makes it easy to center the text as the transform is applied to the anchor
        .attr("transform", "translate(-" + (padding / 2) + "," + (height / 2) + ")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
        .attr("font-size", "13px")
        .text("Number of Reports");
    // Confidence area
    var confidenceArea = d3.area()
        .curve(d3.curveLinear)
        .x(function (d) { return x(d.year); })
        .y0(function (d) { return d.prr - d.ci >= 0 ? y(d.prr - d.ci) : y(0); })
        .y1(function (d) { return d.prr + d.ci <= y.domain()[1] ? y(d.prr + d.ci) : y(y.domain()[1]); });
    svg.append("path")
        .datum(data)
        .attr("class", "area confidence")
        //        .attr("fill", "red") //estimateOneColor,
        .attr("d", confidenceArea);


    var focus = svg.append("g")
        .style("display", "none");
    var focus2 = svg2.append("g")
        .style("display", "none");
    // append the x line
    focus.append("line")
        .attr("class", "x")
        .style("stroke", "black")
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0.5)
        .attr("y1", 0)
        .attr("y2", height);
    focus2.append("line")
        .attr("class", "x")
        .style("stroke", "black")
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0.5)
        .attr("y1", 0)
        .attr("y2", height);
    // append the y line
    focus.append("line")
        .attr("class", "y")
        .style("stroke", "black")
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0.5)
        .attr("x1", width)
        .attr("x2", width);
    focus2.append("line")
        .attr("class", "y")
        .style("stroke", "black")
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0.5)
        .attr("x1", width)
        .attr("x2", width);
    // append the circle at the intersection
    focus.append("circle")
        .attr("class", "y")
        .style("fill", "none")
        .style("stroke", "steelblue")
        .style("stroke-width", 1.5)
        .attr("r", 4);
    focus2.append("circle")
        .attr("class", "y")
        .style("fill", "none")
        .style("stroke", "steelblue")
        .style("stroke-width", 1.5)
        .attr("r", 4);
    // place the prr/nreports at the intersection
    focus.append("text")
        .attr("class", "y1")
        .style("stroke", "white")
        .style("stroke-width", "3.5px")
        .style("opacity", 0.8)
        .attr("dx", 8)
        .attr("dy", "-.3em");
    focus2.append("text")
        .attr("class", "y1")
        .style("stroke", "white")
        .style("stroke-width", "3.5px")
        .style("opacity", 0.8)
        .attr("dx", 8)
        .attr("dy", "-.3em");
    focus.append("text")
        .attr("class", "y2")
        .attr("dx", 8)
        .attr("dy", "-.3em");
    focus2.append("text")
        .attr("class", "y2")
        .attr("dx", 8)
        .attr("dy", "-.3em");
    // place the date at the intersection
    focus.append("text")
        .attr("class", "y3")
        .style("stroke", "white")
        .style("stroke-width", "3.5px")
        .style("opacity", 0.8)
        .attr("dx", 8)
        .attr("dy", "1em");
    focus2.append("text")
        .attr("class", "y3")
        .style("stroke", "white")
        .style("stroke-width", "3.5px")
        .style("opacity", 0.8)
        .attr("dx", 8)
        .attr("dy", "1em");
    focus.append("text")
        .attr("class", "y4")
        .attr("dx", 8)
        .attr("dy", "1em");
    focus2.append("text")
        .attr("class", "y4")
        .attr("dx", 8)
        .attr("dy", "1em");
    // append the rectangle to capture mouse
    svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .style("fill", "none")
        .style("pointer-events", "all")
        .on("mouseover", function () { focus.style("display", null); })
        .on("mouseout", function () { focus.style("display", "none"); })
        .on("mousemove", mousemove);
    svg2.append("rect")
        .attr("width", width)
        .attr("height", height)
        .style("fill", "none")
        .style("pointer-events", "all")
        .on("mouseover", function () { focus2.style("display", null); })
        .on("mouseout", function () { focus2.style("display", "none"); })
        .on("mousemove", mousemove2);
    console.log(focus, focus2, focus._groups[0][0]);
    function mousemove() {
      var x0 = x.invert(d3.mouse(this)[0]), // get the array of x,y coordinate then select x and invert it back into a date
        i = bisectDate(data, x0, 1),
        d0 = data[i - 1],
        d1 = data[i],
        d = x0 - d0.year > d1.year - x0 ? d1 : d0;
        console.log(x0, '\ni', i, '\nd0', d0, '\nd1', d1, '\nd', d, data);
      focus.select("circle.y")
        .attr("transform",
        "translate(" + x(d.year) + "," +
        y(d.prr) + ")");
      focus.select("text.y2")
        .attr("transform",
        "translate(" + x(d.year) + "," +
        y(d.prr) + ")")
        .attr("font-size", "12px")
        .text(d.prr.toFixed(2));
      focus.select("text.y4")
        .attr("transform",
        "translate(" + x(d.year) + "," +
        y(d.prr) + ")")
        .attr("font-size", "12px")
        .text(formatDate(d.year));
      focus.select(".x")
        .attr("transform",
        "translate(" + x(d.year) + "," +
        y(d.prr) + ")")
        .attr("y2", height - y(d.prr));
      focus.select(".y")
        .attr("transform",
        "translate(" + width * -1 + "," +
        y(d.prr) + ")")
        .attr("x2", width + width);
    };
    function mousemove2() {
      var x0 = x.invert(d3.mouse(this)[0]),
        i = bisectDate(data2, x0, 1),
        d0 = data2[i - 1],
        d1 = data2[i],
        d = x0 - d0.year > d1.year - x0 ? d1 : d0;
      focus2.select("circle.y")
        .attr("transform",
        "translate(" + x(d.year) + "," +
        y2(d.nreports) + ")");
      focus2.select("text.y2")
        .attr("transform",
        "translate(" + x(d.year) + "," +
        y2(d.nreports) + ")")
        .attr("font-size", "12px")
        .text(d.nreports);
      focus2.select("text.y4")
        .attr("transform",
        "translate(" + x(d.year) + "," +
        y2(d.nreports) + ")")
        .attr("font-size", "12px")
        .text(formatDate(d.year));
      focus2.select(".x")
        .attr("transform",
        "translate(" + x(d.year) + "," +
        y2(d.nreports) + ")")
        .attr("y2", height - y2(d.nreports));
      focus2.select(".y")
        .attr("transform",
        "translate(" + width * -1 + "," +
        y2(d.nreports) + ")")
        .attr("x2", width + width);
    };
    svg.append("text")
      .attr("x", width)
      .attr("y", 0 - (margin.top / 2) + 12)
      .attr("text-anchor", "end")
      .text("Model type: " + modelType);
  }

  svg.append("text")
    .attr("x", (width / 2))
    .attr("y", 0 - (margin.top / 2))
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text(title);
  svg2.append("text")
    .attr("x", (width / 2))
    .attr("y", 0 - (margin.top / 2))
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text(title2);
};

const all = {
  drawTimeSeriesGraph
};

export default all;
export { 
  drawTimeSeriesGraph 
};