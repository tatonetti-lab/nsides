import * as d3 from 'd3';
import c3 from 'c3';
import React from 'react';

const createXAxis = function (xScale, height) {
  // var ticks = d3.selectAll(".tick text");
  // ticks.attr("class", function (d, i) {
  //   if (i % 2 !== 0) {
  //     d3.select(this).remove()
  //   };
  // });

  return d3.axisBottom()
    .scale(xScale)
    // .ticks(d3.timeYear.every(1)) // display 1 year intervals
    .tickSizeInner(-height)
    .tickSizeOuter(0)
    .tickPadding(10);
};

const createYAxis = function (yScale, width) {
  return d3.axisLeft()
    .scale(yScale)
    .tickSizeInner(-width)
    .tickSizeOuter(0)
    .tickPadding(5);
};

const createGraphLine = function (x, y, graphType) {
  return d3.line()
  .x(function (d) {
    // console.log('x', x(d.year)); 
    return x(d.year); 
  })
  .y(function (d) { 
    // console.log('y', y(d.prr));
    return y(d[graphType]); 
  });
};

const createSvg = function (margin) {
  return d3.select("#viz_container") // graph number 1
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
};

const appendTextsToCanvas = function (svg, width, margin, title) {
  svg.append("text")
    .attr("x", (width / 2))
    .attr("y", 0 - (margin.top / 2))
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .text(title);
};

const appendModelTypeToCanvas = function (svg, width, margin, modelType) {
  svg.append("text")
    .attr("x", width)
    .attr("y", 0 - (margin.top / 2) + 12)
    .attr("text-anchor", "end")
    .text("Model type: " + modelType);
};

const modifyDataYearToDate = function (data, parseDate) {
  console.log('before', data);
  return data.map(d => {
    // console.log('before',d);
    d = Object.assign({}, d);
    d.year = parseDate(d.year);
    // console.log(d);
    d.prr = +d.prr;
    d.ci = +d.ci;
    return d;
  });
};

const modifyData2YearToDate = function (data2, parseDate) {
  // console.log('before', d2.year, d2.nreports);
  return data2.map(d2 => {
    d2 = Object.assign({}, d2);
    d2.year = parseDate(d2.year);
    d2.nreports = +d2.nreports;
    return d2;
  });
};

const getDataWithMaxPrr = function (data, parseDate) {
  let max = 0;
  let dataWithMaxPrr = data.reduce((dataWithMax, datum) => {
    console.log(datum);
    let currentMax = datum.estimates.reduce((item, max) => { //get the max prr from current datum
      let currentMaxPrr = item.prr;
      if (currentMaxPrr > max) {
        max = currentMaxPrr;
        return currentMaxPrr;
      }
      return max;
    }, datum.estimates[0].prr);

    if (currentMax > max) { //if greater then this is the new greatest datum;
      return datum;
    }
    return dataWithMax;
  }, data[0]);
    // console.log(svg._groups[0][0], svg2._groups[0][0]);
  // Scale the range of the data
  // domain determines the range of possible values, extent determines the minimum and maxium of a set 
  return modifyDataYearToDate(dataWithMaxPrr.estimates, parseDate)
};

const addThresholdLine = (svg, x, y) => {
  var prrThreshold = 2;
  svg.append("line")
    .attr("class", "divider")
    .attr("x1", x.range()[0])
    .attr("x2", x.range()[1])
    .attr("y1", y(prrThreshold))
    .attr("y2", y(prrThreshold));
}

const addPath = (svg, data, prrline, color) => {
  svg.append("path")
    .data(data)
    .attr("class", "line")
    .style("stroke", color)
    .attr("d", prrline);
}

const drawLineForEstimatesData = function ({ svg, data, model, parseDate, bisectDate, formatDate, margin, x, y, xAxis, yAxis, width, height, prrline}) {
  // Get the data (data should be the estimates array);
  // let prrline;
  // // data = modifyDataYearToDate(data, parseDate)
  //   // Define the line
  // prrline = createGraphLine(x, y, 'prr'); //createPrrLine(x, y);
  // y.domain([0, d3.max(data, function (d) { return d.prr; }) > 2 ? (0.5 + d3.max(data, function (d) { return d.prr; })) : 2.5]);

  // Threshold line

  // Add the Y Axis
  // if (model === 'lrc') {
  //   svg.append("g")
  //     .attr("class", "y axis")
  //     .call(yAxis);
  // }

  // Only show every other y-axis tick
  // From https://stackoverflow.com/a/38921326


  // Y axis title
  var padding = 80;
  svg.append("text")
    .attr("class", "ylabel")
    .attr("text-anchor", "middle")  // this makes it easy to center the text as the transform is applied to the anchor
    .attr("transform", "translate(-" + (padding / 2) + "," + (height / 2) + ")rotate(-90)")  // text is drawn off the screen top left, move down and out and rotate
    .attr("font-size", "13px")
    .text("PRR");

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
    .style("display", "none")
    .attr("class", "focus"); //  focus area when mouse moves
  // var focus2 = svg2.append("g").style("display", "none"); //  area

  // append the x line
  focus.append("line")
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

  // append the circle at the intersection
  focus.append("circle")
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

  focus.append("text")
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

  focus.append("text")
    .attr("class", "y4")
    .attr("dx", 8)
    .attr("dy", "1em");

  // append the rectangle to capture mouse
  function mousemove () {
    var x0 = x.invert(d3.mouse(this)[0]), // get the array of x,y coordinate then select x and invert it back into a date
    i = bisectDate(data, x0, 1),
    d0 = data[i - 1],
    d1 = data[i],
    d = x0 - d0.year > d1.year - x0 ? d1 : d0;
    // console.log(x0, '\ni', i, '\nd0', d0, '\nd1', d1, '\nd', d);
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
  }

  svg.append("rect")  //area of the graph
    .attr("width", width)
    .attr("height", height)
    .style("fill", "none")
    .style("pointer-events", "all")
    .on("mouseover", function () { 
      focus.style("display", null); 
    })
    .on("mouseout", function () { 
      focus.style("display", "none"); 
    })
    .on("mousemove", mousemove);
  // console.log(focus, focus2, focus._groups[0][0]);
  
  // appendModelTypeToCanvas(svg, width, margin, model);
}


const drawTimeSeriesGraph = function (data, data2, title, title2, dateformat, blank = false, modelType = 'DNN') {
  // console.log(
  //   'data', data, '\ndata2', data2, '\ntitle', title, 
  //   '\ntitle2', title2, '\ndateformat', dateformat, 
  //   '\nblank', blank, '\nmodelType', modelType
  // );
  // console.log(data);
  document.getElementById("viz_container").innerHTML = ""; // resets the viz_container
  data = data.slice();
  data2 = data2.slice();
  // Set the dimensions of the canvas / graph
  let margin = { top: 50, right: 150, bottom: 50, left: 50 },
    width = 800 - margin.left - margin.right,  // 600
    height = 270 - margin.top - margin.bottom,  // 170
  // Parse the date / time
    parseDate = d3.timeParse(dateformat), // converts year to date    Tue Jan 01 2013 00:00:00 GMT-0500 (EST)
    formatDate = d3.timeFormat(dateformat), // 
    bisectDate = d3.bisector(function (d) { return d.year; }).left, // Returns the insertion point for x in array to maintain sorted order. 
    // bisector.left(array, x[, lo[, hi]])     x is the x0 or potential input to array
  // Set the ranges

    // Define the line
    svg = createSvg(margin); // Adds the svg canvas;
    // yAxis2 = createYAxis(y2, width),

  if (!blank) {
    
    let dataWithMaxPrr = getDataWithMaxPrr(data, parseDate);
    let x, y, xAxis, yAxis, prrline, prrline2, prrline3;
    x = d3.scaleTime()
      .range([0, width]) // scale from 0 - 600. How does this scale work? each x unit is 50 margin apart
      .domain(d3.extent(dataWithMaxPrr, function (d) { return d.year; }));
    y = d3.scaleLinear()
      .range([height, 0]) // scale from 140 - 0. 170 low, 0 high.
      .domain([0, d3.max(dataWithMaxPrr, function (d) { return d.prr; }) > 2 ? (0.5 + d3.max(data, function (d) { return d.prr; })) : 2.5]);
    prrline = createGraphLine(x, y, 'prr'); //createPrrLine(x, y);
    prrline2 = createGraphLine(x, y, 'prr');
    prrline3 = createGraphLine(x, y, 'prr');

    xAxis = createXAxis(x, height);
    yAxis = createYAxis(y, width);
    console.log(y, 'prrthreshold', y(2));
    addThresholdLine(svg, x, y);
    // Add the prrline path.
    // var lineSvg = svg.append("g");
    // // var lineSvg2 = svg2.append("g");
    // lineSvg.append("path")
    //   .attr("class", "line")
    //   .attr("d", prrline(data));
    let iteraction = [
      {
        color: 'blue',
        prrline: prrline
      },
      {
        color: 'red',
        prrline: prrline2
      },
      {
        color: 'yellow',
        prrline: prrline3
      }
    ];

    data.forEach((datum, i) => {
      let modified = modifyDataYearToDate(datum.estimates, parseDate);
      let current = iteraction[i];
      let prrline = current.prrline;
      let color = current.color;
      addPath(svg, modified, prrline, color);
      // let input = Object.assign({}, parameters);
      // input.data = modifyDataYearToDate(datum.estimates, parseDate);
      // input.model = datum.model;
      // console.log('input before', input.data);
      // drawLineForEstimatesData(input);
    })

    svg.append('g')
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);
    svg.append('g')
      .attr("class", "y axis")
      .call(yAxis);


    let parameters = { svg, parseDate, bisectDate, formatDate, margin, x, y, xAxis, yAxis, width, height, prrline };
    // data.forEach((datum) => {
    //   let input = Object.assign({}, parameters);
    //   input.data = modifyDataYearToDate(datum.estimates, parseDate);
    //   input.model = datum.model;
    //   console.log('input before', input.data);
    //   drawLineForEstimatesData(input);
    // })
    
    d3.select("#viz_container") // graph number 1
      .append("div")
      .attr("id", 'c3-graph')
    drawNreportsAndControlGraph(data2, parseDate);
  }
  appendTextsToCanvas(svg, width, margin, title);
  // appendTextsToCanvas(svg2, width, margin, title2);
  // console.log('ending', data, data2, data.length > 0 ? typeof(data[0].year) : null)
};

const yearAxis = [
  {value: 2004},
  {value: 2005},
  {value: 2006},
  {value: 2007},
  {value: 2008},
  {value: 2009},
  {value: 2010},
  {value: 2011},
  {value: 2012},
  {value: 2013},
  {value: 2014},
  {value: 2015},
  {value: 2016},
];

const trimAxis = function (selector) {
  let axis = document.querySelectorAll(selector);
  axis.forEach((tick, i) => {
    if (i % 2) {
      tick.remove();
    }
  });
}

const setUpFocus = function (height, width) {
  var svg = d3.select(`#c3-graph svg`);
  var focus = svg.append("g").style("display", "none"); //  focus area when mouse moves

  focus.append("line")
    .attr("class", "x")
    .style("stroke", "black")
    .style("stroke-dasharray", "3,3")
    .style("opacity", 0.5)
    .attr("y1", 0)
    .attr("y2", height);

  focus.append("line")
    .attr("class", "y")
    .style("stroke", "black")
    .style("stroke-dasharray", "3,3")
    .style("opacity", 0.5)
    .attr("x1", width)
    .attr("x2", width);

  focus.append("circle")
    .attr("class", "y")
    .style("fill", "none")
    .style("stroke", "steelblue")
    .style("stroke-width", 1.5)
    .attr("r", 4);

  focus.append("text")
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

  focus.append("text")
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
}

const drawNreportsAndControlGraph = function (data2, parseDate) {
  data2 = modifyData2YearToDate(data2, parseDate);
  let nreports = [], years = [];
  data2.forEach(datum => {
    nreports.push(datum.nreports);
    years.push(datum.year.getFullYear());
  });
  c3.generate({
    bindto: `#c3-graph`,
    padding: {
      top: 20
    },
    title: {
      text: 'Number of Reports and Proportion of Total Patients'
    },
    data: {
      x: 'year',
      // xFormat: '%Y',
      columns: [
        ['year', ...years],
        ['nreports', ...nreports],
        ['control', 0.3, 0.4, 0.2, 0.4, 0.15, 0.25, 0.50, 0.20, 0.10, 0.40, 0.15, 0.25, 0.50]
      ],
      axes: {
        nreports: 'y',
        control: 'y2'
      }
    },
    axis: {
      x: {
        type: 'indexed',
        label: {
          text: 'Year',
          position: 'outer-right'
        },
        tick: {
          // format: (x) => x,
          values: [...years],
          outer: false  //removes superfluous axis overflow
        },
        padding: {
          left: 0,  //remove padding on graphs left and right side
          right: 0
        }
      },
      y: {
        show: true,
        label: {
          text: 'nreports',
          position: 'outer-middle'
        },
        tick: {
          outer: false
        },
        padding: {
          top: 0,
          bottom: 0
        }
      },
      y2: {
        min: 0,
        max: 1,
        show: true,
        label: {
          text: 'control',
          position: 'outer-middle'
        },
        tick: {
          outer: false
        },
        padding: {
          top: 0,
          bottom: 0
        }
      }
    },
    grid: {
      x: {
        show: true
      },
      y: {
        show: true
      },
      focus: {
        show: true
      }
    },
    legend: {
      position: 'bottom'
    }
  });
  // chart.focus();
  trimAxis(`#c3-graph g.c3-axis.c3-axis-y g`);
  trimAxis(`#c3-graph g.c3-axis.c3-axis-y2 g`);
  // setUpFocus();
}

const showLoading = () => {
  let viz_container = document.getElementById("viz_container");
  let loading = document.createElement('img');
  loading.src = '../../dist/gifs/loading.gif';
  loading.className = 'main-graph-loading';
  viz_container.innerHTML = "";
  viz_container.append(loading);
}
const all = {
  drawTimeSeriesGraph,
  showLoading
};

export default all;
export { 
  drawTimeSeriesGraph,
  showLoading
};